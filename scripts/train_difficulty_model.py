"""Module created to refresh the MongoDB database with new FFR stepfiles."""

import logging
import time
from operator import itemgetter

from dotenv import find_dotenv, dotenv_values
import numpy as np
import pandas as pd

# https://github.com/ray-project/ray/issues/42257
# import joblib
# import ray
# from ray.util.joblib import register_ray
# register_ray()

from acubed.connector import FFRContestedDifficultySheet
from acubed.density import ModelSelection
from acubed.regressors import FFRDifficultyModel

from sklearn.metrics import root_mean_squared_error
from sklearn.linear_model import LinearRegression
from skpro.regression.residual import ResidualDouble

if __name__ == '__main__':

    #pylint: disable=duplicate-code

    LOG_FMT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=LOG_FMT)

    start_time = time.time()

    config = {
        **dotenv_values(find_dotenv())
    }

    sheet = FFRContestedDifficultySheet(config['GSHEETS_SECRET_KEY'])
    model_selection = ModelSelection(config)

    contested_diff_data = pd.concat([sheet.extract(yr).new_diff for yr in
        [2022, 2023, 2024]]).reset_index().new_diff.to_numpy(dtype = int)

    train, val, test = model_selection.train_test_split(contested_diff_data, test_size = 0.2, val = True)

    model = FFRDifficultyModel(subseq_len = 13)
    # residuals = LinearRegression()
    # proba = ResidualDouble(model, residuals)

    model.fit(train, np.fromiter(map(itemgetter('difficulty'), train), dtype=int))

    print(f"--- FFR Difficulty Model Trained: {time.time() - start_time} seconds ---")
    y_pred = model.predict(test)
    #y_pred = proba.predict_quantiles(test, alpha=[0.05, 0.5, 0.95])
    y_true = np.fromiter(map(itemgetter('difficulty'), test), dtype=int)

    print(root_mean_squared_error(np.fromiter(map(itemgetter('difficulty'), train), dtype=int), model.predict(train)))

    print(y_pred)
    print(y_true)
    print(root_mean_squared_error(y_true, y_pred))

    print(f"--- FFR Difficulty Predictions are generated: {time.time() - start_time} seconds ---")
