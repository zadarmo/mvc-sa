from keras.layers import Embedding, Dense
from tensorflow.python.keras.layers import Dense,Dropout,Activation,Flatten
from tensorflow.python.keras.models import Sequential
from keras import Input, Model

class TextRNN(object):
    def __init__(self):
        pass

    def get_model(self):

        model = Sequential()

        model.add(Embedding(output_dim=32,
                            input_dim=2000,
                            input_length=100))
        model.add(Dropout(0.2))
        model.add(Flatten())
        model.add(Dense(units=256,
                        activation='relu'))
        model.add(Dropout(0.35))
        model.add(Dense(units=1,
                        activation='sigmoid'))

        model.build((100, ))

        return model