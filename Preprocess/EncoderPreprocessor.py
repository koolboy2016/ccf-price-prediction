"""
进行独热编码预处理类
"""
from os.path import join
from Utils import delete_dir_and_makedir, base
import pandas as pd


class SplitPreprocessor(object):
    def split(self, csv_file, dir_path, groupby_key='key'):
        """
        :param csv_file: 已经完成缺失值填补和特征提取的 farming 文件或者 product_market 文件
        :param dir_path: 存放分割后的 csv 文件目录
        :param groupby_key 进行分组的键值
        """
        delete_dir_and_makedir(dir_path)
        df = pd.read_csv(csv_file, header=0,
                         names=['province', 'market', 'type', 'key', 'date', 'averin1', 'averin3', 'averin7',
                                'aver'])
        group_df = df.groupby(groupby_key)
        for key in group_df.groups:
            print(group_df.groups[key])
            key_df = df.iloc[group_df.groups[key], :]

            file = join(dir_path, key_df[groupby_key].iloc[1] + '.csv')
            key_df.to_csv(file, index=False, header=True,
                          columns=['province', 'market', 'type', 'key', 'date', 'averin1', 'averin3', 'averin7',
                                   'aver'])


if __name__ == '__main__':
    splitpreprocessor = SplitPreprocessor()
    splitpreprocessor.split(join(base, 'farming_with_feature.csv'), join(base, 'farmingFeature'))
    # splitpreprocessor.split(join(base, 'product_market.csv'), join(base, 'productFeature'), isFarming=False)
