"""Module providing definitions of stepfile features."""

from operator import itemgetter
import datetime

import numpy as np
import polars as pl

class VerticalDensity():

    """Calculates the vertical density of the chart by identifying all
    temporal differences within the chart for each step orientation. The
    reciprocal of the timedeltas is returned as np.array([...]).

    Units: sec^(-1)
    """

    def __init__(self):
        pass

    def compute(self, chart):
        '''Returns computed density values per note for a given chart'''
        return pl.DataFrame(data = {
                    'time': map(itemgetter('time'), chart),
                    'step': map(itemgetter('step'), chart),
        }).with_columns(
            boolean = pl.col('step').str.extract_all(r"\d").cast(pl.List(pl.Int64)).cast(pl.List(pl.Boolean)),
            directions = ['left', 'down', 'up', 'right']
        ).explode(["boolean", "directions"]).filter(pl.col("boolean")) \
        .group_by('directions', maintain_order = True).agg(pl.col("time")) \
        .with_columns(delta=pl.col("time").list.diff()).explode(['time','delta']) \
        .select(pl.col(["time", "delta", "directions"]).sort_by("time")) \
        .with_columns(
            pl.col("delta").pow(-1).alias("density")) \
            .fill_null(0).get_column('density').to_numpy()

class HorizontalDensity():

    """Calculates the horizontal density of the chart by applying a mask
    (defined with respect to FFR's accuracy window) onto a stepfile.
    Returns np.array([...]).

    Units: utils per second (at a given timestamp per note in a chart, an action is defined as:
        - being able to hit that one note perfectly
        - being able to avoid hitting other neighboring notes
    )
    """

    def __init__(self):
        self.partition = np.array([-0.117, -0.083, -0.050, -0.017, 0.017, 0.050, 0.118])
        self.weights = np.array([0.1, 0.5, 1, 1, 1, 0.5])
        self.window_size = np.multiply(np.diff(self.partition), self.weights).sum()
        self.month, self.day, self.year = 10, 17, 2002

    def compute(self, chart):
        '''Returns computed density values per note for a given chart'''
        df = pl.DataFrame(data = {
            'time': self.map_many(chart, [itemgetter('time'), self.convert_to_ms]),
            'step': self.map_many(chart, [itemgetter('step'), self.sum_digits]),
        }).select(
            timestamp = pl.duration(milliseconds="time") + pl.datetime(
                month = self.month , day = self.day, year = self.year),
            time = pl.col('time'),
            step = pl.col('step')
        )

        _df = df.set_sorted('timestamp').rolling(index_column="timestamp", offset="-117ms", period="235ms") \
            .agg(pl.col('timestamp').alias('window'), pl.col('step')) \
            .explode("window", 'step') \
            .with_columns(((pl.col('window') - pl.col('timestamp'))/datetime.timedelta(seconds=1)).alias('delta')) \
            .with_columns(
                (pl.col('step') * self.define_weight_conditions(
                    list(map(tuple, np.hstack([
                        np.lib.stride_tricks.sliding_window_view(self.partition, 2),
                        self.weights.reshape(-1, 1)]))))
                ).alias('density')) \
            .group_by('timestamp', 'step').agg(pl.col("density").sum())

        return df.join(_df, on=['timestamp', 'step']).with_columns(
                pl.col("density").truediv(self.window_size).repeat_by(pl.col("step"))
            ).select(pl.col("density").explode()).get_column('density').to_numpy()

    def define_weight_conditions(self, arr):
        '''Helper function to define weight conditions'''
        if len(arr) == 0:
            return 0
        lower, upper, weight = arr.pop(0)
        if (lower == -0.017 and upper == 0.017):
            equality = 'both'
        else:
            equality = 'left' if lower < 0 else 'right'
        return pl.when(pl.col('delta').is_between(lower, upper, closed=equality )) \
            .then(weight).otherwise(self.define_weight_conditions(arr))

    def map_many(self, iterable, function_list):
        '''Helper function to apply multiple functions on iterables'''
        if function_list:
            function = function_list.pop(0)
            return self.map_many(map(function, iterable), function_list)
        return iterable

    def sum_digits(self, digit):
        '''Helper function to translate steps to number of notes'''
        return sum(int(x) for x in digit if x.isdigit())

    def convert_to_ms(self, seconds):
        '''Helper function to convert all timestamps to ms'''
        return 1000 * seconds
