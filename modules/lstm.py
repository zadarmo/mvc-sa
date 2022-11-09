from keras.layers import Embedding, Dense, Dropout, LSTM, SimpleRNN
from keras import Model, Input


class TextLSTM(object):
    def __init__(self, maxlen, num_words, class_num=1, first_activation='relu', last_activation='sigmoid'):
        self.maxlen = maxlen
        self.num_words = num_words
        self.class_num = class_num
        self.last_activation = last_activation
        self.first_activation = first_activation

    def get_model(self):

        r"""


        model = Sequential()

        model.add(Embedding(output_dim=32,
                            input_dim=self.num_words,
                            input_length=self.maxlen))
        model.add(Dropout(0.35))
        model.add(SimpleRNN(units=1))  # RNN模型
        model.add(Dense(units=256,
                        activation='relu'))
        model.add(Dropout(0.35))
        model.add(Dense(units=1,
                        activation='sigmoid'))


        model.build((self.maxlen, 32))

        """
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

        return model

