import torch.nn as nn
import torch.nn.functional as F


class RNN_pytorch(nn.Module):
    def __init__(self, max_words, emb_size, hid_size, dropout):
        super(RNN_pytorch, self).__init__()
        self.max_words = max_words
        self.emb_size = emb_size
        self.hid_size = hid_size
        self.dropout = dropout
        self.Embedding = nn.Embedding(self.max_words, self.emb_size)
        self.fc2 = nn.Linear(self.hid_size, 2)
        self.RNN = nn.RNN(self.emb_size, self.hid_size, num_layers=1, batch_first=True)

    def forward(self, x):
        r"""
        定义前向计算
        """
        x = self.Embedding(x)
        x, _ = self.RNN(x)
        x = F.avg_pool2d(x, (x.shape[1], 1)).squeeze()
        out = self.fc2(x)

        return out
