# coding: utf8
from Preprocess.Utils import delete_dir_and_makedir, base
import pandas as pd
from os import listdir, makedirs
from os.path import join


class FeatureExtractor(object):
    """
    从已经完成缺失值填充的文件中进行特征提取
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
        return rolling_df[90:]

    def run(self):
        for dir_path in listdir(self.src_dir):
            src_dir = join(self.src_dir, dir_path)
            target_dir = join(self.target_dir, dir_path)
            makedirs(target_dir)
            for file in listdir(src_dir):
                df = pd.read_csv(join(src_dir, file))
                if len(df) > 0:
                    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
                    offset = pd.Timedelta(days=90)
                    date_range = pd.date_range((df['date'].min() + offset).date(),
                                               df['date'].max().date())
                    averin1 = self.rolling_mean(df['aver'], 1)
                    averin7 = self.rolling_mean(df['aver'], 7)
                    averin15 = self.rolling_mean(df['aver'], 15)
                    averin30 = self.rolling_mean(df['aver'], 30)
                    averin90 = self.rolling_mean(df['aver'], 90)

                    assert len(averin1) == len(averin30) == len(averin7) == len(averin15) == len(averin90) == len(
                        df['aver'][90:])
                    target_df = pd.DataFrame({
                        'province': df['province'][0],
                        'market': df['market'][0],
                        'type': df['type'][0],
                        'key': df['key'][0],
                        'date': date_range,
                        'aver': df['aver'][90:],
                        'averin1': averin1,
                        'averin7': averin7,
                        'averin15': averin15,
                        'averin30': averin30,
                        'averin90': averin90
                    })
                    target_df.to_csv(join(target_dir, file), header=True, index=False,
                                     columns=['province', 'market', 'type', 'key', 'date', 'averin1',
                                              'averin7', 'averin15', 'averin30', 'averin90', 'aver'])


if __name__ == '__main__':
    feature_extractor = FeatureExtractor(join(base, 'sortImputation'), join(base, 'sortFeature'))
    feature_extractor.run()
