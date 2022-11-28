import os
import pandas as pd
import re
import numpy as np

class DataPredict:
    """创建自定义Dataset数据集，初始化参数传入数据预处理器"""

    def __init__(self, xlsx_name, root_path='E:\Git\mvc-sa\data'):
        r"""
        xlsx_path保存xlsx数据文件的位置
        """

        self.root_path = root_path
        self.xlsx_path = os.path.join(root_path, xlsx_name)
        # 读取数据
        self.read_file = pd.read_excel(self.xlsx_path)
        # 数据长度
        self.data_len = self.read_file.shape[0]
        # 特征数据
        self.datas = self.read_file.values[:, 1:]

    def data_predict_clean(self, name):
        r"""
        处理预测集数据
        """
        # 保存
        xlsx_folder = os.path.join(self.root_path, name)
        to_xlsx_path = os.path.join(xlsx_folder, f'{name}.xlsx')
        # 若没有清洗过的文件则创建
        if not os.path.exists(xlsx_folder):
            os.mkdir(xlsx_folder)
            clean_xlsx = self.read_file
            # 过滤空值
            clean_xlsx.replace(to_replace=r'^\s*$', value=np.nan, regex=True, inplace=True)
            clean_xlsx.dropna(inplace=True)
            # 过滤标点，表情，特殊符号
            clean_xlsx['评论内容'] = clean_xlsx['评论内容'].apply(
                lambda x: re.sub(r"[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+|[^\u4e00-\u9fa5]+", "", x))
            # 过滤空值
            clean_xlsx.replace(to_replace=r'^\s*$', value=np.nan, regex=True, inplace=True)
            clean_xlsx.dropna(inplace=True)
            clean_xlsx.to_excel(to_xlsx_path, index=False)

        read_list = pd.read_excel(to_xlsx_path)

        predict_texts = list(read_list['评论内容'])

        return predict_texts









