import torch, numpy as np
from app.predict.io.save_load import load_bundle, build_model_from_meta

class Predictor:
    def __init__(self, device: str | None=None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.model = None
        self.meta = None

    def load(self, path: str):
        bundle = load_bundle(path)
        self.meta = bundle["meta"]
        self.model = build_model_from_meta(self.meta)
        self.model.load_state_dict(bundle["state_dict"])
        self.model.to(self.device).eval()

    def forecast(self, x_seq: np.ndarray, x_static: np.ndarray):
        assert self.model is not None, "model not loaded"
        with torch.no_grad():
            xs = torch.tensor(x_seq, dtype=torch.float32, device=self.device).unsqueeze(0)
            xt = torch.tensor(x_static, dtype=torch.float32, device=self.device).unsqueeze(0)
            yhat = self.model(xs, xt)[0].cpu().numpy().tolist()
        return yhat
