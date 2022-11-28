'''
    对电影评论基本信息数据进行统计分析
'''
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType, IntegerType, ArrayType, MapType, FloatType
from pyspark.storagelevel import StorageLevel
import os


os.environ['HADOOP_CONF_DIR'] = "/opt/module/hadoop-3.1.3"

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

    # 统计各类别电影的数量
    df_type_movie_count = spark.sql(
        "SELECT movie_type, COUNT(*) AS movie_count FROM movie WHERE "
        "movie_year >= 2012 AND movie_year <=2022 GROUP BY movie_type "
    )

    df_type_movie_count.show()

    # 转成pandas 存本地
    # pd.DataFrame(df_type_movie_count.toPandas()).to_excel("../result/各类别电影数量.xlsx")
    # 导出为csv
    df_type_movie_count.write.mode("overwrite"). \
        format("csv"). \
        option("seq", "\t"). \
        option("header", True). \
        save("/comments/result/各类别电影数量.csv")


    # 统计各个国家上映的电影的数量
    df_nation_movie_count = spark.sql(
        "SELECT movie_nation, COUNT(*) AS movie_count FROM movie "
        "WHERE movie_year >= 2012 AND movie_year <=2022 GROUP BY movie_nation "
    ).na.fill('null')

    df_nation_movie_count.show()


    # 导出为csv
    df_type_movie_count.write.mode("overwrite"). \
        format("csv"). \
        option("seq", "\t"). \
        option("header", True). \
        save("/comments/result/各国家电影数量.csv")

    # 转成pandas 存本地
    # pd.DataFrame(df_nation_movie_count.toPandas()).to_excel("../result/各国家电影数量.xlsx")






