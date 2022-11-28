import util
df_info = util.get_douban_info()
df_info.to_excel("../data/train_set/info_6k.xlsx", index=False)