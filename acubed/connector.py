"""Module providing connector functions to access data sources."""

import json
import time
import logging
from concurrent.futures import ThreadPoolExecutor

import httplib2
import apiclient
import pandas as pd
import numpy as np

from pymongo import MongoClient
from pymongo.operations import ReplaceOne
import requests
from requests.exceptions import RequestException
from acubed.preprocessing import FFRChartPreprocesser

class FFRDatabaseConnector(FFRChartPreprocesser):

    """Connects to FFR API via api_key and downloads all
    public chart data with additional preprocessing in 2.5 minutes.
    Stores all results in self.charts.
    """

    def __init__(self, config):
        super().__init__()
        for k, v in config.items():
            setattr(self, k, v)
        self.thread_pool = 16
        self.max_retries = 3
        self.session = requests.Session()
        self.session.mount(
            'https://',
            requests.adapters.HTTPAdapter(pool_maxsize=self.thread_pool,
                                        max_retries=self.max_retries,
                                        pool_block=True)
        )
        self.base_api_url = "https://www.flashflashrevolution.com/api/api.php"
        self.api_url = f"{self.base_api_url}?key={self.FFR_API_KEY}&action={{}}"
        self._get_chart_urls()

        self.charts = {}

    def get(self, url):
        '''Function to fetch results from url'''
        response = self.session.get(url)
        logging.info("request was completed in %s seconds [%s]",
                     response.elapsed.total_seconds(), response.url)
        if response.status_code != 200:
            logging.error("request failed, error code %s [%s]",
                          response.status_code, response.url)
        if 500 <= response.status_code < 600:
            time.sleep(5)
        return response

    def download_charts(self, charts = None):
        '''Download all charts from FFR's API to self.charts'''
        if charts is None:
            charts = []
        with ThreadPoolExecutor(max_workers=self.thread_pool) as executor:
            for response in list(executor.map(self.get, self.urls)):
                if response.status_code == 200:
                    chart = self.preprocess(json.loads(response.content))
                    charts.append(chart)
                else:
                    break
        self.charts = dict((d['_id'], dict(d, index=index))
            for (index, d) in enumerate(charts))

    def _get_chart_urls(self, chart_urls = None):
        '''Utility function to retrieve all chart urls from FFR's API'''
        if chart_urls is None:
            chart_urls = []
        try:
            for song in requests.get(self.api_url.format('songlist'), timeout=10).json():
                chart_urls.append(
                    self.api_url.format(f"chart&level={song['id']}"))
        except RequestException:
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
        self.cluster = 'atlascluster.hlpskdz.mongodb.net'
        self.options = "?retryWrites=true&w=majority"
        self.uri = f"mongodb+srv://{self.USERNAME}:{self.MONGODB_PASSWORD}@{self.cluster}/{self.options}"

        self.client = MongoClient(self.uri)
        self.database_changes = None

    def upsert(self, data):
        '''Upserts stepfile into MongoDB database'''
        operations = [ReplaceOne(
            filter={"_id": doc["_id"]},
            replacement=doc,
            upsert=True
        ) for doc in data]
        results = self.client.get_database(
            'ffr').charts.bulk_write(operations)
        self.database_changes = results.bulk_api_result

    def reset(self):
        '''Clear MongoDB database'''
        results = self.client.get_database(
            'ffr').charts.delete_many({})
        return results

class FFRContestedDifficultySheet():
    """Connects to Google Sheets document containing a log of all
    contested difficulties on FFR. 
    """

    def __init__(self, api_key):
        self.max_difficulty = 120
        self.url = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
        self.service = apiclient.discovery.build(
            serviceName = 'sheets',
            version = 'v4',
            http = httplib2.Http(),
            discoveryServiceUrl = self.url,
            developerKey = api_key,
            cache_discovery = False
        )
        self.spreadsheet_id = '1Wm1RHG318EK07U4VDXkztKTKnfy9wEOQqWRiTclbCz8'

    def extract(self, year):
        '''Retrieve and preprocess data from Google Sheets'''
        range_name = f'{year} Difficulty Changes!B3:D250'
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, range=range_name).execute()
            values = result.get('values', [])
            df = pd.DataFrame(values,
                columns=['song_name', 'old_diff', 'new_diff'])
        except apiclient.http.HttpError:
            return None
        df.old_diff = pd.to_numeric(df.old_diff, errors='coerce')
        df.new_diff = pd.to_numeric(df.new_diff, errors='coerce')
        df.replace(0, np.nan, inplace=True)
        df.new_diff = df.new_diff.combine_first(df.old_diff)
        return df[df.new_diff <= self.max_difficulty].dropna()
