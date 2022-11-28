import pandas as pd
from pyecharts.charts import *
from visualize.util.visual import *
import json
from pyecharts.globals import SymbolType

# 读取文件
df = pd.read_excel("./result/差评率前100电影的词频统计.xlsx")
word_freq_str = str(df['neg_comment_word_json'][0])
m = json.loads(word_freq_str)
sorted_m = sorted(m.items(), key=lambda x : x[1], reverse=True)
filtered_sorted_m = list(filter(lambda x: x[1] >= 30, sorted_m))  # 过滤掉出现次数 < 30的评论

data = []
filter_word = ['电影', '剧情', '故事']
for k, v in filtered_sorted_m:
    if k in filter_word:
        continue
    data.append((k, v))
mywordcloud = WordCloud()
mywordcloud.add('',data, shape=SymbolType.ROUND_RECT)
mywordcloud.set_global_opts(title_opts=opts.TitleOpts(title="差评率前100电影词云图", pos_left=330))
mywordcloud.render('./figures/差评率前100电影词云图.html')