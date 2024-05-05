import logging
import requests
import json
import time

from concurrent.futures import ThreadPoolExecutor

from pymongo import MongoClient
from pymongo.operations import ReplaceOne

from acubed.preprocessing import FFRChartPreprocessor

class FFRDatabaseConnector(FFRChartPreprocessor):

    """Connects to FFR API via api_key (given by Velocity) and downloads all
    public chart data with additional preprocessing in 2.5 minutes.
    Stores all results in self.charts.
    """

    def __init__(self, config):
        super().__init__()
        for k, v in config.items():
            setattr(self, k, v)
        self.THREAD_POOL = 16
        self.max_retries = 3
        self.session = requests.Session()
        self.session.mount(
            'https://',
            requests.adapters.HTTPAdapter(pool_maxsize=self.THREAD_POOL,
                                        max_retries=self.max_retries,
                                        pool_block=True)
        )
        self.BASE_API_URL = "https://www.flashflashrevolution.com/api/api.php"
        self.API_URL = f"{self.BASE_API_URL}?key={self.FFR_API_KEY}&action={{}}"
        self._get_chart_urls()

    def get(self, url):
        response = self.session.get(url)
        logging.info("request was completed in %s seconds [%s]",
                     response.elapsed.total_seconds(), response.url)
        if response.status_code != 200:
            logging.error("request failed, error code %s [%s]",
                          response.status_code, response.url)
        if 500 <= response.status_code < 600:
            time.sleep(5)
        return response

    def download_charts(self, charts = []):
        with ThreadPoolExecutor(max_workers=self.THREAD_POOL) as executor:
            for response in list(executor.map(self.get, self.urls)):
                if response.status_code == 200:
                    chart = self.preprocess(json.loads(response.content))
                    charts.append(chart)
                else:
                    break
        self.charts = dict((d['_id'], dict(d, index=index))
            for (index, d) in enumerate(charts))

    def _get_chart_urls(self, chart_urls = []):
        try:
            for song in requests.get(self.API_URL.format('songlist')).json():
                chart_urls.append(
                    self.API_URL.format(f"chart&level={song['id']}"))
        except:
            pass
        self.urls = chart_urls

class MongoDBConnector():

    """Connects to MongoDB Database under a database user (created by WirryWoo)
    to update collections in MongoDB.

    MongoDB Login Credentials:
    Username: <FFR Username>
    Password: <FFR_API_KEY>
    """

    def __init__(self, config):
        for k, v in config.items():
            setattr(self, k, v)
        self.cluster_name = 'atlascluster.hlpskdz.mongodb.net'
        self.uri = 'mongodb+srv://{}:{}@{}/?retryWrites=true&w=majority'.format(
            self.USERNAME, self.MONGODB_KEY, self.cluster_name)
        self.client = MongoClient(self.uri)
        self.database_changes = None

    def upsert(self, data):
        operations = [ReplaceOne(
            filter={"_id": doc["_id"]},
            replacement=doc,
            upsert=True
        ) for doc in data]
        results = self.client.get_database(
            'ffr').charts.bulk_write(operations)
        self.database_changes = results.bulk_api_result

    def reset(self):
        results = self.client.get_database(
            'ffr').charts.delete_many({})
        return results