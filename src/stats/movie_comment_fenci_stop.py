'''
    对电影评论数据进行预处理和评论词的分词
'''
import jieba
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType, IntegerType, ArrayType, MapType, FloatType
from pyspark.sql import functions as F
import re
from jieba import analyse
import jieba.posseg as pseg
from pyspark.storagelevel import StorageLevel

import os
os.environ['HADOOP_CONF_DIR'] = "/opt/module/hadoop-3.1.3"

# 取出本地的停用词列表
def read_stopwords():
    with open("/opt/module/data/stopwords-master/cn_stopwords.txt", 'r', encoding='utf-8') as f:
        stopwords = ",".join(f.read().splitlines())
        print(stopwords)
        return stopwords  # 返回停用词列表

# 对评论内容进行分词，过滤掉停用词
def context_jieba_udf(context, stopword):
    r2 = '[^\u4e00-\u9fa5]'
    cont = re.sub(r2, '', context)
    allow = ['ns', 'n', 'vn', 'a', 'nw', 'nt', 'nz']
    seg = jieba.lcut(cont)
    stops = list(stopword.split(','))
    word_list = list()
    for word in seg:
        if word not in stops:
            word_list.append(word)
    words = ','.join(word_list)
    return words

# 对评论内容进行分词，过滤掉停用词并筛选词性
def context_pesg_udf(context, stopword):
    # r2 = '[^\u4e00-\u9fa5]'
    # cont = re.sub(r2, '', context)
    allow = ['ns', 'n', 'vn', 'a', 'nw', 'nt', 'nz']
    seg = pseg.cut(context, HMM=False)
    word_list = list()
    stops = list(stopword.split(','))
    for word, flag in seg:
        if flag in allow and word not in stops:
            word_list.append(word)
    words = ','.join(word_list)
    return words

# 对评论内容进行textRank提取关键词
def context_textrank_udf(context):
    r2 = '[^\u4e00-\u9fa5]'
    cont = re.sub(r2, '', context)
    allow = ['ns', 'n', 'vn', 'a', 'nw', 'nt', 'nz']
    word_list = analyse.textrank(context, topK=50, allowPOS=allow)
    words = ','.join(word_list)
    return words

# 对评论内容进行清洗和关键字提取
def context_tf_idf(context):
    r2 = '[^\u4e00-\u9fa5]'
    cont = re.sub(r2, '', context)
    allow = ['ns', 'n', 'vn', 'a', 'nw', 'nt', 'nz']
    word_list = analyse.tfidf(cont, topK=50, allowPOS= allow)
    words = ','.join(word_list)
    return words

