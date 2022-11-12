import pandas as pd
from pyecharts.charts import *
from visual import *

# 读取文件
df = pd.read_excel("./result/好评率前100各国家电影数.xlsx")
del df[df.keys()[0]]
data = [tuple(x) for x in df.values]
sorted_data = sorted(data, key=lambda x : x[1], reverse=True)

c = render_pie(sorted_data[:5])
c.render('./figures/好评率前100各国家电影数.html')