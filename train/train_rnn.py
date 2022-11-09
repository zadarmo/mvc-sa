import re
import jieba
from gensim.models import KeyedVectors
from keras.utils import pad_sequences
from preprocess.data_processer import DataProcesser
from tensorflow.python.keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard, ReduceLROnPlateau
from modules.rnn import TextRNN
from preprocess.jieba_tokenizer import jieba_preprocess
from preprocess.jieba_tokenizer import jiebaConfig

# 使用gensim加载预训练中文分词embedding
cn_model = KeyedVectors.load_word2vec_format("E:\__easyHelper__\sgns.zhihu.bigram\sgns.zhihu.bigram", binary=False)


class Config:
    def __init__(self):
        self.maxlen = 380
        self.batch_size = 100
        self.epochs = 10
        self.num_words = 3800
        # 权重存储点
        self.path_checkpoint = '../models/sentiment_checkpoint_rnn.keras'


# 数据加载
print('-----------Loading data---------------')
movie_data = DataProcesser(xlsx_name='comments_38w.xlsx')
train_labels, train_texts, test_labels, test_texts = movie_data.data_clean('process')
# 保存checkpoint
checkpoint = ModelCheckpoint(filepath=Config().path_checkpoint, monitor='val_loss',
                             verbose=1, save_weights_only=True, save_best_only=True)

print('-------------tokenizer----------------')
train_texts, embedding_matrix, max_tokens = jieba_preprocess(train_texts=train_texts)
test_texts, _, _ = jieba_preprocess(test_texts)

model = TextRNN(num_words=jiebaConfig().num_words,
                embedding_matrix=embedding_matrix, max_tokens=max_tokens)

# 加载模型
try:
    model.load_weights(Config().path_checkpoint)
except Exception as e:
    print(e)
    # earlystop
    earlystopping = EarlyStopping(monitor='val_loss', patience=3, verbose=1)
    # 自动降低learning rate
    lr_reduction = ReduceLROnPlateau(monitor='val_loss', factor=0.1,
                                     min_lr=1e-5, patience=0, verbose=1)

    # callback
    callbacks = [earlystopping, checkpoint, lr_reduction]

    print('-------------training start----------------')

    # 训练
    model.fit(train_texts, train_labels, validation_split=0.1, epochs=10,
              batch_size=128, callbacks=callbacks)

    print('-------------training stop----------------')
# evaluate
result = model.evaluate(test_texts, test_labels)
print(f'Accuracy:{0:.2%}'.format(result[1]))

# 分类
def predict_sentiment(text):
    print(text)
    # 去掉标点符号和表情
    text = re.sub(r"[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+|[^\u4e00-\u9fa5]+", "", text)
    # 分词
    cut = jieba.cut(text)
    cut_list = [i for i in cut]
    # tokenize
    for i, word in enumerate(cut_list):
        try:
            cut_list[i] = cn_model.vocab[word].index
        except KeyError:
            cut_list[i] = 0
    # padding
    tokens_pad = pad_sequences([cut_list], maxlen=max_tokens,
                               padding='pre', truncating='pre')

    # 预测
    result = model.predict(x=tokens_pad)
    coef = result[0][0]
    if coef >= 0.5:
        print('pos:', 'output=%.2f' % coef)
    else:
        print('neg:', 'output=%.2f' % coef)

label_pred = model.predict(test_texts)

for i, label in enumerate(label_pred):
    print("i:{0}, label:{1}".format(i, label))
