import pandas as pd
from visualize.util.visual import *

# 读取文件
df = pd.read_excel("./result/各类别电影数量.xlsx")

# 数据清洗
df.dropna(inplace=True)

# 统计结果
m = {}
for index, row in df.iterrows():
    types = [item.strip() for item in row["movie_type"].split("/")]  # 讲每个类别分开
    for type in types:
        if type not in m:
            m[type] = 0
        else:
            m[type] = m[type] + int(row["movie_count"])

# 对dict按数量排序
sorted_m = sorted(m.items(), key = lambda x : x[1], reverse=True)
print(sorted_m)

xdata = []
ydata = []
for k, v in sorted_m[:15]:
    xdata.append(k)
    ydata.append(v)
c = render_bar(xdata, ydata)
c.render("./figures/各类别电影数.html")