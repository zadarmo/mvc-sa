from keras.layers import Embedding, Dense, Dropout, LSTM, SimpleRNN, GlobalAveragePooling1D
from keras import Model, Input


class TextMLP(object):
    def __init__(self, maxlen, num_words, class_num=1, last_activation='sigmoid'):
        self.maxlen = maxlen
        self.num_words = num_words
        self.class_num = class_num
        self.last_activation = last_activation

    def get_model(self):

        input = Input((self.maxlen,))
        embedding = Embedding(self.num_words, 32, input_length=self.maxlen)(input)
        x = GlobalAveragePooling1D()(embedding)
        output = Dense(self.class_num, activation=self.last_activation)(x)
        model = Model(inputs=input, outputs=output)

        return model