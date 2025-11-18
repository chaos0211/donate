import torch, torch.nn as nn
from .base import BaseModelWrapper

class GlobalLSTM(BaseModelWrapper):
    def __init__(self, seq_dim, static_dim, horizon, hidden=128, layers=2, dropout=0.2, attn=False):
        super().__init__(seq_dim, static_dim, horizon)
        self.lstm = nn.LSTM(seq_dim, hidden, num_layers=layers, batch_first=True,
                            dropout=dropout if layers>1 else 0.0)
        self.use_attn = attn
        if self.use_attn:
            self.attn = nn.MultiheadAttention(hidden, num_heads=8, batch_first=True, dropout=dropout)
        self.static_mlp = nn.Sequential(
            nn.Linear(static_dim, 256), nn.ReLU(), nn.Dropout(dropout),
            nn.Linear(256, 128), nn.ReLU()
        )
        self.head = nn.Sequential(
            nn.Linear(hidden + 128, 128), nn.ReLU(),
            nn.Linear(128, horizon)
        )

    def forward(self, x_seq, x_static):
        y, _ = self.lstm(x_seq)                # [B, L, H]
        if self.use_attn:
            y, _ = self.attn(y, y, y)         # [B, L, H]
        h = y[:, -1, :]
        s = self.static_mlp(x_static)
        out = self.head(torch.cat([h, s], dim=-1))  # [B, H]
        return out
