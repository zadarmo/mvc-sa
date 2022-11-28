from keras.layers import Embedding, Dense, Dropout, LSTM, SimpleRNN, Bidirectional
from keras import Model, Input, Sequential
from keras.optimizers import Adam
import numpy as np
from preprocess.jieba_tokenizer import jiebaConfig


<<<<<<<< HEAD:dl/modules/lstm.py
class TextLSTM(object):
    def __init__(self, maxlen, num_words, class_num=1, first_activation='relu', last_activation='sigmoid'):
        self.maxlen = maxlen
        self.num_words = num_words
        self.class_num = class_num
        self.last_activation = last_activation
        self.first_activation = first_activation
========
class TextRNN(object):
    def __init__(self, num_words, embedding_matrix, max_tokens, activation='sigmoid'):
        # self.maxlen = maxlen
        self.num_words = num_words
        self.last_activation = activation
        self.embedding_matrix = embedding_matrix
        self.max_tokens = max_tokens
>>>>>>>> 1d78d9c (fix):modules/rnn.py

    def get_model(self):
        model = Sequential()

        #Embedding
        model.add(Embedding(jiebaConfig().num_words,
                            jiebaConfig().embedding_dim,
                            weights=[self.embedding_matrix],
                            input_length=self.max_tokens,
                            trainable=False))

        #LSTM
        model.add(Bidirectional(LSTM(units=32, return_sequences=True)))
        model.add(LSTM(units=16, return_sequences=False))

        # Dense
        model.add(Dense(1, activation=self.activation))
        # optimizer
        optimizer = Adam(lr=1e-3)
        model.compile(loss='binary_crossentropy',
                      optimizer=optimizer,
                      metrics=['accuracy'])
        model.summary()

        r"""
        input = Input((self.maxlen,))

        # embedding
        embedding = Embedding(self.num_words, 32, input_length=self.maxlen)(input)
        # dropout
        x = Dropout(0.2)(embedding)
        # LSTM
        x = LSTM(32)(x)  # LSTM or GRU
        # dense
        x = Dense(units=256, activation=self.first_activation)(x)
        # dropout
        x = Dropout(0.2)(x)
        # dense
        output = Dense(units=self.class_num, activation=self.last_activation)(x)

        model = Model(inputs=input, outputs=output)
<<<<<<<< HEAD:dl/modules/lstm.py
========
        """
>>>>>>>> 1d78d9c (fix):modules/rnn.py

        return model


