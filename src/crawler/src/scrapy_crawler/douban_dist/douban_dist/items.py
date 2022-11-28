# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

# ========================================= #
#                豆瓣网实体类
# ========================================= #

class MovieCommentItem(scrapy.Item):
    """豆瓣网电影评论实体类
    """
    comment_time = scrapy.Field()  # 评论时间
    movie_id = scrapy.Field()  # 电影id
    star = scrapy.Field()  # 评论评分
    votes = scrapy.Field()  # 点赞数
    content = scrapy.Field()  # 评论内容
    username = scrapy.Field()  # 用户名称
    area = scrapy.Field()  # 用户地区


# ========================================= #
#                时光网实体类
# ========================================= #

class MtimeMovieInfoItem(scrapy.Item):
    """时光网电影基本信息类
    """
    movie_id = scrapy.Field() 
    movie_url = scrapy.Field() 
    movie_name = scrapy.Field() 
    country = scrapy.Field() 
    movie_types = scrapy.Field() 
    year = scrapy.Field()
    month = scrapy.Field()
    day = scrapy.Field()
    length = scrapy.Field() 
    rating = scrapy.Field() 

class MtimeMovieCommentItem(scrapy.Item):
    """时光网电影评论类
    """
    comment_id = scrapy.Field()
    comment_time = scrapy.Field()
    content = scrapy.Field()
    movie_id = scrapy.Field()
    user_id = scrapy.Field()
    nickname = scrapy.Field()
    rating = scrapy.Field()
    votes = scrapy.Field()