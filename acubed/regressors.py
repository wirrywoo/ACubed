"""Module containing all supported machine learning models in FFR."""

import numpy as np

from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.pipeline import make_pipeline, Pipeline
from sktime.regression.interval_based._tsf import TimeSeriesForestRegressor
from sktime.transformations.compose import FitInTransform
from sktime.transformations.series.subsequence_extraction import SubsequenceExtractionTransformer
from sktime.transformations.series.subset import ColumnSelect

from acubed.transformers import ChartDensityExtractor, AggregateFeaturesTransformer, WeightedVotingRegressor

class FFRDifficultyModel(BaseEstimator, RegressorMixin):
    """Transform to convert inputs to sktime-compatiable format."""

    def __init__(self, subseq_len):
        self.subseq_len = subseq_len
        self.columns = ['vertical', 'horizontal', 'interaction']
        self.pipeline = self.create_pipeline()

    def fit(self, X, y=None):
        """Fit parameters (similar to sklearn-style)"""
        #pylint: disable=invalid-name,unused-argument
        return self.pipeline.fit(X, y)

    def predict(self, X, y=None):
        """Apply predict (similar to sklearn-style)"""
        #pylint: disable=invalid-name,unused-argument
        return self.pipeline.predict(X)

    # def score(self, X, y=None):
    #     """Apply score (similar to sklearn-style)"""
    #     #pylint: disable=invalid-name,unused-argument
    #     return self.model.score(X, y)

    def create_pipeline(self):
        """Creates model pipeline for difficulty model"""
        return Pipeline([
            ('ffr_difficulty_model', WeightedVotingRegressor(
                estimators=[
                    ('local', self._local_regressor()),
                    ('global', self._global_regressor())
                ],
                weights=[0.5, 0.5]
            ))
        ])

    def _global_regressor(self):
        return Pipeline([
            ('transformer', self._global_transformer()),
            ('regressor', HistGradientBoostingRegressor(monotonic_cst=[1, 1, 1, -1]))
        ])

    def _global_transformer(self):
        return Pipeline([
            ('features', ChartDensityExtractor()),
            ('aggregates', AggregateFeaturesTransformer(aggregate = "median"))
        ])

    def _local_regressor(self):
        return WeightedVotingRegressor(
            estimators=[
                (col, self._local_dimensional_regressor(col)) for col in self.columns
            ],
            weights=[0.3, 0.3, 0.4]
        )

    def _local_dimensional_regressor(self, column):
        return Pipeline([
            ('transformer', self._local_dimensional_transformer(column)),
            ('regressor', TimeSeriesForestRegressor(n_estimators = 500, random_state = 0))
        ])

    def _local_dimensional_transformer(self, column):
        return make_pipeline(
            ChartDensityExtractor(),
            FitInTransform(SubsequenceExtractionTransformer(
                aggregate_fn = np.median, subseq_len = self.subseq_len)
                * ColumnSelect(columns=[column]))
        )
