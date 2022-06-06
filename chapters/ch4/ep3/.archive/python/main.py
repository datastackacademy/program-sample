"""
DSA - Ch4Ep3
Create a Flask server that can return routes and airports
"""

import logging
import argparse
from sqlalchemy.sql.expression import table
import yaml
import sys
from typing import List
from logging import DEBUG, INFO, log
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from flask import Flask, current_app, json, request
from pandas import DataFrame

# setup logging and logger
logging.basicConfig(format='[%(levelname)-5s][%(asctime)s][%(module)s:%(lineno)04d] : %(message)s',
                    level=INFO,
                    stream=sys.stderr)
logger: logging.Logger = logging


def set_args():
    """
    Parse args and read config file
    """
    parser = argparse.ArgumentParser(description="Airspace API Parser")
    parser.add_argument("-c", "--config", help="Path to config yaml file", default="config.yml")
    args,_ = parser.parse_known_args()
    return args


def load_config(path_to_yaml):
    """
    Function to parse args out of a yaml file
    """
    with open(path_to_yaml) as open_yaml:
        return yaml.full_load(open_yaml)


# load configuration
args = set_args()
conf = load_config(args.config)
logger.info(f"flask mysql config: host={conf['host']} user={conf['user']} db={conf['database']}")
logger.info(f"starting flask app")

# create flask app and sqlalchemy engine
app = Flask(__name__)
engine = create_engine(f"mysql+pymysql://{conf['user']}:{conf['pswd']}@{conf['host']}/{conf['database']}?charset=utf8mb4", 
                       poolclass=QueuePool, pool_size=5, max_overflow=0)
app.config['engine'] = engine


def create_table(table_name: str, columns: List[str]) -> str:
    """
    Function that takes a table name and list of columns and creates a table
    """
    # Format our SQL creation string
    create_sql = f"CREATE TABLE {table_name} ({', '.join(columns)})"
    logger.info(create_sql)

    # Use our engine to execute our table creation
    engine = current_app.config['engine']
    with engine.connect() as conn:
        conn.execute(text(create_sql))

    return f"Created {table_name}"


@app.route("/create", methods=["POST"])
def json_table():
    """
    Method that takes a JSON schema and creates and SQL table
    """
    # Raise error if we did not get JSON input:
    if not request.is_json:
        return "No JSON supplied", 400

    # Get our JSON table definition
    json_data = request.json  
    # Create an SQL table creation string from the supplied parameters
    table_name = json_data["name"]
    column_list = json_data["columns"]

    created = create_table(table_name, column_list)

    return created, 200


@app.route("/drop", methods=["GET", "POST"])
def drop_table():
    """
    Function to drop a specified table
    """
    # Find the table name depending on request method
    if request.method == "GET":
        table_name = request.args.get("name")
    else:
        table_name = request.json['name']
    
    # Format our SQL drop string
    drop_sql = f"DROP TABLE IF EXISTS {table_name}"
    logger.info(drop_sql)

    # Use our engine to execute our drop statment
    engine = current_app.config['engine']
    with engine.connect() as conn:
        conn.execute(text(drop_sql))

    return f"Dropped {table_name}", 200


@app.route("/update", methods=["POST"])
def update_table():
    # Raise error if we did not get JSON input:
    if not request.is_json:
        return "No JSON supplied", 400

    # get the table name and make a DataFrame the posted data
    json_data = request.json
    table_name = json_data["name"]
    df = DataFrame(json_data['data'])
    logger.info(df)

    engine = current_app.config['engine']
    with engine.connect() as conn:
        # clears temporary table if it exists then write to temporary table
        tmp_table = 'tmp_merge'
        drop_statement = text(f"DROP TABLE IF EXISTS {tmp_table};")
        conn.execute(drop_statement)

        # write our data to the temp table
        df.to_sql(tmp_table, engine, if_exists='fail', chunksize=2000)

        # merge into target table 
        col_str = ", ".join(df.columns.to_list())
        merge_statement = text(f"REPLACE INTO {table_name}({col_str}) SELECT {col_str} FROM {tmp_table};")
        logging.info(merge_statement)
        conn.execute(merge_statement)

        # drop temp table
        conn.execute(drop_statement)
    
    return f"Updated {table_name}", 200



if __name__ == "__main__":
    # run flask app on port 5000
    app.run('0.0.0.0', 5000)
