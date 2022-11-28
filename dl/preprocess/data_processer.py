import os
import pandas as pd
import openpyxl


class DataProcesser:
    """创建自定义Dataset数据集，初始化参数传入数据预处理器"""

    def __init__(self, xlsx_name, root_path='E:\Git\mvc-sa\data'):
        r"""
        xlsx_path保存csv数据文件的位置
        """

        self.root_path = root_path
        self.xlsx_path = os.path.join(root_path, xlsx_name)
        # 读取数据
        self.read_file = pd.read_excel(self.xlsx_path)
        # 数据长度
        self.data_len = self.read_file.shape[0]
        # 特征数据
        self.datas = self.read_file.values[:, 1:]

        self.rate = 0.9

    def __getitem__(self, index):
        r"""
        返回index对应行的数据
        """

        return self.datas[index]

    def __len__(self):
        return self.data_len

    def data_clean(self, name):
        r"""
        按照rate将数据分为测试集和验证集
        """
        # 保存
        xlsx_folder = os.path.join(self.root_path, name)
        to_xlsx_path = os.path.join(xlsx_folder, f'{name}.xlsx')
        # 若没有清洗过的文件则创建
        if not os.path.exists(xlsx_folder):
            os.mkdir(xlsx_folder)

            # 数据预处理
            self.read_file = self.read_file[self.read_file['评论评分'] != 30]

            self.read_file.loc[self.read_file['评论评分'] < 30, ['评论评分']] = 0
            self.read_file.loc[self.read_file['评论评分'] > 30, ['评论评分']] = 1

            # self.read_file.loc[self.read_file['评论评分'] == 30, ['评论评分']] = 2

            # 清洗部分价值低的数据

            self.read_file = self.read_file[self.read_file['点赞数'] > 0]
            clean_xlsx = self.read_file
            # 过滤空值
            clean_xlsx = clean_xlsx.dropna(axis=0)
            clean_xlsx.to_excel(to_xlsx_path, index=False)

        print("Save completed.")

        read_list = pd.read_excel(to_xlsx_path)

        clean_texts = list(read_list['评论内容'])
        clean_labels = list(read_list['评论评分'])

        return clean_texts, clean_labels

