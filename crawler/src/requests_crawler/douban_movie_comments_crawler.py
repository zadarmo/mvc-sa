# %%
import re
import requests
from bs4 import BeautifulSoup  # 最主要的功能是从网页抓取数据
import pandas as pd
import os
from tqdm import tqdm
import traceback
import time
import numpy as np


# User-Agent
USER_AGENT = 'xxx'

# cookie信息
COOKIE = 'xxx'


# 隧道IP池代理配置信息
TUNNEL = 'xxx'  # 隧道代理IP
USERNAME = 'xxx'  # 用户名
PASSWORD = 'xxx'  # 密码


def random_sleep(lb, ub):
    """随机休眠，休眠时间为[lb, ub)的一个数
    """
    t = np.random.random(size=None) * (ub - lb) + lb
    time.sleep(t)


def get_bs(url: str):
    """通过cookie模拟豆瓣登录，然后获取url的BeautifulSoup对象

    Parameters
    ----------
    url : str
        _description_

    Returns
    -------
    _type_
        _description_
    """
    cookies = {
        "cookie": COOKIE
    }
    headers = {
        'User-Agent': USER_AGENT
    }
    # 隧道域名:端口号
    tunnel = TUNNEL

    # 用户名密码方式
    username = USERNAME
    password = PASSWORD
    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
        "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
    }
    html = requests.get(url, cookies=cookies, headers=headers, proxies=proxies)
    soup = BeautifulSoup(html.content, 'html.parser', from_encoding='utf-8')
    return soup


def get_movie_info(url: str):
    """爬取电影基本信息，url格式：https://movie.douban.com/subject/{id}
    电影名字

    类型 #info
    制片国家 #info
    语言 #info
    上映时间 #info
    片长 #info

    豆瓣评分
    评星
    评价人数
    评价5星人数占比
    评价4星人数占比
    评价3星人数占比
    评价2星人数占比
    评价1星人数占比

    Parameters
    ----------
    bs : BeautifulSoup
        电影详情页面对应的bs对象

    Returns
    -------
    _type_
        _description_
    """
    # print(f"url: {url}, 正在爬取基本信息...", end="")
    map_infos = {}

    bs = get_bs(url)
    print(url)
    name = bs.select("h1>span[property='v:itemreviewed']")[0].text
    map_infos["电影名称"] = name

    div_info = bs.select("#info")[0]
    tag_text_infos = [child.text for child in div_info.children if not (
        child.text.strip() == "")]
    pre_k = None
    for index, tag_text_info in enumerate(tag_text_infos):
        if ":" in tag_text_info:
            k, v = tag_text_info.split(":")
            if k in map_infos:
                map_infos[k] += v
            else:
                map_infos[k] = v
                pre_k = k
        else:
            map_infos[pre_k] += tag_text_info

    div_rating = bs.select("div[rel='v:rating']")[0]
    douban_rating = div_rating.find("strong").text
    douban_star = div_rating.select(".bigstar")[0].attrs["class"][2].lstrip(
        "bigstar")  # 评星 * 10(根据类名"ll bigstar bigstar35"获取)
    vote_num = div_rating.select("span[property='v:votes']")[0].text
    star_percent = [tag.text for tag in div_rating.select(".rating_per")]

    map_infos["豆瓣评分"] = douban_rating
    map_infos["豆瓣评星"] = douban_star
    map_infos["评价人数"] = vote_num
    map_infos["评价5星人数百分比"] = star_percent[0]
    map_infos["评价4星人数百分比"] = star_percent[1]
    map_infos["评价3星人数百分比"] = star_percent[2]
    map_infos["评价2星人数百分比"] = star_percent[3]
    map_infos["评价1星人数百分比"] = star_percent[4]

    # print("爬取基本信息完成. ", end="")
    return map_infos


def get_movie_single_comments(url: str):
    """爬取电影单个页面的短评信息

    评论日期
    评星
    有用数
    评论分类（好评、一般、差评）（根据评星计算：超过3星为好评，等于3星为一般，小于3星为差评）
    评论内容

    Parameters
    ----------
    url : str
        _description_
    """
    list_comments = []
    error_cnt = 0  # 评论信息有部分缺失的个数

    bs = get_bs(url)
    div_comments = bs.select("#comments>.comment-item")
    for index, div_comment in enumerate(div_comments):
        try:
            comment_datetime = div_comment.select(
                "span[class='comment-time']")[0].attrs["title"]
            # 评星 * 10(根据类名"allstar40 rating"获取)
            star = div_comment(class_=re.compile('allstar*')
                               )[0].attrs["class"][0].lstrip("allstar")
            useful_num = div_comment.select(
                "span[class='votes vote-count']")[0].text
            comment_type = None
            star_value = int(star)
            if star_value > 30:
                comment_type = "好评"
            elif star_value == 30:
                comment_type = "一般"
            else:
                comment_type = "差评"
            comment_content = div_comment.select("span[class='short']")[0].text

            map_comment = {
                "评论日期": comment_datetime,
                "评星": star,
                "有用数": useful_num,
                "评论分类": comment_type,
                "评论内容": comment_content
            }
            list_comments.append(map_comment)
        except Exception as e:
            error_cnt += 1
    return list_comments, error_cnt


