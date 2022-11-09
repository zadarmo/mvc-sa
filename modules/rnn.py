from keras.layers import Embedding, Dense, Dropout, LSTM, SimpleRNN, Bidirectional
from keras import Model, Input, Sequential
from keras.optimizers import Adam
import numpy as np
from preprocess.jieba_tokenizer import jiebaConfig


class TextRNN(object):
    def __init__(self, num_words, embedding_matrix, max_tokens, activation='sigmoid'):
        # self.maxlen = maxlen
        self.num_words = num_words
        self.last_activation = activation
        self.embedding_matrix = embedding_matrix
        self.max_tokens = max_tokens

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

        embedding = Embedding(self.num_words, 32, input_length=self.maxlen)(input)
        x = LSTM(128)(embedding)  # LSTM or GRU

        output = Dense(self.class_num, activation=self.last_activation)(x)
        model = Model(inputs=input, outputs=output)
        """

        return model


