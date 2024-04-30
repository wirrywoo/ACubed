import numpy as np
import re

class FFRChartPreprocesser():

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

    def __init__(self, decimal_precision = 3):
        self.decimal_precision = decimal_precision
        self.encoding_mappings = {
            0: 1000,
            1: 100,
            2: 10,
            3: 1
        }

    def preprocess(self, chart_data):
        raw_data = chart_data.copy()
        chart = self._zero_framer_preprocessing(chart_data)
        chart = self._map_encodings(chart)
        chart = self._aggregate_steps(chart)

        return {
            '_id': raw_data['info']['id'],
            'name': raw_data['info']['name'],
            'difficulty': raw_data['info']['difficulty'],
            'chart': [{
                'time': np.round(time_stamp - chart[:, 0].min(), self.decimal_precision)/1000.,
                'step': str(int(step_encoding)).zfill(4)
            } for time_stamp, step_encoding in chart],

        }

    def _aggregate_steps(self, sorted_chart):
        row_mask = np.append(np.diff(sorted_chart[:,0],axis=0)!=0,[True])
        group_cumulative_sums = sorted_chart.cumsum(0)[row_mask,1:]
        group_sums = np.diff(group_cumulative_sums,axis=0)
        counts = np.concatenate((group_cumulative_sums[0,:][None],group_sums),axis=0)
        return np.concatenate((sorted_chart[row_mask,0][:,None],counts),axis=1)

    def _map_encodings(self, chart):
        (orientations, encoding_indices) = np.unique(chart[:, 0], return_inverse=True)
        chart[:, 0] = np.array([*map(
            self.encoding_mappings.get, orientations)])[encoding_indices]
        return np.flip(chart.astype(float), axis = 1)

    def _zero_framer_preprocessing(self, chart_data):
        sorted_chart = chart_data['chart']
        sorted_chart.sort(key = self._get_step_attributes)
        sorted_chart = np.array(sorted_chart)
        _, inverse_indices = np.unique(sorted_chart[:, [0, 1, 3]], axis=0, return_inverse=True)
        duplicate_indices = (np.argwhere(np.diff(inverse_indices) == 0) + 1).reshape(-1,)
        sorted_chart[duplicate_indices, :] += np.array([0, 0, 0, 1])
        return np.array(sorted_chart)[:, 1::2]

    def _get_step_attributes(self, step):
        return tuple(step[:2])

class SMChartPreprocesser():

    """Preprocesses SM file to a dictionary in following format:
    {
        'difficulty': None (no FFR rating is assigned for .sm files),
        'chart': {
            'time': timestamps (float),
            'step': binary step encodings (str)
        }
    }
    """
    def __init__(self):
        self.regex_dictionary = {
            "\n," : ",", "\n;" : ";"
        }
        self.notes, self.timings, self.chart = [], {}, {}

    def preprocess(self, path):
        with open(path, 'r') as sm_file:
            content = self.multiple_replace(self.regex_dictionary, sm_file.read())

        for line in content.split('\n'):
            if line.startswith("//"):
                continue
            try:
                sm_key, sm_value = tuple(line.split(':'))
                if sm_key not in ['#OFFSET', '#BPMS']:
                    continue
                if sm_key == '#OFFSET':
                    self.timings['offset'] = float(sm_value.strip(';'))
                else:
                    value = dict(map(float, bpm.split("="))
                        for bpm in sm_value.strip(';').split(","))
                    self.timings['bpm'] = value
            except ValueError:
                self.notes.append(line.strip(';'))

        time = -1*self.timings['offset']
        for i, measure in enumerate(' '.join(self.notes).split(', ')):
            measure = np.array(measure.strip().split(' '))
            beat = np.round(np.linspace(4*i, 4*(i+1), num=len(measure), endpoint=False), 3)
            for key, value in zip(beat, measure):
                if value != '0000':
                    if not len(self.chart):
                        min_time = time
                    self.chart[key] = {'time': time - min_time, 'step': value}
                _bpm = {v: k for k, v in self.timings['bpm'].items() if k <= key}
                bpm = max(_bpm, key=_bpm.get, default=None)
                time += 240./ (len(measure) * bpm)
        return {'chart': list(self.chart.values()), 'difficulty': None}

    def multiple_replace(self, dict, text):
        regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
        return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)