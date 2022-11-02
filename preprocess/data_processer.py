import os
from torch.utils.data import Dataset
import pandas as pd


class DataProcesser(Dataset):
    """创建自定义Dataset数据集，初始化参数传入数据预处理器"""

    def __init__(self, csv_name, root_path = 'E:\Git\mvc-sa\data'):
        r"""
        csv_path保存csv数据文件的位置
        """

        self.root_path = root_path
        self.csv_path = os.path.join(root_path, csv_name)
        #读取数据
        self.read_file = pd.read_csv(self.csv_path)
        #数据长度
        self.data_len = self.read_file.shape[0]
        #特征数据
        self.datas = self.read_file.values[:,1:]

    def __getitem__(self, index):
        r"""
        返回index对应行的数据
        """

        return self.datas[index]

    def __len__(self):
        return self.data_len

    def data_clean(self, name, rate=0.5):
        r"""
        按照rate将数据分为测试集和验证集
        """


        # 数据预处理
        self.read_file.loc[self.read_file.Star < 3, 'Star'] = 0
        self.read_file.loc[self.read_file.Star > 3, 'Star'] = 1
        self.read_file.loc[self.read_file.Star == 3, 'Star'] = 2

        clean_csv = self.read_file[['Star', 'Comment']]

        # 保存
        csv_folder = os.path.join(self.root_path, name)
        if not os.path.exists(csv_folder):
            os.mkdir(csv_folder)

        to_csv_path = os.path.join(csv_folder, f'{name}.csv')
        if not os.path.exists(to_csv_path):
            clean_csv.to_csv(to_csv_path, index=0)

        print("Save completed.")

        #数据加载
        train_labels = []
        train_texts = []
        test_labels = []
        test_texts = []

        read_list = []
        train_list = []
        test_list = []

        train_count = 1
        with open(to_csv_path, encoding='utf-8') as f:
            read_list = f.readlines()

        read_len = len(read_list)
        rate = 0.5

        # train_list = read_list[1:5000]
        # test_list = read_list[5000:10000]

        train_list = read_list[1:int(read_len * rate)]
        test_list = read_list[int(read_len * rate):]

        for line in train_list:
            label, text = line.rstrip('\n').split(',', maxsplit=1)
            train_labels.append(int(label))
            train_texts.append(text)
            train_count += 1

        for line in test_list:
            label, text = line.rstrip('\n').split(',', maxsplit=1)
            test_labels.append(int(label))
            test_texts.append(text)

        print("Load completed.")

        return train_labels, train_texts, test_labels, test_texts

