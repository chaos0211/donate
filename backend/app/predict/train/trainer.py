import torch, torch.nn as nn
from .callbacks import EarlyStopping

class Trainer:
    def __init__(self, model, lr=1e-3, wd=1e-4):
        self.model = model
        self.opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
        self.crit = nn.L1Loss()
        self.sched = torch.optim.lr_scheduler.ReduceLROnPlateau(self.opt, mode='min', patience=3, factor=0.5)
        self.es = EarlyStopping(patience=5)

    def fit(self, dl_train, dl_val, epochs=40, device='cpu'):
        self.model.to(device)
        best = (1e9, None)
        for ep in range(1, epochs+1):
            # train
            self.model.train(); tr_loss=0.0
            for xs, xt, y in dl_train:
                xs, xt, y = xs.to(device), xt.to(device), y.to(device)
                self.opt.zero_grad()
                pred = self.model(xs, xt)
                loss = self.crit(pred, y)
                loss.backward()
                nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.opt.step()
                tr_loss += loss.item()*xs.size(0)
            tr_loss /= len(dl_train.dataset)

            # val
            self.model.eval(); va_loss=0.0
            with torch.no_grad():
                for xs, xt, y in dl_val:
                    xs, xt, y = xs.to(device), xt.to(device), y.to(device)
                    pred = self.model(xs, xt)
                    va_loss += self.crit(pred, y).item()*xs.size(0)
            va_loss /= len(dl_val.dataset)
            self.sched.step(va_loss)

            if va_loss < best[0]:
                best = (va_loss, {k:v.cpu() for k,v in self.model.state_dict().items()})
                self.es.reset()
            else:
                if self.es.step():
                    print("early stop.")
                    break
            print(f"epoch {ep}/{epochs} - train_mae: {tr_loss:.4f} - val_mae: {va_loss:.4f}")
        return best
