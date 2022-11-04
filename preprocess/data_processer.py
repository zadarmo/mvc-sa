import os
from torch.utils.data import Dataset
import pandas as pd
import openpyxl


class DataProcesser(Dataset):
    """创建自定义Dataset数据集，初始化参数传入数据预处理器"""

    def __init__(self, csv_name, root_path='E:\Git\mvc-sa\data'):
        r"""
        csv_path保存csv数据文件的位置
        """

        self.root_path = root_path
        self.csv_path = os.path.join(root_path, csv_name)
        # 读取数据
        self.read_file = pd.read_excel(self.csv_path)
        # 数据长度
        self.data_len = self.read_file.shape[0]
        # 特征数据
        self.datas = self.read_file.values[:, 1:]

        self.rate = 0.5

    def __getitem__(self, index):
        r"""
        返回index对应行的数据
        """

        return self.datas[index]

    def __len__(self):
        return self.data_len

    def data_clean(self, name, rate=0.7):
        r"""
        按照rate将数据分为测试集和验证集
        """

        # 数据预处理
        self.read_file.loc[self.read_file['评论评分'] < 30, ['评论评分']] = 0
        self.read_file.loc[self.read_file['评论评分'] > 30, ['评论评分']] = 1
        self.read_file.loc[self.read_file['评论评分'] == 30, ['评论评分']] = 2

        # 清洗部分价值低的数据
        self.read_file = self.read_file[self.read_file['点赞数'] > 0]

        clean_csv = self.read_file[['评论评分', '评论内容']]

        # 保存
        csv_folder = os.path.join(self.root_path, name)
        if not os.path.exists(csv_folder):
            os.mkdir(csv_folder)

        to_csv_path = os.path.join(csv_folder, f'{name}.xlsx')
        if not os.path.exists(to_csv_path):
            clean_csv.to_excel(to_csv_path, index=0)

        print("Save completed.")

        # 数据加载
        train_labels = []
        train_texts = []
        test_labels = []
        test_texts = []

        read_list = []
        train_list = []
        test_list = []

        # with open(to_csv_path, encoding='utf-8') as f:
        read_list = pd.read_excel(to_csv_path)

        read_len = len(read_list)
        self.rate = rate

        # train_list = read_list[1:5000]
        # test_list = read_list[5000:10000]

        train_list = read_list[1:int(read_len * rate)]
        test_list = read_list[int(read_len * rate):]

        train_labels = list(train_list['评论评分'])
        train_texts = list(train_list['评论内容'].fillna(''))

        test_labels = list(test_list['评论评分'])
        test_texts = list(test_list['评论内容'].fillna(''))

        print("--------------Load completed------------------")

        print("train_texts:", train_texts[:100])
        print("train_labels:", train_labels[:100])
        print("test_texts:", test_texts[:100])
        print("test_labels:", test_labels[:100])

        return train_labels, train_texts, test_labels, test_texts
