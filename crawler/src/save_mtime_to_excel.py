import util
df_info = util.get_mtime_info()
df_info.to_excel("../data/test_set/info_2k.xlsx", index=False)
df_comments = util.get_mtime_comments()
df_comments.to_excel("../data/test_set/comments_5w.xlsx", index=False)