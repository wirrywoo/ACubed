"""Module providing definitions of stepfile features."""

from operator import itemgetter

import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.ensemble import VotingRegressor
from acubed.features import VerticalDensity, HorizontalDensity

class ChartDensityExtractor(BaseEstimator, TransformerMixin):
    """Transform to convert inputs to sktime-compatiable format."""

    def __init__(self):
        self.vertical = VerticalDensity()
        self.horizontal = HorizontalDensity()

    def fit(self, X, y=None):
        """Fit parameters (similar to sklearn-style)"""
        #pylint: disable=invalid-name,unused-argument
        return self

    def transform(self, X, y=None):
        """Apply transforms (similar to sklearn-style)"""
        #pylint: disable=invalid-name,unused-argument
        charts = list(map(itemgetter('chart'), X))
        df = pd.concat(list(map(self._get_features, charts)), keys = pd.RangeIndex(len(X)), names = ['instances'], axis = 0)
        return df

    def _get_features(self, chart):
        verticals = self.vertical.compute(chart)
        horizontals = self.horizontal.compute(chart)
        df =  pd.DataFrame.from_dict({
            'vertical': verticals, 'horizontal': np.sqrt(horizontals), 'interaction': np.multiply(verticals, np.sqrt(horizontals))})
        df.index = pd.RangeIndex(len(verticals))
        df.index.name = 'timepoints'
        return df

    def _map_many(self, iterable, f, *other):
        if other:
            return self._map_many(map(f, iterable), *other)
        return map(f, iterable)

class AggregateFeaturesTransformer(BaseEstimator, TransformerMixin):
    """Aggregates all features for stepfile."""

    def __init__(self, aggregate):
        self.aggregate = aggregate

    def fit(self, X, y=None):
        """Fit parameters (similar to sklearn-style)"""
        #pylint: disable=invalid-name,unused-argument
        return self

    def transform(self, X, y=None):
        """Apply transforms (similar to sklearn-style)"""
        #pylint: disable=invalid-name,unused-argument
        file_length = X.groupby('instances').agg(file_length = ("interaction", "count")).rdiv(1)
        df = pd.concat([X.groupby('instances').agg(self.aggregate), file_length], axis = 1)
        df.columns = df.columns.get_level_values(0)
        return df

class WeightedVotingRegressor(VotingRegressor):
    """Variant of VotingRegressor with tunable weights"""
    # pylint: disable=too-many-ancestors

    @property
    def weights(self):
        """Override weights"""
        return self._weights

    @weights.setter
    def weights(self, value):
        """Override weights"""
        if isinstance(value, float):
            value = [value, 1-value]
        self._weights = value
