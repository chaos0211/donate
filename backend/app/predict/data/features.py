import math, re, numpy as np
from dataclasses import dataclass
from datetime import datetime, date as date_cls

HASH_DIM_DEFAULT = 512
_WORD = re.compile(r"[A-Za-z0-9_]+")

def to_date(x):
    if isinstance(x, datetime): return x.date()
    if isinstance(x, date_cls): return x
    try: return datetime.fromisoformat(str(x)).date()
    except: return None

def dow_feats(d):
    w = d.weekday()
    return math.sin(2*math.pi*w/7.0), math.cos(2*math.pi*w/7.0)

def hash_bow(texts, dim: int):
    v = np.zeros(dim, dtype=np.float32)
    for t in texts or []:
        for tok in _WORD.findall(str(t or "").lower()):
            idx = (hash(tok) % dim + dim) % dim
            v[idx] += 1.0
    if v.sum() > 0:
        v = v / np.linalg.norm(v)
    return v

@dataclass
class SeqFeatureConfig:
    use_rank_norm: bool = True
    use_diff: bool = True
    use_ma7: bool = True
    use_dow: bool = True

@dataclass
class StaticFeatureConfig:
    use_price: bool = True
    use_is_ad: bool = True
    use_rating: bool = True
    use_rating_num_log: bool = True
    use_age: bool = True
    use_keyword_hash: bool = True
    keyword_hash_dim: int = HASH_DIM_DEFAULT
