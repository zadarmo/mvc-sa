from preprocess.data_processer import DataProcesser
from keras.callbacks import EarlyStopping
from keras.utils import pad_sequences
from keras.preprocessing.text import Tokenizer
import numpy as np
from keras.layers import Embedding
from keras.layers import Dense,Dropout
from keras.models import Sequential
from keras.layers import SimpleRNN

class Config:
    def __init__(self):
        self.maxlen = 380
        self.batch_size = 100
        self.epochs = 10
        self.num_words = 3800

# 数据加载
print('-----------Loading data---------------')

movie_data = DataProcesser(csv_name='DMSC.csv')
train_labels, train_texts, test_labels, test_texts = movie_data.data_clean('process')

print(len(train_texts), 'train sequences')
print(len(test_texts), 'test sequences')

print('-----------Padding sequences---------------')

token = Tokenizer(num_words=Config().num_words)
token.fit_on_texts(train_texts)

texts_train_seq = token.texts_to_sequences(train_texts)
texts_test_seq = token.texts_to_sequences(test_texts)

train_texts = pad_sequences(texts_train_seq, maxlen=Config().maxlen)
test_texts = pad_sequences(texts_test_seq, maxlen=Config().maxlen)

print("train_texts shape", train_texts.shape)
print("test_texts shape", test_texts.shape)

print('-----------Building model---------------')


model = Sequential()

model.add(Embedding(output_dim=32,
                    input_dim=3800,
                   input_length=380))
model.add(Dropout(0.35))
model.add(SimpleRNN(units=1))         #RNN模型
model.add(Dense(units=256,
               activation='relu'))
model.add(Dropout(0.35))
model.add(Dense(units=1,
               activation='sigmoid'))

model.build(input_shape=(380,3800))
model.summary()
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])



print('-----------Training---------------')

train_labels = np.array(train_labels)
test_labels = np.array(test_labels)

early_stopping = EarlyStopping(monitor='val_acc', patience=3, mode='max')

print("text shape:", train_texts.shape)
print("label shape:", train_labels.shape)

model.summary()

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

model.fit(train_texts, train_labels, batch_size=Config().batch_size,
          epochs=Config().epochs, callbacks=[early_stopping],
          verbose=1, validation_split=0.2)

print('-----------Testing---------------')


result = model.predict(test_texts)

# 保存
model.save('rnn.h5')
del model

print('-----------Save model completed---------------')

