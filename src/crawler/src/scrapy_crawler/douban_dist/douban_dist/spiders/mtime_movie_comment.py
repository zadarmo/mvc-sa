import scrapy
from scrapy.http import HtmlResponse
from scrapy.http.response.text import TextResponse
from scrapy_redis.spiders import RedisSpider
from urllib.parse import urlencode
import pymysql

from ..items import MtimeMovieCommentItem

MYSQL_CONFIG = {
    'host': 'xxx',
    'port': 3306,
    'user': 'xxx',
    'password': 'xxx',
    'database': 'xxx'
}

class MtimeMovieCommentSpider(RedisSpider):
    name = 'mtime_movie_comment'
    allowed_domains = ['front-gateway.mtime.com']
    custom_settings ={
        'DOWNLOAD_DELAY': 3,
        'ITEM_PIPELINES':{'douban_dist.pipelines.MtimeMovieCommentPipeline': 300,},
        'DOWNLOADER_MIDDLEWARES': {'douban_dist.middlewares.MtimeMovieCommentDownloaderMiddleware': 543}
    } 

    def __init__(self):
        self.url = f'http://front-gateway.mtime.com/library/movie/comment.api'
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'front-gateway.mtime.com',
            'Origin': 'http://film.mtime.com',
            'Referer': 'http://film.mtime.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
        }

    def start_requests(self):
        """生成待爬取的url，用于爬取指定年份的所有电影基本信息
        """
        list_ids = self._get_ids()
        for movie_id in list_ids:
            params = {
               "tt": "xxx",
               "movieId": movie_id,
                "pageIndex": "1",
                "pageSize": "20",
                "orderType": "1",
            }
            encoded_params = urlencode(params)
            yield scrapy.Request(
                url=f'{self.url}?{encoded_params}', 
                headers=self.headers, 
                callback=self.parse, 
                cb_kwargs=dict(movie_id=movie_id, next_page=2)
            )

    def parse(self, response: HtmlResponse, movie_id: int, next_page: int):
        data = response.json()['data']
        comments = data['list']
        for comment in comments:
            mtime_movie_comment_item = MtimeMovieCommentItem()
            mtime_movie_comment_item['comment_id'] = comment['commentId']
            mtime_movie_comment_item['comment_time'] = comment['commentTime']
            mtime_movie_comment_item['content'] = comment['content']
            mtime_movie_comment_item['movie_id'] = movie_id
            mtime_movie_comment_item['user_id'] = comment['userId']
            mtime_movie_comment_item['nickname'] = comment['nickname']
            mtime_movie_comment_item['rating'] = comment['rating']
            mtime_movie_comment_item['votes'] = comment['praiseCount']
            yield mtime_movie_comment_item

        # 爬取前3页评论
        if data['hasMore'] and next_page <= 3:
            params = {
               "tt": "xxx",
               "movieId": movie_id,
                "pageIndex": str(next_page),
                "pageSize": "20",
                "orderType": "1",
            }
            encoded_params = urlencode(params)
            yield scrapy.Request(
                url=f'{self.url}?{encoded_params}', 
                headers=self.headers, 
                callback=self.parse, 
                cb_kwargs=dict(movie_id=movie_id, next_page=next_page + 1)
            )

    def _get_ids(self):
        """从数据库中读取所有电影id
        """
        conn = pymysql.connect(
            host=MYSQL_CONFIG['host'], port=MYSQL_CONFIG['port'],
            user=MYSQL_CONFIG['user'], password=MYSQL_CONFIG['password'],
            database=MYSQL_CONFIG['database'], charset='utf8'
        )
        cursor = conn.cursor()
        # all ids
        cursor.execute(
            'select movie_id from mtime_movie_info'
        )
        ids_result = cursor.fetchall()
        list_ids = [item[0] for item in ids_result]
        return list_ids
