#coding: utf8
import os
import pandas as pd
import re
from os import listdir
from os.path import join
from Utils import delete_dir_and_makedir, base, makedir_if_not_exists


class Spliter(object):
    """
    对原始数据进行分割，分割后将产生市场文件夹，每个市场文件夹下由对应的农产品组成
    并且按照日期进行降序排列
    """

    def split(self, csv_file, target_dir, isfarming=True):
        delete_dir_and_makedir(target_dir)
        if isfarming:
            df = pd.read_csv(csv_file,
                             header=0,
                             names=['province', 'market', 'type', 'key', 'spec', 'area', 'color', 'standard',
                                    'min', 'aver', 'max', 'enter_time', 'date'])
        else:
            df = pd.read_csv(csv_file,
                             header=0,
                             names=['province', 'market', 'type', 'key', 'date'])
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df_groups = df.groupby(by=['market', 'type', 'key'])
        for key in df_groups.groups:
            dir_path = join(target_dir, key[0])
            makedir_if_not_exists(dir_path)
            file = join(dir_path, key[1] + key[2] + '.csv')
            subdf = df.iloc[df_groups.groups[key]].sort_values(by=['date'])
            print(file)
            if isfarming:
                subdf.to_csv(file, index=False, header=True,
                             columns=['province', 'market', 'type', 'key', 'min', 'aver', 'max', 'date'])
            else:
                subdf.to_csv(file, index=False, header=True,
                             columns=['province', 'market', 'type', 'key', 'date'])


if __name__ == '__main__':
    pd.options.display.max_rows = 999999
    farming_csv_file = join(base, 'farming.csv')
    sort_dir = join(base, 'sort')
    product_market_csv_file = join(base, 'product_market.csv')
    sort_result_dir = join(base, 'sort_result')
    spliter = Spliter()
    spliter.split(farming_csv_file, sort_dir)
    spliter.split(product_market_csv_file, sort_result_dir, isfarming=False)
