'''
    对电影评论词进行统计分析以及词云生成
'''
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType, IntegerType, ArrayType, MapType, FloatType
from pyspark.sql import functions as F
from pyspark.storagelevel import StorageLevel
import os
import wordcloud

os.environ['HADOOP_CONF_DIR'] = "/opt/module/hadoop-3.1.3"

# 计算词频
def words_freq(words):
    words_list = words.split(',')
    count_dict = dict()
    for item in words_list:
        if item in count_dict:
            count_dict[item] += 1
        else:
            count_dict[item] = 1
    # 对评论词按照词频进行筛选
    return count_dict

# 生成词云
def plot_Wc(name, counts1):
    image_name = name.replace("/", "_")
    '''这是将词频字典生成词云的函数'''
    wc = wordcloud.WordCloud(             #根据词频字典生成词云图
            max_words=150,  # 最多显示词数
            max_font_size=300,  # 字体最大值
            background_color="white",  # 设置背景为白色，默认为黑色
            width=1500,  # 设置图片的宽度
            height=960,  # 设置图片的高度
            margin=10,  # 设置图片的边缘
            font_path='../Fonts/simsun.ttc'
        )
    wc.generate_from_frequencies(counts1)  # 从字典生成词云
    wc.to_file('../images/{}_wordcloud.png'.format(image_name))


