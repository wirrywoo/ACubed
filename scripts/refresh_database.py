"""Module created to refresh the MongoDB database with new FFR stepfiles."""

# pylint: disable=import-error

import logging
import time
from dotenv import find_dotenv, dotenv_values
from acubed.connector import FFRDatabaseConnector, MongoDBConnector

def main(config):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """

if __name__ == '__main__':

    """Assumes FFR_API_KEY is provided by Velocity and MongoDB database access
    is granted by WirryWoo.
    """

    start_time = time.time()

    config = {
        **dotenv_values(find_dotenv())
    }

    ## Completes in 0.061 seconds per song (goes through all songs in game)
    ffr = FFRDatabaseConnector(config)
    ffr.download_charts()

    print("--- Downloaded Charts: %s seconds ---" % (time.time() - start_time))

    db = MongoDBConnector(config)
    db.upsert(ffr.charts.values())
    upserts = db.database_changes['upserted']

    print("--- Updated MongoDB database with new charts: %s seconds ---" % (time.time() - start_time))

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
