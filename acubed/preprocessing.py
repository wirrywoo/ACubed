"""Module providing preprocessing functions to standardize stepfile data inputs."""

# import re
# from itertools import groupby, zip_longest

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from acubed.datatypes import Note, Stepfile

class FFRChartTransformer(BaseEstimator, TransformerMixin):

    """Preprocesses FFR API response to a dictionary in following format:
    {
        'id': id of stepfile (int),
        'name': name of stepfile (str),
        'difficulty': manually assigned difficulty of stepfile (int),
        'chart': {
            'time': timestamps (float),
            'step': binary step encodings (str)
        }
    }
    """

    def __init__(self):
        """
        Initializes the FFRChartTransformer. 
        """
        return

    def fit(self, X, y=None):
        """
        Prepare the transformer. This is a no-op for this transformer since no fitting is needed.

        Args:
            X (Dict[str, Any]): Input data in dictionary format.
            y (Optional[Any]): Optional target variable (not used).

        Returns:
            FFRChartTransformer: Returns the instance itself.
        """
        #pylint: disable=invalid-name,unused-argument
        return self

    def transform(self, X, y=None):
        """
        Transforms the given chart data into a structured format using Notes.

        Args:
            X (Dict[str, Any]): Dictionary containing chart data.
            y (Optional[Any]): Optional target variable (not used).

        Returns:
            Dict[str, Any]: Dictionary with transformed chart data including Note objects.
        """
        #pylint: disable=invalid-name,unused-argument

        data = np.array(X['chart'])[:, 1::2]
        steps = np.array([''.join(i) for i in np.eye(4)[data[:, 0]].astype('<U1')])
        times = (data[:, 1] - min(data[:, 1]))/1000.

        return {
            '_id': X['level'],
            'name': X['name'],
            'difficulty': X['difficulty'],
            'preview': X['previewhash'],
            'chart': Stepfile([Note(time = t, step = s) for t, s in zip(times, steps)]).notes
        }