# 对电影评论分词后的结果进行分析
if __name__ == '__main__':
    spark = SparkSession.builder. \
        appName("test"). \
        master("yarn"). \
        config("spark.sql.shuffle.partitions", 6). \
        getOrCreate()

    # 读取电影评论数据集字段信息
    comment_schema = StructType().add("comment_id", StringType(), nullable=True). \
        add("comment_date", IntegerType(), nullable=True). \
        add("comment_word", StringType(), nullable=True). \
        add("movie_id", IntegerType(), nullable=True). \
        add("user_id", IntegerType(), nullable=True). \
        add("user_name", StringType(), nullable=True). \
        add("user_rate", FloatType(), nullable=True). \
        add("like_num", IntegerType(), nullable=True). \
        add("emo_tag", StringType(), nullable=True). \
        add("emo_rate", FloatType(), nullable=True)

    # 读取电影信息数据集字段信息
    movie_schema = StructType().add("movie_id", IntegerType(), nullable=True). \
        add("movie_url", StringType(), nullable=True). \
        add("movie_name", StringType(), nullable=True). \
        add("movie_nation", StringType(), nullable=True). \
        add("movie_type", StringType(), nullable=True). \
        add("movie_year", IntegerType(), nullable=True). \
        add("movie_month", IntegerType(), nullable=True). \
        add("movie_day", IntegerType(), nullable=True). \
        add("movie_length", IntegerType(), nullable=True). \
        add("movie_rate", FloatType(), nullable=True)

    df_comment = spark.read.format("csv"). \
        option("sep", ","). \
        option("header", True). \
        option("encoding", "utf-8"). \
        schema(schema=comment_schema). \
        load("/comments/predict_words_tf_idf.csv")

    # 读取电影信息
    df_movie = spark.read.format("csv"). \
        option("sep", ","). \
        option("header", True). \
        option("encoding", "utf-8"). \
        schema(schema=movie_schema). \
        load("/comments/movie_info.csv")

    # 将评论和电影的dataframe存入磁盘缓存
    df_comment.persist(StorageLevel.DISK_ONLY)
    df_movie.persist(StorageLevel.DISK_ONLY)

    df_comment.createTempView("comment")
    df_movie.createTempView("movie")

    udf_words_statis = spark.udf.register("udf_words_statis", words_freq, MapType(StringType(), IntegerType()))

    #========================== 找出好评率（差评率）前xxx的电影，分析好评（差评）中出现的高频词，做词云 ======================================
    # 计算每一部电影的评论数
    df_movie_comment_count = df_comment.\
        groupBy('movie_id'). \
        agg(F.count("comment_word")). \
        withColumnRenamed("count(comment_word)", "comment_count")

    # 计算每一部电影的好评数，并且整合好评词，总评论数和电影信息,并且选出评论数大于20的电影
    df_movie_pos_com = df_comment. \
        filter(df_comment.emo_tag == 'pos'). \
        groupBy('movie_id'). \
        agg(F.count("comment_word"), F.concat_ws(",", F.collect_list('comment_word'))). \
        withColumnRenamed("count(comment_word)", "pos_comment_count"). \
        withColumnRenamed("concat_ws(,, collect_list(comment_word))", "pos_comment_word"). \
        join(df_movie, 'movie_id', 'left'). \
        join(df_movie_comment_count, 'movie_id', 'left'). \
        filter('comment_count is not null and comment_count>20')

    # 计算每一部电影的差评数目,并且整合差评词，总评论数和电影信息
    df_movie_neg_com = df_comment. \
        filter(df_comment.emo_tag == 'neg'). \
        groupBy('movie_id'). \
        agg(F.count("comment_word"), F.concat_ws(",", F.collect_list('comment_word'))). \
        withColumnRenamed("count(comment_word)", "neg_comment_count"). \
        withColumnRenamed("concat_ws(,, collect_list(comment_word))", "neg_comment_word"). \
        join(df_movie, 'movie_id', 'left'). \
        join(df_movie_comment_count, 'movie_id', 'left')
    df_movie_neg_com = df_movie_neg_com.filter('comment_count is not null and comment_count>10')

    # 计算好评率和差评率,选出前100
    df_movie_pos_com_top = df_movie_pos_com.withColumn('pos_rate', df_movie_pos_com.pos_comment_count / df_movie_pos_com.comment_count). \
        orderBy(F.desc('pos_rate')).limit(100)
    df_movie_neg_com_top = df_movie_neg_com.withColumn('neg_rate', df_movie_neg_com.neg_comment_count / df_movie_neg_com.comment_count). \
        orderBy(F.desc('neg_rate')).limit(100)
    df_movie_pos_com_top.show()
    df_movie_neg_com_top.show()

    df_movie_neg_com_top.persist(StorageLevel.DISK_ONLY)
    df_movie_pos_com_top.persist(StorageLevel.DISK_ONLY)

    # ============好评率和差评率前100电影的不同类别的电影数==============
    df_movie_pos_top_type = df_movie_pos_com_top.groupBy("movie_type").\
        agg(F.count("movie_id")).\
        withColumnRenamed("count(movie_id)", "movie_count").\
        orderBy(F.desc('movie_count'))
    df_movie_pos_top_type.show()
    # # 导出为csv
    df_movie_pos_top_type.write.mode("overwrite"). \
        format("csv"). \
        option("seq", "\t"). \
        option("header", True). \
        save("/comments/result/好评率前100各类别电影数.csv")

    # pd.DataFrame(df_movie_pos_top_type.toPandas()).to_excel("../result/好评率前100各类别电影数.xlsx")

    df_movie_neg_top_type = df_movie_neg_com_top.groupBy("movie_type").\
        agg(F.count("movie_id")).\
        withColumnRenamed("count(movie_id)", "movie_count").\
        orderBy(F.desc('movie_count'))
    df_movie_neg_top_type.show()
    # 导出为csv
    df_movie_neg_top_type.write.mode("overwrite"). \
        format("csv"). \
        option("seq", "\t"). \
        option("header", True). \
        save("/comments/result/差评率前100各类别电影数.csv")

    # pd.DataFrame(df_movie_neg_top_type.toPandas()).to_excel("../result/差评率前100各类别电影数.xlsx")
    # ============================================================

    # =======================好评率差评率前100不同国家的电影数========================
    # 找出好评率和差评率前100电影的不同国家的电影数
    df_movie_pos_top_nation = df_movie_pos_com_top.groupBy("movie_nation"). \
        agg(F.count("movie_id")). \
        withColumnRenamed("count(movie_id)", "movie_count"). \
        orderBy(F.desc('movie_count'))
    df_movie_pos_top_nation.show()

    # 导出为csv
    df_movie_pos_top_nation.write.mode("overwrite"). \
        format("csv"). \
        option("seq", "\t"). \
        option("header", True). \
        save("/comments/result/好评率前100各国家电影数.csv")
    # pd.DataFrame(df_movie_pos_top_nation.toPandas()).to_excel("../result/好评率前100各国家电影数.xlsx")


    df_movie_neg_top_nation = df_movie_neg_com_top.groupBy("movie_nation"). \
        agg(F.count("movie_id")). \
        withColumnRenamed("count(movie_id)", "movie_count"). \
        orderBy(F.desc('movie_count'))
    df_movie_neg_top_nation.show()

    # # 导出为csv
    df_movie_neg_top_nation.write.mode("overwrite"). \
        format("csv"). \
        option("seq", "\t"). \
        option("header", True). \
        save("/comments/result/差评率前100各国家电影数.csv")
    # pd.DataFrame(df_movie_neg_top_nation.toPandas()).to_excel("../result/差评率前100各国家电影数.xlsx")

    # =======================================================================

    # ======================对评论词进行统计,生成好评率和差评率前100电影评论的词云===================

    # 整合差评率前100电影的评论词
    df_movie_neg_com_top_dict = df_movie_neg_com_top.\
        agg(F.concat_ws(",", F.collect_list('neg_comment_word'))). \
        withColumnRenamed("concat_ws(,, collect_list(neg_comment_word))", "neg_comment_word")
    # 统计差评率前100电影的评论词生成字典，转json字符串写入csv
    df_movie_neg_com_top_dict = df_movie_neg_com_top_dict.select(udf_words_statis(df_movie_neg_com_top_dict.neg_comment_word). \
        alias('neg_comment_word_dict')).\
        withColumn('neg_comment_word_json',F.to_json('neg_comment_word_dict')).\
        select('neg_comment_word_json')

    df_movie_neg_com_top_dict.show()
    # 导出为csv
    df_movie_neg_com_top_dict.write.mode("overwrite"). \
        format("csv"). \
        option("seq", "\t"). \
        option("header", True). \
        save("/comments/result/差评率前100电影的词频统计.csv")
    # pd.DataFrame(df_movie_neg_com_top_dict.toPandas()).to_excel("../result/差评率前100电影的词频统计.xlsx")


    df_movie_pos_com_top_dict = df_movie_pos_com_top.\
        agg(F.concat_ws(",", F.collect_list('pos_comment_word'))). \
        withColumnRenamed("concat_ws(,, collect_list(pos_comment_word))", "pos_comment_word")
    df_movie_pos_com_top_dict = df_movie_pos_com_top_dict.select(udf_words_statis(df_movie_pos_com_top_dict.pos_comment_word). \
        alias('pos_comment_word_dict')).\
        withColumn('pos_comment_word_json',F.to_json('pos_comment_word_dict')).\
        select('pos_comment_word_json')

    df_movie_pos_com_top_dict.show()

    # 导出为csv
    df_movie_pos_com_top_dict.write.mode("overwrite"). \
        format("csv"). \
        option("seq", "\t"). \
        option("header", True). \
        save("/comments/result/好评率前100电影的词频统计.csv")

    # pd.DataFrame(df_movie_pos_com_top_dict.toPandas()).to_excel("../result/好评率前100电影的词频统计.xlsx")

    #=========================================================================

    # ============================================================================

    # 将每一部电影的评论词整合,并且与电影信息连接
    df_movie_word = df_comment.groupBy('movie_id'). \
        agg(F.concat_ws(",", F.collect_list('comment_word'))).\
        withColumnRenamed("concat_ws(,, collect_list(comment_word))", "comment_word").\
        join(df_movie, 'movie_id', 'left')

    # # 按照类型进行整合
    # df_type_word = df_movie_word.groupBy('movie_type').\
    #     agg(F.concat_ws(",", F.collect_list('comment_word'))).\
    #     withColumnRenamed("concat_ws(,, collect_list(comment_word))", "comment_word")
    # df_type_word.show()
    #
    #
    # # 对电影类型进行统计，选出电影数目最多的10个类型
    # df_type_count_top = df_movie_word.\
    #     groupBy('movie_type').\
    #     agg(F.count('movie_id')).\
    #     withColumnRenamed("count(movie_id)", "movie_count").\
    #     orderBy(F.desc("movie_count")).limit(10)
    # df_type_count_top.show()
    # # filter(df_movie_word['movie_type'] != np.NaN).\
    #
    # # 得到电影数目最多的10个类型的所有评论词
    # df_type_top_word = df_type_count_top.join(df_type_word, "movie_type", "left")
    # df_type_top_word.show()
    #
    # # 对评论词进行统计
    # udf_words_statis = spark.udf.register("udf_words_statis", words_freq, MapType(StringType(), IntegerType()))
    # df_type_top_word_statis = df_type_top_word.select(df_type_top_word.movie_type,
    #                                           udf_words_statis(df_type_top_word.comment_word). \
    #                                           alias('comment_word_statis'))
    # df_type_top_word_statis.show()
    #
    # # # 词云生成
    # # pd_type_top_word_statis = df_type_top_word_statis.toPandas().dropna()
    # # for i in pd_type_top_word_statis.index:
    # #     plot_Wc(pd_type_top_word_statis["movie_type"][i]
    # #             , pd_type_top_word_statis["comment_word_statis"][i])
    #
    # # 对不同地区电影进行词云生成
    # # 按照地区进行整合
    # df_nation_word = df_movie_word.groupBy('movie_nation'). \
    #     agg(F.concat_ws(",", F.collect_list('comment_word'))). \
    #     withColumnRenamed("concat_ws(,, collect_list(comment_word))", "comment_word")
    # df_nation_word.show()
    #
    # # 对电影地区进行统计，选出电影数目最多的10个类型
    # df_nation_count_top = df_movie_word. \
    #     groupBy('movie_nation'). \
    #     agg(F.count('movie_id')). \
    #     withColumnRenamed("count(movie_id)", "movie_count"). \
    #     orderBy(F.desc("movie_count")).limit(10)
    # df_nation_count_top.show()
    # # filter(df_movie_word['movie_type'] != np.NaN).\
    #
    # # 得到电影数目最多的10个地区的所有评论词
    # df_nation_top_word = df_nation_count_top.join(df_nation_word, "movie_nation", "left")
    # df_nation_top_word.show()
    #
    # # 对评论词进行统计
    # udf_words_statis = spark.udf.register("udf_words_statis", words_freq, MapType(StringType(), IntegerType()))
    # df_nation_top_word_statis = df_nation_top_word.select(df_nation_top_word.movie_nation,
    #                                                   udf_words_statis(df_nation_top_word.comment_word). \
    #                                                   alias('comment_word_statis'))
    # df_nation_top_word_statis.show()
    #
    # # # 词云生成
    # # pd_type_top_word_statis = df_nation_top_word_statis.toPandas().dropna()
    # # for i in pd_type_top_word_statis.index:
    # #     plot_Wc(pd_type_top_word_statis["movie_nation"][i]
    # #             , pd_type_top_word_statis["comment_word_statis"][i])

