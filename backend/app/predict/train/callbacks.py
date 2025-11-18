class EarlyStopping:
    def __init__(self, patience=5):
        self.patience = patience
        self.bad = 0
    def step(self):
        self.bad += 1
        return self.bad >= self.patience
    def reset(self):
        self.bad = 0
