import pandas as pd
from pyecharts.charts import *
from visual import *
import json
from pyecharts.globals import SymbolType

# 读取文件
df = pd.read_excel("./result/好评率前100电影的词频统计.xlsx")
word_freq_str = str(df['pos_comment_word_json'][0])
word_freq_json = word_freq_str + '}'
m = json.loads(word_freq_json)

data = []
filter_word = ['电影', '剧情', '故事', '影片']
for k, v in m.items():
    if k in filter_word:
        continue
    data.append((k, v))
mywordcloud = WordCloud()
mywordcloud.add('',data, shape=SymbolType.DIAMOND)
mywordcloud.set_global_opts(title_opts=opts.TitleOpts(title="好评率前100电影词云图", pos_left=330))
mywordcloud.render('./figures/好评率前100电影词云图.html')