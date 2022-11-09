from tensorflow.python.keras.models import load_model
from preprocess.data_processer import DataProcesser
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences
import numpy as np

print('------------Loading xlsx------------')

movie_data = DataProcesser(csv_name='comments_38w.csv')
train_labels, train_texts, test_labels, test_texts = movie_data.data_clean('process', rate=0.7)
rate = movie_data.rate

print('------------Processing data------------')
token = Tokenizer(num_words=3800)
token.fit_on_texts(train_texts)

x_test_seq = token.texts_to_sequences(test_texts)
test_texts = pad_sequences(x_test_seq, maxlen=380)

test_labels = np.array(test_labels)
print('------------Loading model------------')
model = load_model(f'../models/rnn_{rate}.h5')
print('------------Loading completed------------')

print("type texts:", type(test_texts[0]))
print("type labels:", type(test_labels[0]))
scores = model.evaluate(test_texts, test_labels, verbose=1)

print("scores:", scores)
