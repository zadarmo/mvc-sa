import pandas as pd
from sqlalchemy import create_engine
mysql_columns = ['comment_time', 'movie_id', 'star', 'votes', 'content']
df = pd.read_csv('../data/train_set/comments_38w.csv', names=mysql_columns, header=0)
engine = create_engine(
    'mysql+pymysql://xxx:xxx@localhost:3306/xxx?charset=utf8mb4'
)
df.to_sql('comments', engine, if_exists='append', index=False, chunksize=100)