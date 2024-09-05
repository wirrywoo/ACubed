"""Module providing kernel density estimates for train-test split methodology."""

from operator import itemgetter
from functools import partial

import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl
import seaborn as sns

from acubed.connector import MongoDBConnector

class HistogramVisualizer():

    """Generates histogram visualization of kernel density estimates of
    contested stepfile difficulties. Requires LaTeX for plot styling purposes.
    """

    def __init__(self, bins):
        self.rc_context = {"text.usetex": True}
        self.sns_context = {"axes.titlesize": 12, "axes.labelsize": 10}
        self.bins = bins

    def visualize(self, observed_df, title):
        """Create data visualization showing histogram of contested difficulties"""
        with plt.style.context('ggplot'), mpl.rc_context(self.rc_context):
            with sns.plotting_context("paper", rc = self.sns_context):
                vis = sns.displot(observed_df, x = observed_df.columns[0], kde = True,
                                bins = self.bins, color = '#00A3C8', alpha = 0.2)
                vis.set(yticklabels = [])
                vis.set(title = title)
                vis.set(ylabel = 'Density')
                vis.tick_params(left = False)

                return vis.figure.get_figure()

class ModelSelection(MongoDBConnector):

    """Uses kernel density estimates from contested difficulty sheet to apply
    train-test split methodology on entire FFR charts dataset.
    """

    def __init__(self, config, seed = 0):
        super().__init__(config)
        self.min_difficulty, self.max_difficulty = 1, 120
        self.seed = seed
        np.random.seed(self.seed)

        self.train = None
        self.weights = None
        self.test_size = None

    def train_test_split(self, observed_data, test_size, val = False):
        """Splits dataset into train and test sets"""
        self.train = self._get_raw_data()
        get_weight = partial(self._get_weight, observed_data)
        self.weights = np.array(list(map(get_weight, self.train)))
        self.test_size = test_size
        test_data = self._split_and_update()
        if val:
            val_data = self._split_and_update()
            return self.train, val_data, test_data
        return self.train, test_data

    def _split_and_update(self):
        """Utility function to split dataset"""
        _indices = self._get_indices(self.train, self.test_size)
        test = np.array(self.train)[_indices]
        self._update_variables(_indices)
        return test

    def _update_variables(self, indices):
        """Utility function to update train, weights and test_size"""
        mask = np.ones(len(self.train)).astype(bool)
        mask[indices] = False
        self.train = np.array(self.train)[mask]
        self.weights = self.weights[mask]
        self.test_size = self.test_size / (1-self.test_size)

    def _get_indices(self, data, test_size):
        """Utility function to generate indices"""
        return np.random.choice(range(len(data)), size = int(test_size*len(data)),
            replace = False, p = self.weights/np.sum(self.weights))

    def _get_raw_data(self):
        """Utility function to retrieve raw data"""
        return list(self.client.get_database('ffr').charts.find({
            'difficulty': { '$gte' : self.min_difficulty, '$lte' : self.max_difficulty}
        }, { '_id': 1, 'name': 1, 'difficulty': 1, 'chart': 1} ))

    def _get_weight(self, observed_data, chart):
        """Utility function to query for respective weight based on chart difficulty"""
        return np.pad(np.bincount(observed_data),
            self.max_difficulty - max(observed_data) - 1)[itemgetter('difficulty')(chart)]
