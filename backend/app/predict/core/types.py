from typing import TypedDict, List, Any

class BuildOutput(TypedDict):
    X_seq: Any   # np.ndarray [N, L, Fs]
    X_static: Any # np.ndarray [N, Fs2]
    y: Any       # np.ndarray [N, H]
    ids: List[str]
    dates: List[Any]
