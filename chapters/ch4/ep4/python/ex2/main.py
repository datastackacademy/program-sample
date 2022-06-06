import sys
import yaml
import logging
from google.cloud import bigquery as bq
from flask import Flask, request


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

# get bigquery configuration and create a bq client
project = conf['project']
dataset = conf['dataset']
logger.info(f"bigquery Config: project='{project}', dataset='{dataset}'")
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
    table_name = conf["airports_table"]
    full_table_name = f"{project}.{dataset}.{table_name}"

    # get the iata GET param
    iata = request.args.get('iata', default=None)

    if iata is not None:
        # search for specific iata airport code
        # create a parametrized query
        logger.info(f"query {table_name} for iata: {iata}")

        query = f"""
            SELECT iata, airport, city, state, country, lat, lon 
            FROM `{full_table_name}` 
            WHERE 
                iata = @iata
            """
        logger.debug(f"query:\n {query}\n")

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
        # data = df.to_dict(orient="records")

        return {
            "iata": iata,
            "result": data,
        }, 200, {"content-type": "application/json"}
    else:
        # no iata code provided, return all airports
        logger.info(f"query all {table_name}")
        query = f"""
            SELECT iata, airport, city, state, country, lat, lon 
            FROM `{full_table_name}` 
            WHERE 
                iata = @iata
            ORDER BY iata
            """
        logger.debug(f"query:\n {query}\n")
        
        result = client.query(query)
        data = [{k: v for k, v in row.items()} for row in result]
        return {
            "iata": iata,
            "result": data,
        }, 200, {"content-type": "application/json"}


# query airline routes between two airports
@app.route(('/routes'))
def get_route():
    """
    GET route that returns airline routes based on source and destination
    """
    # variables from the global scope including the bq client
    global client, conf, dataset, project
    # get airports table name
    table_name = conf["routes_table"]
    full_table_name = f"{project}.{dataset}.{table_name}"

    # get src and dest from the GET params
    src = request.args.get("src", default=None)
    dest = request.args.get("dest", default=None)
    
    # check to see if we got both src and dest
    if (src is not None) and (dest is not None):
        logger.info(f"query {table_name} for src: {src} and dest: {dest}")

        query = f"""
            SELECT airline, src, dest, codeshare, stops, equipment
            FROM {full_table_name}
            WHERE
                src = @src
                AND
                dest = @dest
            ORDER BY airline, src, dest
        """
        logger.debug(f"query:\n {query}\n")

        # pass the SQL query params
        jc = bq.QueryJobConfig(
            query_parameters=[
                bq.ScalarQueryParameter("src", "STRING", src),
                bq.ScalarQueryParameter("dest", "STRING", dest),
            ]
        )
        # run the query
        result = client.query(query, jc)
        # convert the result into a list of dict rows
        data = [{k: v for k, v in row.items()} for row in result]
        # create the json response
        return {
            "src": src,
            "dest": dest,
            "result": data,
        }, 200, {"content-type": "application/json"}
    else:
        # not both src and dest are provided.
        # respond back with an error msg
        logger.debug("invalid ")
        return {
            "status": "error",
            "msg": "Please provide both a src and dest GET param to the routes to search!"
        }, 404, {"content-type": "application/json"}



if __name__ == "__main__":
    # run flask app on port 8080
    app.run('0.0.0.0', 8080)
