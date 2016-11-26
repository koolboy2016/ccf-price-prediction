from Preprocess.Utils import delete_dir_and_makedir, base
from os import listdir, makedirs
from os.path import join
import pandas as pd


class Imputator(object):
    """
    对 sort 文件夹中文件缺失值进行填充
    """

    def __init__(self, sort_dir_path, target_dir_path):
        delete_dir_and_makedir(target_dir_path)
        self.sort_dir_path = sort_dir_path
        self.target_dir_path = target_dir_path

    def impute(self, src_file, target_file):
        src_df = pd.read_csv(src_file, header=0,
                             names=['province', 'market', 'type', 'key', 'min', 'aver', 'max', 'date'])
        src_df['date'] = pd.to_datetime(src_df['date'], format='%Y-%m-%d')
        end_date = src_df['date'].max().date()
        date_range = pd.date_range('20141125', end_date)
        target_df = pd.DataFrame({
            'pronvince': src_df['province'][0],
            'market': src_df['market'][0],
            'type': src_df['type'][0],
            'key': src_df['key'][0],
            'date': date_range,
        })
        target_df = pd.merge(target_df, src_df[['aver', 'date']], how='left', on='date')
        target_df = target_df.set_index(pd.DatetimeIndex(target_df['date']))
        target_df = target_df.interpolate(method='time', limit_direction='both').bfill()
        target_df.to_csv(target_file, header=True,
                         index=False,
                         columns=['province', 'market', 'type', 'key', 'aver', 'date'])

    def run(self):
        for src_dir in listdir(self.sort_dir_path):
            target_dir = join(self.target_dir_path, src_dir)
            makedirs(target_dir)
            for src_file in listdir(join(self.sort_dir_path, src_dir)):
                file = join(self.sort_dir_path, src_dir, src_file)
                target_file = join(target_dir, src_file)
                self.impute(file, target_file)


if __name__ == '__main__':
    imputator = Imputator(join(base, 'sort'), join(base, 'sortImputation'))
    imputator.run()
