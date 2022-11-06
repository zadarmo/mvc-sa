import pymysql

import scrapy
from scrapy.http import HtmlResponse
from scrapy import Selector

from ..items import MovieCommentItem

MYSQL_CONFIG = {
    'host': 'xxx',
    'port': 3306,
    'user': 'xxx',
    'password': 'xxx',
    'database': 'xxx'
}

class DoubanSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['movie.douban.com']

    def __init__(self):
        self.page_dict = {}  # 每个电影爬取到第几页了
        self.comments_num_dict = {}  # 每个电影爬取到了几条评论了

    def start_requests(self):
        """生成待爬取的url，每次生成电影的第一页评论(20条)
        """
        set_ids, set_crawled_ids = self._get_ids()
        set_diff = set_ids - set_crawled_ids
        for id in set_diff:
            # 第一页评论
            url = f'https://movie.douban.com/subject/{id}/comments?\
                limit=20&status=P&sort=new_score' 
            yield scrapy.Request(
                url=url, 
                callback=self.parse, 
                cb_kwargs=dict(movie_id=id)
            )

    def parse(self, response: HtmlResponse, movie_id: int):
        """解析爬虫返回的响应

        Parameters
        ----------
        response : HtmlResponse
            响应
        movie_id : int
            电影id
        """
        list_movie_comment_item = self._get_comments_from_response(response, movie_id)
        for comment_item in list_movie_comment_item: 
            # 将数据交给引擎
            yield comment_item

        # 继续爬取其他的页
        # urls_list = []
        # for url in urls_list:
        #     yield scrapy.Request(url=url)

    def _get_comments_from_response(self, response: HtmlResponse, movie_id: int):
        """从响应中解析电影名称和评论信息
        """
        sel = Selector(response)
        list_movie_comment_item = []
        comments = sel.css('#comments > div')
        for comment in comments:
            try:
                star = comment.css('div.comment > h3 > span.comment-info > span[class^="allstar"]::attr(class)').get().\
                        split(" ")[0].lstrip("allstar")
                votes = comment.css('div.comment > h3 > span.comment-vote > span::text').get()
                content = comment.css('div.comment > p > span::text').get()
                item = MovieCommentItem()
                item["movie_id"] = movie_id
                item["star"] = star
                item["votes"] = votes
                item["content"] = content
                list_movie_comment_item.append(item)
            except:
                pass # 跳过解析有误的评论
        return list_movie_comment_item

    def _get_ids(self):
        """从数据库中读取所有电影id和已经爬取过的电影id
        """
        conn = pymysql.connect(
            host=MYSQL_CONFIG['host'], port=MYSQL_CONFIG['port'],
            user=MYSQL_CONFIG['user'], password=MYSQL_CONFIG['password'],
            database=MYSQL_CONFIG['database'], charset='utf8'
        )
        cursor = conn.cursor()
        # all ids
        cursor.execute(
            'select movie_id from id_name_map'
        )
        ids_result = cursor.fetchall()
        set_ids = set([item[0] for item in ids_result]) 
        # crawled ids
        cursor.execute(
            'select distinct movie_id from comments'
        )
        crawled_ids_result = cursor.fetchall()
        set_crawled_ids = set([item[0] for item in crawled_ids_result]) 
        conn.close()
        return set_ids, set_crawled_ids
        


