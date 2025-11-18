import torch.nn as nn
from abc import ABC, abstractmethod

class BaseModelWrapper(nn.Module, ABC):
    def __init__(self, seq_dim: int, static_dim: int, horizon: int):
        super().__init__()
        self.seq_dim = seq_dim
        self.static_dim = static_dim
        self.horizon = horizon

    @abstractmethod
    def forward(self, x_seq, x_static):
        ...
