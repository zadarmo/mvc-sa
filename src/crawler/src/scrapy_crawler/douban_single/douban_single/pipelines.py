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

    def __init__(self):
        """建立数据库连接, 创建缓存(大小为100)
        """
        self.conn = pymysql.connect(
            host=MYSQL_CONFIG['host'],
            port=3306,
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            database=MYSQL_CONFIG['database'],
            charset='utf8mb4'
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
        self.conn.close()

    def process_item(self, item, spider):
        """每次向数据库中插入100条数据
        """
        movie_id = item["movie_id"]
        star = item["star"]
        votes = item["votes"]
        content = item["content"]
        self.cache.append((movie_id, star, votes, content))
        if len(self.cache) >= 100:
            try:
                self._save_cache_to_db()
            except Exception as e:
                print(str(e))
            self.cache.clear()
        return item

    def _save_cache_to_db(self):
        """将当前cache中的数据存入mysql中
        """
        self.cursor.executemany(
            'insert into comments \
            (movie_id, star, votes, content) \
            values (%s, %s, %s, %s)',
            self.cache
        )
        self.conn.commit()  # 提交
        print("============================================================")
        print(f"{len(self.cache)}条数据已存入数据库。")
        print("============================================================")

    
