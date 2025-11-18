import os, sys, argparse, asyncio, numpy as np, torch
from torch.utils.data import TensorDataset, DataLoader
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.db.base import DATABASE_URL
from app.predict.data.features import SeqFeatureConfig, StaticFeatureConfig
from app.predict.data.builders import build_global_samples
from app.predict.models.lstm import GlobalLSTM
from app.predict.train.trainer import Trainer
from app.predict.io.paths import global_model_path
from app.predict.io.save_load import save_bundle

def to_tensors(x_seq, x_static, y):
    Xs = torch.tensor(x_seq, dtype=torch.float32)
    Xt = torch.tensor(x_static, dtype=torch.float32)
    Y  = torch.tensor(y, dtype=torch.float32)
    return Xs, Xt, Y

async def _amain(args):
    engine = create_async_engine(DATABASE_URL, future=True)
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    try:
        async with Session() as session:
            out = await build_global_samples(
                session,
                country=args.country, device=args.device, brand=args.brand,
                days=args.days, lookback=args.lookback, horizon=args.horizon,
                seq_cfg=SeqFeatureConfig(), static_cfg=StaticFeatureConfig(keyword_hash_dim=args.hash_dim)
            )
        Xs, Xt, Y = to_tensors(out["X_seq"], out["X_static"], out["y"])
        if len(Xs)==0:
            raise RuntimeError("no samples built")

        # 时间切分 80/20（保持时间序）
        dates_ord = np.argsort(np.array([int(d.strftime('%Y%m%d')) for d in out["dates"]]))
        Xs, Xt, Y = Xs[dates_ord], Xt[dates_ord], Y[dates_ord]
        n = len(Xs); n_tr = max(1, int(n*0.8))
        Xs_tr, Xs_val = Xs[:n_tr], Xs[n_tr:]; Xt_tr, Xt_val = Xt[:n_tr], Xt[n_tr:]; Y_tr, Y_val = Y[:n_tr], Y[n_tr:]

        dl_tr = DataLoader(TensorDataset(Xs_tr, Xt_tr, Y_tr), batch_size=args.batch, shuffle=True)
        dl_val = DataLoader(TensorDataset(Xs_val, Xt_val, Y_val), batch_size=args.batch, shuffle=False)

        model = GlobalLSTM(seq_dim=Xs.shape[-1], static_dim=Xt.shape[-1],
                           horizon=args.horizon, hidden=args.hidden, layers=args.layers, dropout=args.dropout)
        trainer = Trainer(model, lr=args.lr, wd=args.wd)
        best = trainer.fit(dl_tr, dl_val, epochs=args.epochs, device=("cuda" if torch.cuda.is_available() else "cpu"))

        save_path = global_model_path(args.country, args.device, args.brand, "lstm")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        meta = {"algo":"lstm","seq_dim":Xs.shape[-1],"static_dim":Xt.shape[-1],"horizon":args.horizon,
                "lookback":args.lookback,"hidden":args.hidden,"layers":args.layers,"dropout":args.dropout}
        torch.save({"state_dict": best[1], "meta": meta}, save_path)
        print("saved:", save_path)
    finally:
        await engine.dispose()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--country", required=True)
    p.add_argument("--device", required=True)
    p.add_argument("--brand", required=True, choices=["free","paid","grossing"])
    p.add_argument("--days", type=int, default=420)
    p.add_argument("--lookback", type=int, default=30)
    p.add_argument("--horizon", type=int, default=7)
    p.add_argument("--epochs", type=int, default=40)
    p.add_argument("--batch", type=int, default=256)
    p.add_argument("--hidden", type=int, default=128)
    p.add_argument("--layers", type=int, default=2)
    p.add_argument("--dropout", type=float, default=0.2)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--wd", type=float, default=1e-4)
    p.add_argument("--hash_dim", type=int, default=512)
    args = p.parse_args()
    asyncio.run(_amain(args))

if __name__ == "__main__":
    main()
