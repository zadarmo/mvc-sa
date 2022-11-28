import pymysql
import pandas as pd
import redis
import openpyxl


#==========================================#
#                   MySQL
#==========================================#

MYSQL_CONFIG = {
    'host': 'xxx',
    'port': 3306,
    'username': 'xxx',
    'password': 'xxx',
    'database': 'xxx'
}

def get_mysql_connection():
    """获取mysql数据库连接
    """
    conn = pymysql.connect(
        host=MYSQL_CONFIG['host'],
        port=MYSQL_CONFIG['port'],
        user=MYSQL_CONFIG['username'],
        password=MYSQL_CONFIG['password'],
        database=MYSQL_CONFIG['database'],
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    return conn, cursor

def get_douban_info():
    conn, cursor = get_mysql_connection()
    cursor.execute(
        'select * from douban_movie_info'
    )
    result = cursor.fetchall()
    conn.close()

    columns = ["movie_id", "movie_name"]
    df = pd.DataFrame(result, columns=columns)
    return df

def get_douban_comments():
    """从数据库获取豆瓣电影评论
    """
    conn, cursor = get_mysql_connection()
    cursor.execute(
        'select * from comments'
    )
    result = cursor.fetchall()
    conn.close()

    columns = ["评论时间", "电影id", "评论评分", "点赞数", "评论内容"]
    df = pd.DataFrame(result, columns=columns)
    return df

def get_mtime_info():
    """从数据库获取时光网电影基本信息
    """
    conn, cursor = get_mysql_connection()
    cursor.execute(
        'select * from mtime_movie_info'
    )
    result = cursor.fetchall()
    conn.close()

    columns = ["电影id", "电影url", "电影名称", "国家", "类型", "年", "月", "日", "长度（分钟）", "打分"]
    df = pd.DataFrame(result, columns=columns)
    return df

def get_mtime_comments():
    """从数据库获取时光网电影评论
    """
    conn, cursor = get_mysql_connection()
    cursor.execute(
        'select * from mtime_movie_comments'
    )
    result = cursor.fetchall()
    conn.close()

    columns = ["评论id", "评论时间戳", "评论内容", "电影id", "用户id", "用户昵称", "用户评分", "点赞数"]
    df = pd.DataFrame(result, columns=columns)
    return df


#==========================================#
#                   Redis
#==========================================#

def get_values(db_id: int, key: str):
    """获取redis数据库id为db_id中的某个key的value值
    """
    r = redis.Redis(
        host="xxx",
        password="xxx",
        port=6379,
        db=db_id
    )
    res = r.hgetall(key)
    return res