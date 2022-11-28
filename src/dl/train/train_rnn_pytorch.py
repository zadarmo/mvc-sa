import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import RandomSampler, DataLoader, TensorDataset, SequentialSampler
from keras.utils import pad_sequences
from preprocess.data_processer import DataProcesser
from keras.preprocessing.text import Tokenizer
from modules.rnn_pytorch import RNN_pytorch
from train.train_and_test import train, test


# 定义模型超参
class Config:
    def __init__(self):
        self.MAX_WORDS = 10000
        self.MAX_LEN = 200
        self.BATCH_SIZE = 256
        self.EMB_SIZE = 300
        self.HID_SIZE = 300
        self.DROPOUT = 0.2
        self.DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# 数据加载
print('-----------Loading data---------------')

movie_data = DataProcesser(xlsx_name='comments_38w.xlsx')
train_labels, train_texts, test_labels, test_texts = movie_data.data_clean('process')

rate = movie_data.rate
# 数据处理

token = Tokenizer(num_words=Config().MAX_WORDS)
token.fit_on_texts(train_texts)

texts_train_seq = token.texts_to_sequences(train_texts)
texts_test_seq = token.texts_to_sequences(test_texts)

train_texts = pad_sequences(texts_train_seq, maxlen=Config().MAX_LEN)
test_texts = pad_sequences(texts_test_seq, maxlen=Config().MAX_LEN)

# 将数据转为tensorDataset
train_data = TensorDataset(torch.LongTensor(train_texts), torch.LongTensor(train_labels))
test_data = TensorDataset(torch.LongTensor(test_texts), torch.LongTensor(test_labels))

# 将数据放入dataloader
train_sampler = RandomSampler(train_data)
train_loader = DataLoader(train_data, sampler=train_sampler, batch_size=Config().BATCH_SIZE)
test_sampler = SequentialSampler(test_data)
test_loader = DataLoader(test_data, sampler=test_sampler, batch_size=Config().BATCH_SIZE)

print("-----------导入模型-------------")
model = RNN_pytorch(Config().MAX_WORDS, Config().EMB_SIZE, Config().HID_SIZE,
                    Config().DROPOUT).to(Config().DEVICE)
print(model)

optimizer = optim.Adam(model.parameters())
best_acc = 0.0

print("-----------开始训练-------------")

for epoch in range(1, 11):
    try:
        train(model, Config().DEVICE, train_loader, optimizer, epoch)
    except Exception as e:
        print("exception:", e)
    acc = test(model, Config().DEVICE, test_loader)

    if best_acc < acc:
        best_acc = acc

    print("acc is:{:.4f},best acc is {:.4f}\n".format(acc, best_acc))

torch.save(model, f'../models/rnn_{rate}_pytorch.pt')