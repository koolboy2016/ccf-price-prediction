#coding: utf8
from Preprocess.Utils import delete_dir_and_makedir
import pandas as pd
from os import listdir, makedirs
from os.path import join


class FeatureExtractor(object):
    """
    从已经完成缺失值填充的文件中进行特征提取
    主要特征包括前一天的值，前三天均值，前七天均值
    """

    def __init__(self, src_dir, target_dir):
        """
        :param src_dir: 存放已经完成缺失值填补的文件夹
        :param target_dir: 存放提取特征后的文件夹
        """
        delete_dir_and_makedir(target_dir)
        self.src_dir = src_dir
        self.target_dir = target_dir

    def rolling_mean(self, df, window, shift=1):
        """

        :param df: 需要提取特征的 dataFrame
        :param window: 窗口大小
        :param shitf: 默认偏移1
        :return: 不提取最前面7天的 dataFrame
        """
        rolling_df = pd.rolling_mean(df, window=window).shift(shift)
        return rolling_df[7:]

    def run(self):
        for dir_path in listdir(self.src_dir):
            src_dir = join(self.src_dir, dir_path)
            target_dir = join(self.target_dir, dir_path)
            makedirs(target_dir)
            for file in listdir(src_dir):
                df = pd.read_csv(join(src_dir, file))
                if len(df) > 0:
                    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
                    offset = pd.Timedelta(days=7)
                    date_range = pd.date_range((df['date'].min() + offset).date(),
                                               df['date'].max().date())
                    averin1 = self.rolling_mean(df['aver'], 1)
                    averin3 = self.rolling_mean(df['aver'], 3)
                    averin7 = self.rolling_mean(df['aver'], 7)
                    assert len(averin1) == len(averin3) == len(averin7) == len(df['aver'][7:])
                    target_df = pd.DataFrame({
                        'province': df['province'][0],
                        'market': df['market'][0],
                        'type': df['type'][0],
                        'type_mapping': df['type_mapping'][0],
                        'date': date_range,
                        'average': df['average'][7:],
                        'averin1': averin1,
                        'averin3': averin3,
                        'averin7': averin7
                    })
                    target_df.to_csv(join(target_dir, file), header=True, index=False,
                                     columns=['province', 'market', 'type', 'key', 'date', 'averin1',
                                              'averin3', 'averin7', 'aver'])

