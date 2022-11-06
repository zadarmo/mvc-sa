# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter

import pymysql

MYSQL_CONFIG = {
    'host': 'xxx',
    'port': 3306,
    'user': 'xxx',
    'password': 'xxx',
    'database': 'xxx'
}

class MysqlPipeline:
    """豆瓣评论数据Mysql管道
    """
    def __init__(self):
        """建立数据库连接, 创建缓存(大小为100)
        """
        self.conn = pymysql.connect(
             host=MYSQL_CONFIG['host'], port=MYSQL_CONFIG['port'],
            user=MYSQL_CONFIG['user'], password=MYSQL_CONFIG['password'],
            database=MYSQL_CONFIG['database'], charset='utf8mb4'
        )
        self.cursor = self.conn.cursor()
        self.cache = []

    def close_spider(self, spider):
        """处理剩余不足100条的数据, 然后关闭数据库连接
        """
        if len(self.cache) > 0:
            try:
                self._save_cache_to_db()
            except Exception as e:
                print(str(e))
        self.cache.clear()
        self.conn.close()

    def process_item(self, item, spider):
        """每次向数据库中插入100条数据
        """
        comment_time = item["comment_time"]
        movie_id = item["movie_id"]
        star = item["star"]
        votes = item["votes"]
        content = item["content"]
        username = item["username"]
        area = item["area"]
        self.cache.append((comment_time, movie_id, star, votes, content, username, area))
        print(len(self.cache))
        if len(self.cache) >= 100:
            try:
                self._save_cache_to_db()
            except Exception as e:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print(str(e))
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            self.cache.clear()
        return item

    def _save_cache_to_db(self):
        """将当前cache中的数据存入mysql中
        """
        self.cursor.executemany(
            'insert into comments \
            (comment_time, movie_id, star, votes, content, username, area) \
            values (%s, %s, %s, %s, %s, %s, %s)',
            self.cache
        )
        self.conn.commit()  # 提交
        print("====================================")
        print(f"{len(self.cache)}条数据已存入数据库。")
        print("====================================")


class MtimeMovieInfoPipeline:
    """时光网电影基本信息管道
    """
    def __init__(self):
        """建立数据库连接, 创建缓存(大小为100)
        """
        self.conn = pymysql.connect(
             host=MYSQL_CONFIG['host'], port=MYSQL_CONFIG['port'],
            user=MYSQL_CONFIG['user'], password=MYSQL_CONFIG['password'],
            database=MYSQL_CONFIG['database'], charset='utf8mb4'
        )
        self.cursor = self.conn.cursor()
        self.cache = []

    def close_spider(self, spider):
        """处理剩余不足100条的数据, 然后关闭数据库连接
        """
        if len(self.cache) > 0:
            try:
                self._save_cache_to_db()
            except Exception as e:
                print(str(e))
        self.cache.clear()
        self.conn.close()

    def process_item(self, item, spider):
        """每次向数据库中插入1条数据
        """
        movie_id = item["movie_id"]
        movie_url = item["movie_url"]
        movie_name = item["movie_name"]
        country = item["country"]
        movie_types = item["movie_types"]
        year = item["year"]
        month = item["month"]
        day = item["day"]
        length = item["length"]
        rating = item["rating"]
        self.cache.append((movie_id, movie_url, movie_name, country, movie_types, year, month, day, length, rating))
        print(len(self.cache))
        if len(self.cache) >= 1:
            try:
                self._save_cache_to_db()
            except Exception as e:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print(str(e))
                for item in self.cache:
                    print(item)
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            self.cache.clear()
        return item

    def _save_cache_to_db(self):
        """将当前cache中的数据存入mysql中
        """
        self.cursor.executemany(
            'insert into mtime_movie_info \
            (movie_id, movie_url, movie_name, country, movie_types, year, month, day, length, rating) \
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
            self.cache
        )
        self.conn.commit()  # 提交
        print("====================================")
        print(f"{len(self.cache)}条数据已存入数据库。")
        print("====================================")

class MtimeMovieCommentPipeline:
    """时光网电影评论管道
    """
    def __init__(self):
        """建立数据库连接, 创建缓存(大小为100)
        """
        self.conn = pymysql.connect(
            host=MYSQL_CONFIG['host'], port=MYSQL_CONFIG['port'],
            user=MYSQL_CONFIG['user'], password=MYSQL_CONFIG['password'],
            database=MYSQL_CONFIG['database'], charset='utf8mb4'
        )
        self.cursor = self.conn.cursor()
        self.cache = []

    def close_spider(self, spider):
        """处理剩余不足100条的数据, 然后关闭数据库连接
        """
        if len(self.cache) > 0:
            try:
                self._save_cache_to_db()
            except Exception as e:
                print(str(e))
        self.cache.clear()
        self.conn.close()

    def process_item(self, item, spider):
        """每次向数据库中插入1条数据
        """
        comment_id = item["comment_id"]
        comment_time = item["comment_time"]
        content = item["content"]
        movie_id = item["movie_id"]
        user_id = item["user_id"]
        nickname = item["nickname"]
        rating = item["rating"]
        votes = item["votes"]
        self.cache.append((comment_id, comment_time, content, movie_id, user_id, nickname, rating, votes))
        print(len(self.cache))
        if len(self.cache) >= 1:
            try:
                self._save_cache_to_db()
            except Exception as e:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print(str(e))
                for item in self.cache:
                    print(item)
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            self.cache.clear()
        return item

    def _save_cache_to_db(self):
        """将当前cache中的数据存入mysql中
        """
        self.cursor.executemany(
            'insert into mtime_movie_comments \
            (comment_id, comment_time, content, movie_id, user_id, nickname, rating, votes) \
            values (%s, %s, %s, %s, %s, %s, %s, %s)',
            self.cache
        )
        self.conn.commit()  # 提交
        print("====================================")
        print(f"{len(self.cache)}条数据已存入数据库。")
        print("====================================")

    