# 对电影的原始评论信息进行分词处理，并且将每一步电影所有的分词结果合并，存放在hdfs中
if __name__ == '__main__':
    spark = SparkSession.builder. \
        appName("test"). \
        master("yarn"). \
        config("spark.sql.shuffle.partitions", 3). \
        getOrCreate()

    # 将停用词从本地取出
    stop_words = read_stopwords()

    # 读取电影评论数据集
    comment_schema = StructType().add("comment_id", StringType(), nullable=True). \
        add("comment_date", IntegerType(), nullable=True). \
        add("comment_context", StringType(), nullable=True). \
        add("movie_id", IntegerType(), nullable=True). \
        add("user_id", IntegerType(), nullable=True). \
        add("user_name", StringType(), nullable=True). \
        add("user_rate", FloatType(), nullable=True). \
        add("like_num", IntegerType(), nullable=True).\
        add("emo_tag", StringType(), nullable=True).\
        add("emo_rate", FloatType(), nullable=True)

    df_comment = spark.read.format("csv"). \
        option("sep", "%"). \
        option("header", True). \
        option("encoding", "utf-8"). \
        schema(schema=comment_schema). \
        load("/comments/predict.csv")



    # 对评论进行预筛选
    df_filter = df_comment.filter(df_comment.comment_context != 'null')
    df_filter.persist(StorageLevel.DISK_ONLY)

    df_stop = df_filter.withColumn('stops', F.lit(stop_words))
    df_stop.persist(StorageLevel.DISK_ONLY)


    # 返回每部电影评论分词后的数据(jieba分词)
    udf_comment_jieba = spark.udf.register("udf_comment_jieba", context_jieba_udf, StringType())
    df_comment_jieba = df_stop.select(df_stop.comment_id, df_stop.comment_date,
                                          udf_comment_jieba(df_stop.comment_context, df_stop.stops). \
                                          alias('comment_words'),
                                          df_stop.movie_id, df_stop.user_id, df_stop.user_name,
                                          df_stop.user_rate, df_stop.like_num, df_stop.emo_tag, df_stop.emo_rate)
    # 分词后进行一个过滤
    df_comment_words1 = df_comment_jieba.filter(df_comment_jieba.comment_words != '')
    df_comment_words1.show()

    # 将未筛选词性分词后的结果保存到hdfs的 csv文件中
    df_comment_words1.write.mode("overwrite"). \
        format("csv"). \
        option("seq", "\t"). \
        option("header", True). \
        save("/comments/predict_words_jieba.csv")

    # 返回每部电影评论分词后的数据(pesg分词)
    udf_comment_pesg = spark.udf.register("udf_comment_pesg", context_pesg_udf, StringType())
    df_comment_pesg = df_stop.select(df_stop.comment_id, df_stop.comment_date,
                                      udf_comment_pesg(df_stop.comment_context, df_stop.stops). \
                                      alias('comment_words'),
                                      df_stop.movie_id, df_stop.user_id, df_stop.user_name,
                                      df_stop.user_rate, df_stop.like_num, df_stop.emo_tag, df_stop.emo_rate)
    # 分词后进行一个过滤
    df_comment_words2 = df_comment_pesg.filter(df_comment_pesg.comment_words != '')
    df_comment_words2.show()

    # 将筛选词性后的结果保存到hdfs的 csv文件中
    df_comment_words2.write.mode("overwrite"). \
        format("csv"). \
        option("seq", "\t"). \
        option("header", True). \
        save("/comments/predict_words_pesg.csv")

    # 返回每部电影评论分词后的数据(textrank分词)
    udf_comment_textrank = spark.udf.register("udf_comment_textrank", context_textrank_udf, StringType())
    df_comment_textrank = df_filter.select(df_filter.comment_id, df_filter.comment_date,
                                     udf_comment_textrank(df_filter.comment_context). \
                                     alias('comment_words'),
                                     df_filter.movie_id, df_filter.user_id, df_filter.user_name,
                                     df_filter.user_rate, df_filter.like_num, df_stop.emo_tag, df_stop.emo_rate)
    # 分词后进行一个过滤
    df_comment_words3 = df_comment_textrank.filter(df_comment_textrank.comment_words != '')
    df_comment_words3.show()
    print("提取关键字后评论数:",df_comment_words3.count())

    # 将提取关键字后的结果保存到hdfs的 csv文件中
    df_comment_words3.write.mode("overwrite"). \
        format("csv"). \
        option("seq", "\t"). \
        option("header", True). \
        save("/comments/predict_words_textrank.csv")

    # 返回每部电影评论分词后的数据(df_idf关键字提取)
    udf_comment_df_idf = spark.udf.register("udf_comment_df_idf", context_tf_idf, StringType())
    df_comment_df_idf = df_filter.select(df_filter.comment_id, df_filter.comment_date,
                                           udf_comment_df_idf(df_filter.comment_context). \
                                           alias('comment_words'),
                                           df_filter.movie_id, df_filter.user_id, df_filter.user_name,
                                           df_filter.user_rate, df_filter.like_num, df_stop.emo_tag, df_stop.emo_rate)
    # 分词、提取后进行一个过滤
    df_comment_words3 = df_comment_df_idf.filter(df_comment_df_idf.comment_words != '')
    df_comment_words3.show()
    print("提取关键字后评论数:", df_comment_words3.count())

    # 将提取关键字后的结果保存到hdfs的 csv文件中
    df_comment_words3.write.mode("overwrite"). \
        format("csv"). \
        option("seq", "\t"). \
        option("header", True). \
        save("/comments/predict_words_tf_idf.csv")



