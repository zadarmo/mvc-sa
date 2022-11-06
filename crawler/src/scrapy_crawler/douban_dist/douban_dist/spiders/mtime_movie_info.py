import scrapy
from scrapy.http.response.text import TextResponse
from scrapy_redis.spiders import RedisSpider
from urllib.parse import urlencode

from ..items import MtimeMovieInfoItem

class MtimeMovieInfoSpider(RedisSpider):
    name = 'mtime_movie_info'
    allowed_domains = ['http://front-gateway.mtime.com']
    custom_settings ={
        'DOWNLOAD_DELAY': 5,
        'ITEM_PIPELINES':{'douban_dist.pipelines.MtimeMovieInfoPipeline': 300,},
        'DOWNLOADER_MIDDLEWARES': {'douban_dist.middlewares.MtimeMovieInfoDownloaderMiddleware': 543}
    }  # spider对应的pipeline

    def start_requests(self):
        """生成待爬取的url，用于爬取指定年份的所有电影基本信息
        """
        url = f'http://front-gateway.mtime.com/mtime-search/search/unionSearch2'
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'xxx',
            'Host': 'front-gateway.mtime.com',
            'Origin': 'http://film.mtime.com',
            'Referer': 'http://film.mtime.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
        }
        # 爬取近10年的电影，每一年爬取前3页
        total_page = 3  # 总共的页数
        for year in range(2012, 2021 + 1):
            for i_page in range(1, total_page + 1):
                params = {
                    "keyword": "",
                    "pageIndex": str(i_page),
                    "pageSize": "20",
                    "searchType": "0",
                    "locationId": "290",
                    "genreTypes": "", 
                    "area": "",
                    "year": str(year)
                }
                encoded_params = urlencode(params)
                yield scrapy.Request(url=f'{url}?{encoded_params}', headers=headers, callback=self.parse)

    def parse(self, response: TextResponse):
        res = response.json()
        movies = res['data']['movies']
        for movie in movies:
            mtime_movie_info_item = MtimeMovieInfoItem()
            mtime_movie_info_item['movie_id'] = movie['movieId']
            mtime_movie_info_item['movie_url'] = movie['href']
            mtime_movie_info_item['movie_name'] = movie['name']
            mtime_movie_info_item['country'] = movie['locationName']
            mtime_movie_info_item['movie_types'] = movie['movieType']
            mtime_movie_info_item['year'] = movie['rYear']
            mtime_movie_info_item['month'] = movie['rMonth']
            mtime_movie_info_item['day'] = movie['rDay']
            mtime_movie_info_item['length'] = movie['length']
            mtime_movie_info_item['rating'] = movie['rating']
            yield mtime_movie_info_item

