import os
from torch.utils.data import Dataset
import pandas as pd
from preprocess.predict import predict_review
import time

class DataPredict(Dataset):
    """创建自定义Dataset数据集，初始化参数传入数据预处理器"""

    def __init__(self, csv_name, root_path='E:\Git\mvc-sa\data'):
        r"""
        xlsx_path保存xlsx数据文件的位置
        """

        self.root_path = root_path
        self.xlsx_path = os.path.join(root_path, csv_name)
        # 读取数据
        self.read_file = pd.read_excel(self.xlsx_path)
        # 数据长度
        self.data_len = self.read_file.shape[0]
        # 特征数据
        self.datas = self.read_file.values[:, 1:]

    def data_clean(self):
        r"""
        处理预测集数据
        """

        # 评论列转list
        comment_list = (self.read_file['评论内容'].fillna('')).tolist()[:50]
        comment_value = []

        s_time = time.time()
        value = predict_review(comment_list)
        comment_value.append(value)
        p_time = time.time()
        print("time:", p_time - s_time)

        print("value:", comment_list)
        print("comment:", comment_value)






