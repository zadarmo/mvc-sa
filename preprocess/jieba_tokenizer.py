import os
import numpy as np
import matplotlib.pyplot as plt
from keras.utils import pad_sequences
import re
import jieba
from gensim.models import KeyedVectors

# 使用gensim加载预训练中文分词embedding
cn_model = KeyedVectors.load_word2vec_format("E:\__easyHelper__\sgns.zhihu.bigram\sgns.zhihu.bigram", binary=False)
embedding_dim = cn_model['大学'].shape[0]


class jiebaConfig:
    def __int__(self):
        self.embedding_matrix = []
        self.num_words = 50000
        self.embedding_dim = embedding_dim
        self.x = 111


def jieba_preprocess(train_texts):
    train_tokens = []
    filter_texts = []
    for text in train_texts:
        # 去掉标点符号和表情
        text = re.sub(r"[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+|[^\u4e00-\u9fa5]+", "", text)
        filter_texts.append(text)
    # 去掉空评论
    clean_train_texts = list(filter(None, filter_texts))
    for text in clean_train_texts:
        # 分词
        cut = jieba.cut(text)
        # 分词结果为一个生成器
        # 生成器转为list
        cut_list = [i for i in cut]
        for i, word in enumerate(cut_list):
            try:
                # 将词转为索引
                cut_list[i] = cn_model.key_to_index[i]
            except KeyError:
                # 如果词不再词典中，则输出0
                cut_list[i] = 0
        train_tokens.append(cut_list)
    print("train tokens type:", type(train_tokens))
    # 获得tokens长度
    num_tokens = [len(tokens) for tokens in train_tokens]
    num_tokens = np.array(num_tokens)
    # 平均token长度
    np.mean(num_tokens)
    # 最长评价token的长度
    np.max(num_tokens)

    r"""
    # plt画图
    plt.hist(np.log1p(num_tokens), bins=100)
    plt.xlim((0, 10))
    plt.ylabel('number of tokens')
    plt.xlabel('length of tokens')
    plt.title('Distribution of tokens length')
    plt.show()
    """

    # 模拟token最大长度
    # 取tokens平均值并加上两个tokens的标准差，
    # 假设tokens长度的分布为正态分布，则max_tokens这个值可以涵盖95%左右的样本
    max_tokens = np.mean(num_tokens) + 2 * np.std(num_tokens)
    max_tokens = int(max_tokens)

    # padding
    np.sum(num_tokens < max_tokens) / len(num_tokens)

    # 构造embedding
    embedding_matrix = np.zeros((jiebaConfig().num_words, embedding_dim))
    for i in range(jiebaConfig().num_words):
        embedding_matrix[i, :] = cn_model[cn_model.index_to_key[i]]
        embedding_matrix = embedding_matrix.astype('float32')

    np.sum(cn_model[cn_model.index_to_key[333]] == embedding_matrix[333])

    embedding_shape = embedding_matrix.shape

    # padding and truncating
    train_pad = pad_sequences(train_tokens, maxlen=max_tokens, padding='pre', truncating='pre')
    # 超出五万个词向量的词用0代替
    train_pad[train_pad >= jiebaConfig().num_words] = 0
    # target
    train_target = np.concatenate((np.ones(2000), np.zeros(2000)))

    return train_tokens, embedding_matrix, max_tokens


# 由token映射文本
def reverse_tokens(tokens):
    text1 = ''
    for i in tokens:
        if i != 0:
            text1 = text1 + cn_model.index_to_key[i]
        else:
            text1 = text1 + ' '
    return text1
