#====================================================#
from pandas import Series
import numpy as np
import pandas as pd
import pandas.io.sql as sql
#====================================================#

#====================================================#
# dataframe operations
#====================================================#
# %% 1. df初始化
# 二维列表初始化
df = pd.DataFrame([
    ['a1', 1],
    ['a2', 4]
],
    columns=['uid', 'score'])

# dict初始化
df = pd.DataFrame({'col1': np.arange(3), 'col2': np.arange(5, 8)})
df = pd.DataFrame({'col1': [1, 2, 3, 4], 'col2': ['a', 'b', 'c', 'd']})

# 通过文件初始化
df = pd.read_excel(excel_path, header=1)  # header表示从第几行开始读。索引从0开始
df = pd.read_csv()

# 通过sql初始化
sql.read_frame('select * from test', conn)


# %% df, series索引
df = pd.DataFrame([
    ['a1', 1],
    ['a2', 4]
],
    columns=['uid', 'score'])
df[1]  # 取列名为1的列。df里没有，所以会报错
df.loc[1]  # 取index值为1的行。df的index默认从0开始，[0, 1, 2, ...]
df.iloc[1]  # 取第2行，这里1是下标，不是索引名也不是列名。


# %% 2. df输出
df.to_excel()
df.to_csv()


# %% 3. df增、删、改、赋值
# df取出某些列
df = df[["col1", "col2", "col3"]]  # 取出col1, col2, col3列

# df取出某一列转成list或set
myList, mySet = list(df["col"]), set(df["col"])

# df添加行
# 添加一行数据1 2 3, 列名为col1 col2 col3
df = df.append(pd.DataFrame([["1", "2", "3"]],
               columns=["col1", "col2", "col3"]))

# df删除行
df = df.drop(index=i)  # 删除行索引为i的行

# df添加列
df["new_col"] = list(range(10))  # 用列表为一列添加数据

# df删除列
del df["col"]

# df删除某列满足某条件的行
df = df[df["col1"] > 2]  # 取出满足col1 > 2的行

# df修改某个单元格的数据
df.loc[index, "col"] = new_val  # 将索引为index行的col列修改为new_val

# df修改某一列
df.loc[:, "col"] = list(new_val_arr)

# df同时给多列赋值
df.loc[index, ["col1", "col2", "col3"]] = new_val_matrix


# %% 4. df常用操作
# df遍历
for i, row in df.iterrows():
    print(i, row)  # i是索引index，row是一行数据，可以用列名索引这一行的列

# df合并
df = df.append(df2)  # 2022/8/10 马上要废弃了
df = pd.concat([df, df2], ignore_index=True)

# df取出满足条件的行
name_index = df["name"] == "wuxiang"  # 取出name列值为wuxiang的行
age_index = df["age"] > 18  # 取出age列值 > 18的行
# 取出满足以上两个条件的行的col1 col2 col3列
df.loc[name_index & age_index, ["col1", "col2", "col3"]]

# df条件索引
df[df["col1"] > 2]
df[df["name"].isin(mySet)]
df[df["name"].str[0] != "H"]  # 取出name列首字母不是H的行

# df将某一列看成字符串处理
df["col"] = df["col"].str.split()  # .str之后，就可以按string操作了
df["col"] = df["col"].str.count("是")  # 统计每一行的col列中，有多少个是

# df分组groupby统计数量
df = df.groupby(["col"]).count()  # 按col分组统计数量

# df分组查看每组信息
df_grouped = df.groupby(["col1", "col2", "col3"])
for name, group in df_grouped:
    print(name)
    print(group)


# %% df index操作
df = pd.DataFrame([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
    [1, 2, 3],
])
df = df.rename(index={0: "a", 1: "b", 2: "c", 3: "d"})  # 修改列名
# 将index重置为默认值，即[0, 1, 2, ...], drop=True表示将旧列名删掉
df = df.reset_index(drop=True)
#====================================================#


#====================================================#
# series operations
#====================================================#
# 创建Series
s = Series([195, 73], index=[">825.625", "<=825.625"])

# Series数学运算
s + 100
s - 100
s * 100
s / 100

np.sqrt(s)  # numpy实现开方运算
s[0] * 2  
s[[0, 1, 2]] * 2 # 对指定的某些单元格运算