import torch
from typing import Dict, Any
from app.predict.models.lstm import GlobalLSTM  # 默认注册的实现

def save_bundle(path: str, state: Dict[str, Any]):
    torch.save(state, path)

def load_bundle(path: str) -> Dict[str, Any]:
    return torch.load(path, map_location="cpu")

def build_model_from_meta(meta: Dict[str, Any]):
    algo = meta.get("algo", "lstm")
    if algo == "lstm":
        return GlobalLSTM(seq_dim=meta["seq_dim"], static_dim=meta["static_dim"],
                          horizon=meta["horizon"], hidden=meta.get("hidden",128),
                          layers=meta.get("layers",2), dropout=meta.get("dropout",0.2))
    raise ValueError(f"unknown algo: {algo}")
