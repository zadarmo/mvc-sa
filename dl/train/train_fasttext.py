from preprocess.data_processer import DataProcesser
from keras.utils import pad_sequences
from keras.preprocessing.text import Tokenizer
import numpy as np
from modules.fasttext import TextMLP
from keras.callbacks import EarlyStopping


class Config:
    def __init__(self):
        self.maxlen = 400
        self.batch_size = 32
        self.epochs = 10
        self.num_words = 5000

# 数据加载
print('-----------Loading data---------------')

movie_data = DataProcesser(xlsx_name='comments_38w.xlsx')
train_labels, train_texts, test_labels, test_texts = movie_data.data_clean('process')
rate = movie_data.rate

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


init_model = TextMLP(Config().maxlen, Config().num_words)
model = init_model.get_model()

print('-----------Training---------------')

train_labels = np.array(train_labels)
test_labels = np.array(test_labels)

print("text shape:", train_texts.shape)
print("label shape:", train_labels.shape)

model.summary()

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])


early_stopping = EarlyStopping(monitor='val_accuracy', patience=3, mode='max')

model.fit(train_texts, train_labels, batch_size=Config().batch_size,
          epochs=Config().epochs, verbose=1, callbacks=[early_stopping],
          validation_data=(test_texts, test_labels))

print('-----------Testing---------------')

scores = model.evaluate(test_texts, test_labels, verbose=1)
print("score:", scores[1])

result = model.predict(test_texts)

print("result:", result)
# 保存
model.save(f'../models/fasttext_{rate}.h5')
del model

print('-----------Save model completed---------------')