def get_movie_all_comments(url_template: str):
    """爬取电影所有页面的短评信息

    Parameters
    ----------
    url_template : str
        电影短评url模板字符串，形如：https://movie.douban.com/subject/35183042/comments?{}limit=20&status=P&sort=new_score
        第一页：https://movie.douban.com/subject/35183042/comments?limit=20&status=P&sort=new_score
        第二页：https://movie.douban.com/subject/35183042/comments?start=20&limit=20&status=P&sort=new_score
        第二页：https://movie.douban.com/subject/35183042/comments?start=40&limit=20&status=P&sort=new_score
    bs_movie_info : BeautifulSoup
        _description_
    """
    print("正在爬取短评信息...")
    list_comments = []

    page_size = 20  # 豆瓣短评每页显示的个数
    i_page = 0
    cnt_comments = 0
    while cnt_comments < 500:
        random_sleep(1, 2)  # 休眠
        url = url_template.format("") if i_page == 0 else url_template.format(
            f"start={i_page * page_size}&")
        comments, error_cnt = get_movie_single_comments(url)
        list_comments.extend(comments)
        i_page += 1
        cnt_comments += len(comments)
        print(
            f"\rurl: {url}, 第{i_page}页, 爬取到评论{len(comments)}条, 累计爬取评论{cnt_comments}条.", end="")
        if len(comments) + error_cnt < 20:  # 说明是最后一页直接退出
            break
    print(f"爬取短评信息完成, 共爬取到{cnt_comments}条短评.")
    return list_comments


def init_set():
    s = set()
    COMMENT_PATH = "./comment_results"
    excel_comment = os.listdir(COMMENT_PATH)
    s = set([id.split(".")[0] for id in excel_comment])
    return s


IDS_PATH = '../../data/movie_ids'  # 若干个excel，每个excel存储该类别下所有电影的id
RESULT_PATH = './comment_results'  # 若干个excel，每个excel对应一个电影的短评信息爬取结果
excel_ids = os.listdir(IDS_PATH)

set_id = init_set()  # 用于判断哪些id已经爬取过（只爬了一部分评论也算爬取过）
info_columns = ["id", "电影名称", "导演", "编剧", "主演", "类型", "制片国家/地区", "语言", "上映时间", "片长", "又名", "IMDb",
                "豆瓣评分", "豆瓣评星", "评价人数", "评价5星人数百分比", "评价4星人数百分比", "评价3星人数百分比", "评价2星人数百分比", "评价1星人数百分比"]
comment_columns = ["电影名称", "评论日期", "评星", "有用数", "评论分类", "评论内容"]
for excel_id in tqdm(excel_ids):
    df = pd.read_excel(f"{IDS_PATH}/{excel_id}")
    print(excel_id)
    for id in df["id"]:
        id = str(id)
        comment_df = pd.DataFrame([], columns=comment_columns)
        try:
            random_sleep(1, 2)
            movie_url = f"https://movie.douban.com/subject/{id}"
            # 判重
            if id in set_id:
                continue

            # 电影基本信息
            movie_info = get_movie_info(movie_url)

            # 短评信息
            movie_short_comment_url_template = movie_url + \
                "/comments?{}limit=20&status=P&sort=new_score"
            movie_comments = get_movie_all_comments(
                movie_short_comment_url_template)
            for comment in movie_comments:
                data = [movie_info["电影名称"]]
                data.extend(list(comment.values()))
                tmp_df = pd.DataFrame(
                    [data], columns=comment_columns)
                comment_df = pd.concat([comment_df, tmp_df])

            # 短评信息保存到excel中
            comment_df.to_excel(
                f"{RESULT_PATH}/{id}.xlsx", index=False)
            set_id.add(id)  # 爬取过的id添加到集合中
        except Exception as e:
            traceback.print_exc()
            print(f"{id}异常，已跳过。" + str(e))
            comment_df.to_excel(
                f"{RESULT_PATH}/{id}.xlsx", index=False)
            set_id.add(id)
