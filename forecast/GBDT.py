from sklearn.ensemble import GradientBoostingRegressor
from os.path import join
from Preprocess.Utils import base, delete_dir_and_makedir, merge_result
import numpy as np
import pandas as pd
import datetime
from sklearn.feature_extraction import DictVectorizer
import re
from os import makedirs
from os import listdir


class GBDT(object):
    def __init__(self, feature_dir_path, sort_result_dir):
        """
        :param feature_dir_path: 分割后带有 feature 的文件夹
        :param sort_result_dir:　由结果分割后的文件夹
        """
        self.feature_dir_path = feature_dir_path
        self.sort_result_dir = sort_result_dir

    def onehot_encode(self, train_csv_file, predict_csv_file):
        """
        :param train_csv_file: 需要进行独热编码的训练 csv 文件
        :param predict_csv_file: 需要进行独热编码的预测用 csv 文件
        :return: 进行热编码后处理的 Xtrain,ytrain,Xpredict
        xpredict 还需要三个特征
        TODO 提取正确的值
        """
        train_df = pd.read_csv(train_csv_file, header=0,
                               names=['province', 'market', 'type', 'key', 'date', 'averin1', 'averin3', 'averin7',
                                      'aver'])
        # len(df.columns) 返回 dataframe 的长度
        province_list = train_df['province'].unique()
        market_list = train_df['market'].unique()
        type_list = train_df['type'].unique()
        key_list = train_df['key'].unique()
        province_list = [item for item in map(lambda v: {'province': v}, province_list)]
        market_list = [item for item in map(lambda v: {'market': v}, market_list)]
        type_list = [item for item in map(lambda v: {'type': v}, type_list)]
        key_list = [item for item in map(lambda v: {'key': v}, key_list)]

        onehot_encoder = DictVectorizer()

        province_onehot = onehot_encoder.fit_transform(province_list).toarray()
        province_map = {}
        for province, onehot_code in zip(province_list, province_onehot):
            province_map[province['province']] = onehot_code

        market_onehot = onehot_encoder.fit_transform(market_list).toarray()
        market_map = {}
        for market, onehot_code in zip(market_list, market_onehot):
            market_map[market['market']] = onehot_code

        type_onehot = onehot_encoder.fit_transform(type_list).toarray()
        type_map = {}
        for Type, onehot_code in zip(type_list, type_onehot):
            type_map[Type['type']] = onehot_code

        key_onehot = onehot_encoder.fit_transform(key_list).toarray()
        key_map = {}
        for key, onehot_code in zip(key_list, key_onehot):
            key_map[key['key']] = onehot_code

        Xtrain, ytrain = [], []
        for item in train_df.itertuples(index=False):
            onehot_code = np.concatenate((province_map[item[0]], market_map[item[1]], type_map[item[2]],
                                          key_map[item[3]])).tolist()
            date = datetime.datetime.strptime(item[4], '%Y-%m-%d')

            onehot_code = onehot_code + [date.timestamp(), item[5], item[6], item[7]]
            Xtrain.append(onehot_code)
            ytrain.append([item[8]])

        predict_df = pd.read_csv(predict_csv_file, header=0,
                                 names=['province', 'market', 'type', 'key', 'date'])
        print(predict_df['market'][0])
        price_values = train_df.query("market=='%s'" % str(predict_df['market'][0]))['aver'].tolist()

        Xpredict = []
        for item in predict_df.itertuples(index=False):
            onehot_code = np.concatenate((province_map[item[0]], market_map[item[1]], type_map[item[2]],
                                          key_map[item[3]])).tolist()
            date = datetime.datetime.strptime(item[4], '%Y-%m-%d')
            onehot_code.append(date.timestamp())
            Xpredict.append(onehot_code)

        return np.array(Xtrain), np.array(ytrain), np.array(Xpredict), np.array(price_values)

    def fit(self, Xtrain, ytrain, params):
        """
        :param Xtrain: 特征集
        :param ytrain: 结果集
        :param params: 参数
        :return:　训练模型
        """
        regressor = GradientBoostingRegressor(**params)
        regressor.fit(Xtrain, ytrain)
        return regressor

    def predict(self, train_csv_file, predict_csv_file, res_file):
        Xtrain, ytrain, XPredict, price_values = self.onehot_encode(train_csv_file, predict_csv_file)
        params = {'n_estimators': 500, 'max_depth': 4, 'min_samples_split': 2,
                  'learning_rate': 0.01, 'loss': 'ls'}
        regressor = self.fit(Xtrain, np.ravel(ytrain), params)
        date_range = pd.date_range('20160701', '20160731')
        predict_df = pd.DataFrame({
            'date': date_range,
        }, index=date_range)
        values = []
        for i in range(0, 31):
            feature = XPredict[i]
            averin1 = price_values[-1:].mean()
            averin3 = price_values[-3:].mean()
            averin7 = price_values[-7:].mean()
            features = np.append(feature, [averin1, averin3, averin7]).reshape(1, -1)
            predict_value = regressor.predict(features)[0]
            ytrain = np.append(ytrain, [predict_value])
            values.append(predict_value)
        predict_df['aver'] = values
        predict_df.to_csv(res_file, index=False, header=False,
                          columns=['date', 'aver'])

    def run(self, forecast_dir):
        delete_dir_and_makedir(forecast_dir)
        for dir_path in listdir(self.sort_result_dir):
            forecast_dir_path = join(forecast_dir, dir_path)
            makedirs(forecast_dir_path)
            for file in listdir(join(self.sort_result_dir, dir_path)):
                file_name = re.findall(r'[a-zA-Z0-9].*', file)[0]
                train_csv_file = join(self.feature_dir_path, file_name)  # 训练文件路径
                predict_csv_file = join(self.sort_result_dir, dir_path, file)  # 需要预测文件路径
                res_file = join(forecast_dir_path, file)  # 保存结果文件路径
                print(predict_csv_file)
                with open(join(base, 'predict.log'), 'a') as f:
                    f.write(predict_csv_file + '\n')
                self.predict(train_csv_file, predict_csv_file, res_file)


if __name__ == '__main__':
    import warnings

    with warnings.catch_warnings():
        forecast_dir = join(base, 'forecast')
        sort_result = join(base, 'sort_result')
        warnings.simplefilter("error")
        gbdt = GBDT(join(base, 'farmingFeature'), sort_result)
        gbdt.run(forecast_dir)
        merge_result(forecast_dir, sort_result, join(base, 'fuck.csv'))
