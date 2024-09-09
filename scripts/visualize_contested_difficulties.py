"""Module created to refresh the MongoDB database with new FFR stepfiles."""

import logging
import time
from dotenv import find_dotenv, dotenv_values
import pandas as pd

from acubed.connector import FFRContestedDifficultySheet
from acubed.density import ModelSelection, HistogramVisualizer


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

    kde_plot = HistogramVisualizer(bins = 20)
    histogram = kde_plot.visualize(observed_df = pd.DataFrame(
        contested_diff_data, columns = ['Proposed FFR Difficulty']),
        title = 'Kernel Density Estimation of\n Contested Difficulties (2022 - present)')

    histogram.savefig('./reports/figures/plots/kde_contested_difficulties.png', dpi=300, bbox_inches = "tight")
