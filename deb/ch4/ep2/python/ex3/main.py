import logging
import argparse
import yaml
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from flask import Flask, current_app, request

# setup logging and logger
logging.basicConfig(format='[%(levelname)-5s][%(asctime)s][%(module)s:%(lineno)04d] : %(message)s',
                    level=logging.INFO,
                    stream=sys.stderr)
# alias logging as logger
logger: logging.Logger = logging


def set_args():
    """
    Parse args and read config file
    """
    parser = argparse.ArgumentParser(description="Airspace API Parser")
    parser.add_argument("-c", "--config", help="Path to config yaml file", default="config.yml", required=False)
    args,_ = parser.parse_known_args()
    return args


def load_config(path_to_yaml):
    """
    Function to parse args out of a yaml file
    """
    with open(path_to_yaml) as open_yaml:
        return yaml.full_load(open_yaml)


# set cmd line args & load configuration
args = set_args()
conf = load_config(args.config)

# get db config params
db_host = conf['host']
db_user = conf['user']
db_pswd = conf['pswd']
db_name = conf['database']
# print db params (never print passwords!)
logger.info(f"flask mysql config: host={db_host} user={db_user} db={db_name}")
logger.info(f"starting flask app")


# create flask app and sqlalchemy engine
app = Flask(__name__)
# create a db engine with a connection pool
#   a QueuePool creates a pool of database connections. Since routes could be called by multiple clients
#   simultaneously, having a pool of db connection that we could pull from is a good idea. Please refer
#   to the create_engine documentation.
engine = create_engine(f"mysql+pymysql://{db_user}:{db_pswd}@{db_host}/{db_name}?charset=utf8", 
                       poolclass=QueuePool, pool_size=5, max_overflow=0)

# save the engine into the flask app cache to be accessed later
app.config['engine'] = engine


@app.route('/')
def all_routes():
    """main GET route to return all routes"""
    # it's NOT good practice to access the global flask `app` variable
    #  -- instead use the imported `current_app` flask class
    engine = current_app.config['engine']
    logger.info(f"query db for all routes")
    # get a new connection
    with engine.connect() as conn:
        # Return all routes from our database
        logger.info(f"returning all routes")
        result = conn.execute(
            text("select airline, src, dest, codeshare, stops, equipment from routes order by airline")
        )
        # get all the resulting db rows as dict (or mappings)
        rows = result.mappings().all()
        # use a list and dict comprehenssion to return all the rows
        return {
            'results': [{k: v for k, v in row.items()} for row in rows]
        }


@app.route('/airports')
def airport():
    """ GET route to search and return a airport by iata code"""
    # get the GET arg called iata
    iata = request.args.get('iata', default=None)
    logger.info(f"query db for iata: {str(iata)}")
    # get the db engine form config
    engine = current_app.config['engine']
    # create a new connection
    with engine.connect() as conn:
        # if the user has specified an iata GET arg
        if iata is not None:
            # search for specific iata airport code
            result = conn.execute(
                text("select iata, airport, city, state, country, CAST(lat AS CHAR) lat, CAST(lon AS CHAR) lon from airports where iata = :iata"),
                {'iata': str(iata).strip().upper()}
            )
            result = result.mappings()
            # inspect the first row. Do we have any rows matching the iata code provided?
            row = result.first()
            if row is not None:
                # return a single airport result
                return {
                    'iata' : iata,
                    'results': [{k: v for k, v in row.items()}]
                } 
            else:
                # airport code not found, return empty list
                return {
                    'iata' : iata,
                    'results': []
                }
        # if the user has NOT specified an iata GET arg
        else:
            # no iata code provided, return all airports
            logger.info(f"returning all airports")
            result = conn.execute(
                text("select iata, airport, city, state, country, CAST(lat AS CHAR) lat, CAST(lon AS CHAR) lon from airports order by iata")
            )
            rows = result.mappings().all()
            return {
                'iata' : iata,
                'results': [{k: v for k, v in row.items()} for row in rows]
            }


@app.route(('/routes'))
def get_route():
    """
    GET route that returns airline routes based on source and destination
    """
    # get src and dest GET args
    #   -- if provided, create a dict that we will use as parameters to our 
    #      sql statement
    src = request.args.get("src", default=None)
    dest = request.args.get("dest", default=None)
    sql_query_params = {
        "src": str(src).strip().upper(),
        "dest": str(dest).strip().upper(),
        }
    engine = current_app.config['engine']
    with engine.connect() as conn:
        if src and not dest:
            # just src provided, returning all routes for that source
            logger.info(f"Returning all routes from {src}")
            result = conn.execute(
                        text("select airline, src, dest, codeshare, stops, equipment from routes where src = :src order by airline"),
                        sql_query_params
                    )
        elif dest and not src:
            # just dest provided, return all routes with that destination
            logger.info(f"Returning all routes to {dest}")
            result = conn.execute(
                        text("select airline, src, dest, codeshare, stops, equipment from routes where dest = :dest order by airline"),
                        sql_query_params
                    )
        elif src and dest:
            # both provided, return flights from src to dest
            logger.info(f"Returning all routes from {src} to {dest}")
            result = conn.execute(
                        text("select airline, src, dest, codeshare, stops, equipment from routes where src = :src and dest = :dest order by airline"),
                        sql_query_params
                    )
        else:
            # no source/dest provided, return all
            logger.info(f"No src or dest provided")
            return all_routes()    
    
    rows = result.mappings().all()
    return {
        'src': src,
        'dest': dest,
        'results': [{k: v for k, v in row.items()} for row in rows]
    }


# start our flask app
if __name__ == "__main__":
    # run flask app on port 5050
    app.run('0.0.0.0', 5050)
