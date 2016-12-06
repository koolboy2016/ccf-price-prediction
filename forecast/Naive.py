from sklearn.ensemble import GradientBoostingRegressor
from os.path import join
from Preprocess.Utils import base, delete_dir_and_makedir, merge_result, log, log_file
import numpy as np
import pandas as pd
import logging
from os import makedirs, listdir
from os.path import exists
from datetime import datetime


class Naive(object):
    def __init__(self, sort_result_dir, sort_dir):
        self.sort_result_dir = sort_result_dir
        self.sort_dir = sort_dir

    def predict2file(self, predict_values, res_csv_file):
        """
        将预测后的值写入文件
        :param predict_values: 预测值的均值
        :param res_file: 保存结果文件
        :return:
        """
        df = pd.DataFrame({
            'date': pd.date_range('20160701', '20160731'),
            'aver': predict_values
        })
        df.to_csv(res_csv_file, index=False, header=False,
                  columns=['date', 'aver'])

    def predict(self, sort_csv_file,
                sort_result_file,
                res_csv_file):
        sort_df = pd.read_csv(sort_csv_file)
        if sort_df['aver'].std() == 0:
            self.predict2file(sort_df['aver'].mean(), res_csv_file)
        else:
            if float(sort_df['aver'].iloc[-1]) > 20:
                value = float(sort_df['aver'].iloc[-1]) - 1
            else:
                value = float(sort_df['aver'].iloc[-1])
            self.predict2file(value, res_csv_file)

    def run(self, forecast_dir):
        delete_dir_and_makedir(forecast_dir)
        for dir_path in listdir(self.sort_result_dir):
            if not exists(join(forecast_dir, dir_path)):
                makedirs(join(forecast_dir, dir_path))
            for file in listdir(join(self.sort_result_dir, dir_path)):
                sort_csv_file = join(self.sort_dir, dir_path, file)
                sort_result_csv_file = join(self.sort_result_dir, dir_path, file)
                res_csv_file = join(forecast_dir, dir_path, file)
                if not exists(res_csv_file):
                    log(log_file, res_csv_file)
                    self.predict(sort_csv_file, sort_result_csv_file,
                                 res_csv_file)


if __name__ == '__main__':
    sort_dir = join(base, 'sort')
    sort_result_dir = join(base, 'sort_result')
    forecast_dir = join(base, 'naiveforecast')
    naive = Naive(sort_result_dir, sort_dir)
    naive.run(forecast_dir)
    merge_result(forecast_dir, sort_result_dir, 'myfucknaive.csv')
