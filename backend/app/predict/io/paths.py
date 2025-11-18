import os
MODEL_DIR = os.environ.get("PREDICT_MODEL_DIR", "app/predict/models/lstm")

def global_model_path(country: str, device: str, brand: str, algo: str="lstm") -> str:
    os.makedirs(MODEL_DIR, exist_ok=True)
    name = f"global_{country}_{device}_{brand}_{algo}.pt"
    return os.path.join(MODEL_DIR, name)
