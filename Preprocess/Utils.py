import pandas as pd
from os.path import join
from os import listdir,remove
from os.path import exists
from shutil import rmtree
from os import makedirs

base = '/home/wqlin/Desktop/agri'


def delete_dir_and_makedir(dir_path):
    if exists(dir_path):
        rmtree(dir_path)
    makedirs(dir_path)

def makedir_if_not_exists(dir_path):
    if not exists(dir_path):
        makedirs(dir_path)


def merge_result(forecast_dir, sort_result_dir, res_file):
    """
    :param forecast_dir: 存放预测值的文件夹
    :param sort_result_dir: 存放由 product_market 分割的文件
    :return:
    """
    if exists(res_file):
        remove(res_file)
    result_list = []
    for dir_path in listdir(forecast_dir):
        for file in listdir(join(forecast_dir, dir_path)):
            price_file = join(forecast_dir, dir_path, file)
            price_df = pd.read_csv(price_file, header=0,
                                   names=['date', 'price'])
            price_df['date'] = pd.to_datetime(price_df['date'], format='%Y-%m-%d')
            price_df = price_df.set_index(pd.DatetimeIndex(price_df['date']))
            product_file = join(sort_result_dir, dir_path, file)
            product_df = pd.read_csv(product_file, header=0,
                                     names=['province', 'market', 'type', 'key', 'date'])
            product_df['date'] = pd.to_datetime(product_df['date'], format='%Y-%m-%d')
            result_list.append(pd.merge(product_df, price_df, how='left', on='date'))
    result_df = pd.concat(result_list)
    print(str(len(result_df)))
    assert len(result_df) == 43586
    result_df.to_csv(res_file, index=False, header=False)
