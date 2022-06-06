"""
DSA - Ch4Ep4
Create a Flask server that can return routes and airports, create and drop tables, and update data
"""

import sys
import yaml
import logging
from pandas import DataFrame
from google.cloud import bigquery as bq
from flask import Flask, current_app, request

# setup logging and logger
logging.basicConfig(format='[%(levelname)-5s][%(asctime)s][%(module)s:%(lineno)04d] : %(message)s',
                    level=logging.INFO,
                    stream=sys.stderr)
logger: logging.Logger = logging


def load_config(path_to_yaml):
    """
    Function to parse args out of a yaml file
    """
    with open(path_to_yaml) as open_yaml:
        return yaml.full_load(open_yaml)


# load configuration
conf = load_config("config.yml")
logger.info(f"starting flask app")

# create flask app and BigQuery client
app = Flask(__name__)
# Use credential file if provided, if not use credential set in environment

# get bigquery configuration and create a bq client
project = conf['project']
dataset = conf['dataset']
logger.info(f"BiGquery Config: project='{project}', dataset='{dataset}'")
logger.info(f"Creating BigQuery client")
client = bq.Client(project=project)



# index route
@app.route("/")
def hello():
    return "DSA Airspace BigQuery API", 200


# getting airports by iata code route
@app.route('/airports', methods=["GET"])
def airport():
    """Query airports by iata code"""
    # variables from the global scope including the bq client
    global client, conf, dataset, project
    # get airports table name
    airports_table = conf["airports_table"]
    airports_full_table_name = f"{project}.{dataset}.{airports_table}"

    # get the iata GET param
    iata = request.args.get('iata', default=None)

    if iata is not None:
        # search for specific iata airport code
        # create a parametrized query
        logger.info(f"bq: query airports iata={iata}")
        query = f"select iata, airport, city, state, country, lat, lon from `{airports_full_table_name}` where iata = @iata"
        # create a bq job config to provide the iata param
        job_config = bq.QueryJobConfig(
            query_parameters=[
                bq.ScalarQueryParameter("iata", "STRING", iata),
            ]
        )
        # run the query
        result = client.query(query, job_config)

        # bq returns a list of dict rows as the result >> each row is a list item and each dict row contains column key/value pairs
        #   convert this using list/dict comprehensions
        #   data will again be a list of dicts
        data = [{k: v for k, v in row.items()} for row in result]

        # alternatively: we could also get the results by using the .to_dataframe()
        # df = result.to_dataframe()
        # print(df)
        # data = df.to_dict(orient="records")

        return {
            "iata": iata,
            "result": data,
        }, 200, {"content-type": "application/json"}
    else:
        # no iata code provided, return all airports
        logger.info(f"bq: query all airports")
        result = client.query(f"select iata, airport, city, state, country, lat, lon from `{airports_full_table_name}` order by iata")
        data = [{k: v for k, v in row.items()} for row in result]
        return {
            "iata": iata,
            "result": data,
        }, 200, {"content-type": "application/json"}


@app.route(('/routes'))
def get_route():
    """
    GET route that returns airline routes based on source and destination
    """
    # get src and dest if provided and formeat a dict for queries
    src = request.args.get("src", default=None)
    dest = request.args.get("dest", default=None)
    client = current_app.config['client']
    if src and not dest:
        # just src provided, returning all routes for that source
        logger.info(f"Returning all routes from {src}")
        query_job = client.query(f"select route_index, airline, src, dest, codeshare, stops, equipment from {dataset}.routes where src = \"{src}\" order by airline")
    elif dest and not src:
        # just dest provided, return all routes with that destination
        logger.info(f"Returning all routes to {dest}")
        query_job = client.query(f"select route_index, airline, src, dest, codeshare, stops, equipment from {dataset}.routes where dest = \"{dest}\" order by airline")
    elif src and dest:
        # both provided, return flights from src to dest
        logger.info(f"Returning all routes from {src} to {dest}")
        query_job = client.query(f"select route_index, airline, src, dest, codeshare, stops, equipment from {dataset}.routes where src = \"{src}\" and dest = \"{dest}\" order by airline")
    else:
        # no source/dest provided, return all
        logger.info(f"No src or dest provided")
        return all_routes()    
    
    rows = query_job.result()
    return {
        'src': src,
        'dest': dest,
        'results': [{k: v for k, v in row.items()} for row in rows]
    }


if __name__ == "__main__":
    # run flask app on port 5050
    app.run('0.0.0.0', 5050)
