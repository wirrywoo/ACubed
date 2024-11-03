"""Module providing connector functions to access data sources."""

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from operator import itemgetter
from typing import Dict, Any, List, ValuesView

import requests

from pymongo import MongoClient
from pymongo.operations import ReplaceOne

from acubed.preprocessing import FFRChartTransformer


class FFRDatabaseConnector:
    """
    Connects to the FFR API via an API key and downloads all public chart data.

    This process includes additional preprocessing, intended to be completed
    within 2.5 minutes, and stores all result
    s in self.charts.

    Parameters:
        config (Dict[str, Any]): Configuration dictionary to access API on FFR.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the FFRDatabaseConnector with the given configuration.
        """
        self.ffr_api_key = None
        if "USERNAME" not in config.keys():
            raise KeyError("Config dictionary parameter must contain username key.")
        if "FFR_API_KEY" not in config.keys():
            raise KeyError("Config dictionary parameter must contain FFR_API_KEY key.")
        for k, v in config.items():
            setattr(self, k.lower(), v)

        self.thread_pool: int = 16
        max_retries: int = 3
        self.session: requests.Session = requests.Session()
        self.session.mount(
            "https://",
            requests.adapters.HTTPAdapter(
                pool_maxsize=self.thread_pool,
                max_retries=max_retries,
                pool_block=True,
            ),
        )
        base_api_url: str = "https://www.flashflashrevolution.com/api/api.php"
        self.api_url: str = f"{base_api_url}?key={self.ffr_api_key}&action={{}}"

        self.song_list: List[Dict[str, Any]] = requests.get(
            "https://www.flashflashrevolution.com/game/r3/r3-playlist.php",
            headers={
                "User-Agent": " ".join(
                    [
                        "Mozilla/5.0 (Windows NT 6.1; WOW64)",
                        "AppleWebKit/537.36 (KHTML, like Gecko)",
                        "Chrome/56.0.2924.76",
                        "Safari/537.36",
                    ]
                )
            },
            timeout=10,
        ).json()

        self.transformer: FFRChartTransformer = FFRChartTransformer()

    def get(self, url: str) -> requests.Response:
        """
        Perform a GET request to the specified URL.
        """
        response = self.session.get(url)
        logging.info(
            "request was completed in %s seconds [%s]",
            response.elapsed.total_seconds(),
            response.url,
        )

        if response.status_code != 200:
            logging.error(
                "request failed, error code %s [%s]", response.status_code, response.url
            )

        if 500 <= response.status_code < 600:
            time.sleep(5)

        return response

    def download_charts(self) -> Dict[str, Dict[str, Any]]:
        """
        Downloads chart data for each song in the public engine and
        preprocesses the data.
        """
        songs: List[Dict[str, Any]] = []
        self.song_list = [
            dict(song, **{"url": self.api_url.format(f"chart&level={song['level']}")})
            for song in self.song_list
        ]

        with ThreadPoolExecutor(max_workers=self.thread_pool) as executor:
            for song, response in zip(
                self.song_list,
                executor.map(self.get, map(itemgetter("url"), self.song_list)),
            ):
                if response.status_code == 200:
                    song["chart"] = json.loads(response.content)["chart"]
                    song = self.transformer.fit_transform(song)
                    song["chart"] = [note._asdict() for note in song["chart"]]
                    songs.append(song)
                else:
                    break

        return {d["_id"]: dict(d, index=index) for (index, d) in enumerate(songs)}


class MongoDBConnector:
    """
    Connects to a MongoDB Database to update collections in MongoDB.

    Parameters:
        config (Dict[str, Any]): Configuration dictionary to access database in MongoDB.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initializes the MongoDBConnector with the provided configuration.
        """
        self.username = None
        self.mongodb_password = None
        for k, v in config.items():
            setattr(self, k.lower(), v)
        cluster = "atlascluster.hlpskdz.mongodb.net"
        options = "?retryWrites=true&w=majority"
        conn_string = f"{self.username}:{self.mongodb_password}"
        self.uri = f"mongodb+srv://{conn_string}@{cluster}/{options}"

        self.client: Any = MongoClient(self.uri)

    def upsert(self, data: ValuesView) -> Any:
        """
        Performs an upsert operation on the MongoDB database.

        This operation inserts new documents or updates existing documents based
        on the provided data.

        Args:
            data (List[Dict[str, Any]]): A list of dictionaries, each containing
                document data. Each dictionary must have an '_id' field used for
                identifying existing documents.
        """
        operations: List[Any] = [
            ReplaceOne(filter={"_id": doc["_id"]}, replacement=doc, upsert=True)
            for doc in data
        ]
        results = self.client.get_database("ffr").charts.bulk_write(operations)
        return results.bulk_api_result

    def reset(self) -> Any:
        """
        Deletes all documents from the 'charts' collection in the 'ffr' MongoDB database.
        """
        results = self.client.get_database("ffr").charts.delete_many({})
        return results
