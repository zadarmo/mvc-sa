# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieCommentItem(scrapy.Item):
    movie_id = scrapy.Field()  # 电影id
    star = scrapy.Field()  # 评论评分
    votes = scrapy.Field()  # 点赞数
    content = scrapy.Field()  # 评论内容

