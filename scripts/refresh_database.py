"""Module created to refresh the MongoDB database with new FFR stepfiles."""

import logging
import time
from dotenv import find_dotenv, dotenv_values
from acubed.connector import FFRDatabaseConnector, MongoDBConnector

# def main(config):
#     """ Runs data processing scripts to turn raw data from (../raw) into
#         cleaned data ready to be analyzed (saved in ../processed).
#     """

if __name__ == '__main__':

    start_time = time.time()

    config = {
        **dotenv_values(find_dotenv())
    }

    ## Completes in 0.061 seconds per song (goes through all songs in game)
    ffr = FFRDatabaseConnector(config)
    ffr.download_charts()

    print(f"--- Downloaded Charts: {time.time() - start_time} seconds ---")

    db = MongoDBConnector(config)
    db.upsert(ffr.charts.values())
    upserts = db.database_changes['upserted']

    print(f"--- Updated MongoDB database with new charts: {time.time() - start_time} seconds ---")

    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')


# if __name__ == '__main__':
#     LOG_FMT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#     logging.basicConfig(level=logging.INFO, format=LOG_FMT)

#     # # not used in this stub but often useful for finding various files
#     # project_dir = Path(__file__).resolve().parents[2]

#     # find .env automagically by walking up directories until it's found, then
#     # load up the .env entries as environment variables

#     env = {
#         **dotenv_values(find_dotenv())
#     }
#     main(env)
