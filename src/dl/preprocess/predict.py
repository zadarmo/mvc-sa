import numpy as np
from tensorflow.python.keras.models import load_model
from preprocess.data_processer import DataProcesser
from keras.preprocessing.text import Tokenizer
from train.train_rnn import Config

print('------------Loading xlsx------------')

movie_data = DataProcesser(xlsx_name='comments_38w.xlsx')
train_labels, train_texts, test_labels, test_texts = movie_data.data_clean('process')
rate = movie_data.rate

print('------------Processing data------------')
token = Tokenizer(num_words=Config().num_words)
token.fit_on_texts(train_texts)

print('------------Loading model------------')
model = load_model(f'../models/rnn_{rate}.h5')
print('------------Loading completed------------')


def predict_review(input_text):
    print("input_text:", input_text)
    out = []
    for text in input_text:
        print("text:", text)
        input_seq = token.texts_to_sequences([text])
        print("input_seq:", input_seq)
        # pad_input_seq_token = pad_sequences(input_seq, maxlen=Config().maxlen)
        # print("pad_input_seq_token:", pad_input_seq_token)
        predict_result = model.predict(input_seq, verbose=1)
        print("predict_result:", predict_result)
        max_result = np.argmax(predict_result, axis=1)
        print("max_result:", max_result)
        result = max_result.tolist()
        print("result:", result)

        out.append(result)

    return out

