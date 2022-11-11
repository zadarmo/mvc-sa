import re
import jieba
from gensim.models import KeyedVectors
from keras.utils import pad_sequences
from preprocess.data_processer import DataProcesser
from preprocess.data_predict import DataPredict
from tensorflow.python.keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard, ReduceLROnPlateau
from modules.rnn import TextRNN
from preprocess.jieba_tokenizer import jieba_preprocess
from tqdm import tqdm
import numpy as np
import os
import pandas as pd


class Config:
    def __init__(self):
        self.maxlen = 380
        self.batch_size = 100
        self.epochs = 10
        self.num_words = 3800
        # 权重存储点
        self.path_checkpoint = '../models/sentiment_checkpoint_rnn.keras'


if __name__ == '__main__':
    # 使用gensim加载预训练中文分词embedding
    cn_model = KeyedVectors.load_word2vec_format("E:\__easyHelper__\sgns.zhihu.bigram\sgns.zhihu.bigram", binary=False)

    # 数据加载
    print('-----------Loading data---------------')
    movie_data = DataProcesser(xlsx_name='comments_38w.xlsx')
    clean_texts, clean_labels = movie_data.data_clean('process')
    # 保存checkpoint
    checkpoint = ModelCheckpoint(filepath=Config().path_checkpoint, monitor='val_loss',
                                 verbose=1, save_weights_only=True, save_best_only=True)

    print('-------------tokenizer----------------')
    train_tokens, embedding_matrix, max_tokens, embedding_dim, X_train, X_test, y_train, y_test = jieba_preprocess(
        train_texts=clean_texts, train_labels=clean_labels)

    # 转numpy
    y_train = np.array(y_train)
    y_test = np.array(y_test)

    test_model = TextRNN(num_words=50000,
                    embedding_matrix=embedding_matrix, max_tokens=max_tokens, embedding_dim=embedding_dim)
    model = test_model.get_model()

    # 加载模型
    if os.path.exists(Config().path_checkpoint):
        model.load_weights(Config().path_checkpoint)
    else:
        # earlystop
        earlystopping = EarlyStopping(monitor='val_loss', patience=3, verbose=1)
        # 自动降低learning rate
        lr_reduction = ReduceLROnPlateau(monitor='val_loss', factor=0.1,
                                         min_lr=1e-5, patience=0, verbose=1)

        # callback
        callbacks = [earlystopping, checkpoint, lr_reduction]

        print('-------------training start----------------')


        # 训练
        model.fit(X_train, y_train, validation_split=0.1, epochs=10,
                  batch_size=128, callbacks=callbacks, verbose=1)

        print('-------------training stop----------------')
        # evaluate
        print('----------evaluate------------')
        result = model.evaluate(X_test, y_test)
        print(f'Accuracy:{0:.2%}'.format(result[1]))

    # 分类
    def predict_sentiment(text_list):
        tag_list = []
        coef_list = []
        # 去掉标点符号和表情
        for i in tqdm(range(len(text_list))):
            print(text_list[i])
            # 分词
            cut = jieba.cut(text_list[i])
            cut_list = [i for i in cut]
            # tokenize
            for i, word in enumerate(cut_list):
                try:
                    cut_list[i] = cn_model.key_to_index[word]
                except KeyError:
                    cut_list[i] = 0
            # padding
            tokens_pad = pad_sequences([cut_list], maxlen=max_tokens,
                                       padding='pre', truncating='pre')

            # 预测
            result = model.predict(x=tokens_pad)
            coef = result[0][0]
            if coef >= 0.5:
                tag = 'pos'
                # print('是一例正面评价:', 'output=%.2f' % coef)
            else:
                tag = 'neg'
                # print('是一例负面评价:', 'output=%.2f' % coef)
            tag_list.append(tag)
            coef_list.append(coef)
        return tag_list, coef_list

    # 预测
    predict_data = DataPredict(xlsx_name='comments_5w.xlsx')
    predict_texts = predict_data.data_predict_clean('predict')

    # 保存预测结果
    print("-------sentiment---------")
    tag_list, coef_list = predict_sentiment(predict_texts)

    xlsx_path = '../data/predict/predict.xlsx'
    xlsx_file = pd.read_excel(xlsx_path)

    xlsx_file['标签'] = tag_list
    xlsx_file['情感分数'] = coef_list
    xlsx_file.to_excel(xlsx_path, index=False)


