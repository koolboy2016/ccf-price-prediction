# coding: utf8
from sklearn.ensemble import GradientBoostingRegressor
from os.path import join
from Preprocess.Utils import base, delete_dir_and_makedir, merge_result, log, log_file
import numpy as np
import pandas as pd
import logging
from os import makedirs, listdir
# from sklearn.model_selection import GridSearchCV
from sklearn.grid_search import GridSearchCV
from os.path import exists
from datetime import datetime


class GBDT(object):
    def __init__(self, feature_dir,
                 sort_result_dir,
                 sort_dir):
        """
        :param feature_dir: 存放特征的文件夹
        :param sort_result_dir: 由 product_market 分割的文件夹
        :param sort_dir: 由 farming 分割的文件夹
        """
        self.feature_dir = feature_dir
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
                feature_csv_file,
                res_csv_file):
        sort_df = pd.read_csv(sort_csv_file)
        if sort_df['aver'].std() == 0:  # 如果方差为零，就不使用 GBDT
            self.predict2file(sort_df['aver'].mean(), res_csv_file)
        else:
            self.GBDTpredict(feature_csv_file, sort_result_file, res_csv_file)

    def GBDTpredict(self, train_csv_file, predict_csv_file,
                    res_csv_file):
        print('begin GBDT training')
        Xtrain, ytrain = [], []
        train_df = pd.read_csv(train_csv_file)
        for item in train_df.itertuples(index=False):
            date = datetime.strptime(item[4], '%Y-%m-%d')
            feature = [date.year, date.month, date.day, item[5], item[6], item[7], item[8], item[9]]
            Xtrain.append(feature)
            ytrain.append([item[-1]])

        Xtrain = np.array(Xtrain)
        ytrain = np.array(ytrain)
        param_test1 = [
            {'n_estimators': [i for i in range(100, 501, 20)], 'learning_rate': [i / 100 for i in range(1, 151, 5)]}]
        params = {'max_depth': 4, 'min_samples_split': 20, 'min_samples_leaf': 5,
                  'loss': 'ls', 'max_features': 'sqrt',
                  'subsample': 0.8,
                  'random_state': 10}
        gsearch = GridSearchCV(estimator=GradientBoostingRegressor(**params),
                               param_grid=param_test1, n_jobs=4, iid=False, cv=10)
        gsearch.fit(Xtrain, np.ravel(ytrain))
        best_params1 = gsearch.best_params_
        print('best_params1')
        print(best_params1)
        print(gsearch.best_score_)

        params['n_estimators'] = best_params1['n_estimators']
        params['learning_rate'] = best_params1['learning_rate']
        # 更新参数

        del (params['max_depth'])
        del (params['min_samples_split'])

        param_test2 = [{'max_depth': [i for i in range(2, 7, 1)],
                        'min_samples_split': [i for i in range(10, 251, 10)]}]
        gsearch = GridSearchCV(estimator=GradientBoostingRegressor(**params),
                               param_grid=param_test2)
        gsearch.fit(Xtrain, np.ravel(ytrain))
        best_params2 = gsearch.best_params_
        print('best_params2')
        print(best_params2)
        print(gsearch.best_score_)

        params['max_depth'] = best_params2['max_depth']
        params['min_samples_split'] = best_params2['min_samples_split']

        param_test3 = [{'min_samples_split': [i for i in range(10, 251, 10)],
                        'min_samples_leaf': [i for i in range(10, 151, 10)]}]
        gsearch = GridSearchCV(estimator=GradientBoostingRegressor(**params),
                               param_grid=param_test3)
        gsearch.fit(Xtrain, np.ravel(ytrain))
        best_params3 = gsearch.best_params_
        print('best_params3')
        print(best_params3)
        print(gsearch.best_score_)

        params['min_samples_split'] = best_params3['min_samples_split']
        params['min_samples_leaf'] = best_params3['min_samples_leaf']
        print('params:')
        print(params)
        log(log_file, str(params) + '\n')
        # regressor = GradientBoostingRegressor(**params)
        # regressor.fit(Xtrain, np.ravel(ytrain))

        price_values = np.array(train_df['aver'].tolist())
        predict_price = []
        predict_df = pd.read_csv(predict_csv_file)
        for item in predict_df.itertuples(index=False):
            averin1 = price_values[-1:].mean()
            averin7 = price_values[-7:].mean()
            averin15 = price_values[-15:].mean()
            averin30 = price_values[-30:].mean()
            averin90 = price_values[-60:].mean()
            date = datetime.strptime(item[-1], '%Y-%m-%d')
            predict_feature = np.array([date.year, date.month, date.day, averin1, averin7, averin15,
                                        averin30, averin90]).reshape(1, -1)
            price = gsearch.predict(predict_feature)[0]
            predict_price.append(price)
            price_values = np.append(price_values, [price])
        self.predict2file(np.array(predict_price).mean(), res_csv_file)

    def run(self, forecast_dir):
        delete_dir_and_makedir(forecast_dir)
        for dir_path in listdir(self.sort_result_dir):
            if not exists(join(forecast_dir, dir_path)):
                makedirs(join(forecast_dir, dir_path))
            for file in listdir(join(self.sort_result_dir, dir_path)):
                sort_csv_file = join(self.sort_dir, dir_path, file)
                sort_result_csv_file = join(self.sort_result_dir, dir_path, file)
                feature_csv_file = join(self.feature_dir, dir_path, file)
                res_csv_file = join(forecast_dir, dir_path, file)
                if not exists(res_csv_file):
                    log(log_file, res_csv_file)
                    self.predict(sort_csv_file, sort_result_csv_file,
                                 feature_csv_file, res_csv_file)


if __name__ == '__main__':
    sort_dir = join(base, 'sort')
    sort_result_dir = join(base, 'sort_result')
    forecast_dir = join(base, 'myforecast')
    featrue_dir = join(base, 'sortFeature')
    gbdt = GBDT(featrue_dir, sort_result_dir,
                sort_dir)
    logging.basicConfig(filename='exception.log', level=logging.DEBUG)
    try:
        gbdt.run(forecast_dir)
        merge_result(forecast_dir, sort_result_dir, 'myfuckgdbt.csv')
    except:
        logging.exception("Opps")
