'''
    对电影评论数据和电影基本信息数据进行时间梯度上的统计分析
'''
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType, IntegerType, ArrayType, MapType, FloatType

from pyspark.sql import functions as F
from pyspark.storagelevel import StorageLevel
import os

os.environ['HADOOP_CONF_DIR'] = "/opt/module/hadoop-3.1.3"


def merge_nation_pos_rate(list):
    nation_pos_dict = dict()
    for l in list:
        nation_pos = l.split(":")
        nation = nation_pos[0]
        pos = nation_pos[1]
        if nation == 'NaN': continue
        if nation in nation_pos_dict:
            nation_pos_dict[nation] = (nation_pos_dict[nation]+float(pos))/2
        else:
            nation_pos_dict[nation] = float(pos)
    return nation_pos_dict


# 对电影评论分词后的结果进行分析
if __name__ == '__main__':
    spark = SparkSession.builder. \
        appName("test"). \
        master("local[*]"). \
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
    udf_merge_nation_pos_rate = spark.udf.register("udf_merge_nation_pos_rate", merge_nation_pos_rate, MapType(StringType(), FloatType()))

    # ================计算每个国家每个时间节点的累计电影数量=======================
    # # 选出电影数前10的国家
    pd_nation = spark.sql(
        "SELECT movie_nation, COUNT(*) AS movie_count FROM movie "
        "WHERE movie_year >= 2012 AND movie_year <=2022 GROUP BY movie_nation "
    ).orderBy(F.desc('movie_count')).limit(10).select('movie_nation').toPandas()

    # nation_list = ",".join(pd_nation['movie_nation'].values.tolist())
    nation_list = pd_nation['movie_nation'].values.tolist()
    nation_list.remove('NaN')

    # 广播列表
    spark.sparkContext.broadcast(nation_list)

    # 统计不同时间不同地区电影的数量
    df_movie_time_nation = df_movie.filter((df_movie.movie_year != 0) & (df_movie.movie_month != 0) & (df_movie.movie_day != 0)).\
        withColumn("movie_time", F.concat_ws("-", df_movie.movie_year, df_movie.movie_month, df_movie.movie_day)).\
        withColumn("nation_count", F.lit("1")).groupBy("movie_time").pivot('movie_nation', nation_list).\
        agg(F.sum("nation_count")).fillna(0).orderBy("movie_time")
    pd_movie_time_nation = df_movie_time_nation.toPandas()
    for item in nation_list:
        pd_movie_time_nation[item] = pd_movie_time_nation[item].cumsum()
    spark_df = spark.createDataFrame(pd_movie_time_nation)

    spark_df.show()

    # 导出为csv
    # spark_df.write.mode("overwrite"). \
    #     format("csv"). \
    #     option("seq", "\t"). \
    #     option("header", True). \
    #     save("/comments/result/各时间节点国家电影数量追逐图.csv")
    # pd.DataFrame(spark_df.toPandas()).to_excel("../result/各时间节点国家电影数量追逐图.xlsx")

    # =================计算每年各个国家的好评率 ===================
    # 计算每一部电影的评论数
    df_movie_comment_count = df_comment. \
        groupBy('movie_id'). \
        agg(F.count("comment_word")). \
        withColumnRenamed("count(comment_word)", "comment_count")
    df_movie_comment_count.show()

    # 计算每一部电影的好评数, 并且筛选掉评论数<30的电影
    df_movie_pos_count = df_comment. \
        filter(df_comment.emo_tag == 'pos').\
        groupBy('movie_id').\
        agg(F.count("comment_id")).\
        withColumnRenamed("count(comment_id)", "pos_comment_count").\
        join(df_movie_comment_count, 'movie_id', 'left').\
        join(df_movie, 'movie_id', 'left').\
        filter('comment_count is not null and pos_comment_count is not null and comment_count > 30')
    df_movie_pos_count.show()

    # 计算每一部电影的好评率 ，将国家和好评率通过':'拼接起来并按照年代进行整合
    df_movie_pos_rate = df_movie_pos_count.withColumn("pos_comment_rate", df_movie_pos_count.pos_comment_count / df_movie_pos_count.comment_count).\
        withColumn('nation:pos_rate', F.concat_ws(':', 'movie_nation','pos_comment_rate')).\
        filter('movie_year >= 2012 and movie_year <= 2022').\
        groupBy('movie_year').\
        agg(F.collect_list('nation:pos_rate')).\
        withColumnRenamed('collect_list(nation:pos_rate)', 'nation_pos_rate_list')
    df_movie_pos_rate.show()

    # 按照年份整合出每年所有国家的好评率，然后先将一行的字典拆为多行，然后再将多行拆多列
    df_movie_pos_rate = df_movie_pos_rate.select('movie_year', udf_merge_nation_pos_rate('nation_pos_rate_list').alias('nation_pos_rate_dict')).\
        orderBy('movie_year').\
        select('movie_year', F.explode_outer(F.col('nation_pos_rate_dict'))).\
        toDF('movie_year', 'nation', 'pos_rate'). \
        groupBy('movie_year').\
        pivot('nation').agg(F.first('pos_rate')).\
        na.fill(0)
    df_movie_pos_rate.show()

    # 导出为csv
    # df_movie_pos_rate.write.mode("overwrite"). \
    #     format("csv"). \
    #     option("seq", "\t"). \
    #     option("header", True). \
    #     save("/comments/result/年度国家电影好评率追逐图.csv")

   # pd.DataFrame(df_movie_pos_rate.toPandas()).to_excel("../result/年度国家电影好评率追逐图.xlsx")


