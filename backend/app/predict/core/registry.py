from typing import Dict, Callable
REGISTRY: Dict[str, Callable[..., object]] = {}

def register(name: str):
    def deco(fn: Callable[..., object]):
        REGISTRY[name] = fn
        return fn
    return deco

def get(name: str) -> Callable[..., object]:
    if name not in REGISTRY:
        raise KeyError(f"algo not registered: {name}")
    return REGISTRY[name]
