import pandas as pd
import pandas_alive
import bar_chart_race as bcr
import matplotlib
import matplotlib.pyplot as plt
plt.style.use('ggplot')
matplotlib.rc("font", family='Microsoft YaHei')
#读入数据
df = pd.read_excel("./result/各时间节点国家电影数量追逐图.xlsx",
                      index_col=1,
                      parse_dates=[1],
                      thousands=',')
del df[df.keys()[0]]
print(df[len(df) - 10:len(df) - 2])
bcr.bar_chart_race(df, "covid19_horiz2.gif", period_length=2)