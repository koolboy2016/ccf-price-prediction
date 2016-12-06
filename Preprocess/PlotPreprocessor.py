from os import listdir, makedirs
from os.path import join
from Preprocess.Utils import base, delete_dir_and_makedir
import pandas as pd
from matplotlib import pyplot as plt


# csv_file = '/home/wqlin/ccf/data/sort/4A0234139A014A1DC38F4A5243106323/水产46C2FCE254C74B03296E8899B265154F.csv'
# predict_csv_file = '/home/wqlin/ccf/data/forecast/4A0234139A014A1DC38F4A5243106323/水产46C2FCE254C74B03296E8899B265154F.csv'
# df = pd.read_csv(csv_file)
# df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
# df = df.set_index(pd.DatetimeIndex(df['date']))
# predict_df = pd.read_csv(predict_csv_file, header=None,
#                          names=['date', 'aver'])
# predict_df['date'] = pd.to_datetime(predict_df['date'], format='%Y-%m-%d')
# predict_df = predict_df.set_index(pd.DatetimeIndex(predict_df['date']))
# predict_df['aver'].plot(figsize=(20, 20), c='r', linewidth=3.0)
# df['aver'].plot(figsize=(20, 20), linewidth=3.0)
# plt.ylabel('price')
# plt.xlabel('date')
# plt.savefig('/home/wqlin/fuck.png')
# plt.show()
# plt.close()


class ForecastPlotter(object):
    def __init__(self, sort_dir, forecast_dir):
        self.sort_dir = sort_dir
        self.forecast_dir = forecast_dir

    def plot(self, sort_csv_file, forecast_csv_file, save_fig_file):
        sort_df = pd.read_csv(sort_csv_file)
        sort_df['date'] = pd.to_datetime(sort_df['date'], format='%Y-%m-%d')
        sort_df = sort_df.set_index(pd.DatetimeIndex(sort_df['date']))

        forecast_df = pd.read_csv(forecast_csv_file, header=None,
                                  names=['date', 'aver'])
        forecast_df['date'] = pd.to_datetime(forecast_df['date'], format='%Y-%m-%d')
        forecast_df = forecast_df.set_index(pd.DatetimeIndex(forecast_df['date']))
        forecast_df['aver'].plot(figsize=(20, 20), c='r', linewidth=3.0)
        ax = sort_df['aver'].plot(figsize=(20, 20), linewidth=3.0)
        plt.ylabel('price')
        plt.xlabel('date')
        ax.set_ylim(sort_df['aver'].min() * 0.8, sort_df['aver'].max() * 1.2)
        plt.savefig(save_fig_file)
        plt.cla()
        plt.clf()
        plt.close()

    def run(self, save_fig_dir):
        delete_dir_and_makedir(save_fig_dir)
        for dir_path in listdir(self.forecast_dir):
            makedirs(join(save_fig_dir, dir_path))
            temp_dir = join(self.forecast_dir, dir_path)
            for file in listdir(temp_dir):
                print(join(self.sort_dir,dir_path,file))
                self.plot(join(self.sort_dir, dir_path, file),
                          join(temp_dir, file), join(save_fig_dir, dir_path, file.replace('csv', 'png')))


if __name__ == '__main__':
    forecastplotter = ForecastPlotter(join(base, 'sort'), join(base, 'myforecast'))
    forecastplotter.run(join(base, 'forecastPlot'))
