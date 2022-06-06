## Part 3: Airports CRUD API using MariaDB

Now that we can create POST routes, let's revisit our airspace API. We already have routes for reading data, but now we can have them provide data via POST requests. Let's create support for the classic Create, Delete, and Update operations. Let's make a new subdirectory `python/ex3` and start a new `main.py`. This file will start with the expected imports and utils that we saw last episode:

```python
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
```

With these pieces in place, we can start our first POST route for table creation!

## Define table

For this route, we want to allow a user to supply JSON with a table name and a list of columns and datatypes which we will use to make an SQL table creation statement. First, let's specify the format of the JSON we're expecting. We will require JSON with the following format:

```json
{
    "name": "testing",
    "columns": [
        "myID int",
        "myname varchar(255)",
        "height float"
    ]
}
```

As mentioned, we have `name`, the table name and columns is a list of `"columnName SQL-datatype"`. So this JSON will define a table with 3 columns named `testing`. Let's split our functionality into two functions, one that uses a table name and this list to create a table and also a route function that will parse these values out of the POSTed data. This flexibility will allow us to make other routes that support different POSTed data types but reuse the same creation code. The creation function is straightforward, we take the two values and format a SQL statement with them and use our engine to execute that statement:

```python
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
```

Next we need to make our `/create` endpoint that supports JSON input. Our function will check if JSON input in supplied using `request.is_json`, an attribute that automatically checks the request headers for JSON inputs and return an error if we didn't get JSON. Then we simply extract the desired fields from `request.json` and call our creation function:

```python
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
```

If we add an `if __name__ == "__main__"` and choose a port to run our Flask server as usual, we can test this new route with Postman. Copy paste the above JSON table definition into Postman's **Body** > **raw** with JSON format selected and send the request!

>Note: make sure you SQL database is up and running for your server to access

![alt="screenshot of Postman POSTing a table creation JSON"](imgs/post-create.png)

Now let's use very similar logic to drop a table.

## Drop table
To drop a table, all we need to know is its name. As such, let's make a route that can take either a GET or POST response containing a table name and drop the associated table if it exists. In our decorator, we can add both GET and POST to our `methods` list. Then if our `request.method` is GET, we can use the arg `name` and similarly, if our `request.method` is POST, we get the `name` field of the posted JSON. We then quickly format a DROP statement an execute it with our engine:

```python
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

    # Use our engine to execute our drop statement
    engine = current_app.config['engine']
    with engine.connect() as conn:
        conn.execute(text(drop_sql))

    return f"Dropped {table_name}", 200
```

## Add data to table

Our last database operation to support is an update to a table. We will be using a similar pattern to the one used in Chapter 3, Episode 3, write our new data to a temporary table, then merge that into the target table. To accomplish this task, we will make a POST route that takes input JSON, creates a Pandas DataFrame from the data, gets the target table name from the JSON as well and then executes the above temp table merge:

```python
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
```

We need the JSON `data` field format to match the target table; for example, here is a JSON payload with two new or updated airports:

```json
 {
    "name": "airports",
    "data": {
        "iata":{
            "0": "NEW",
            "1": "FAKE"
        },
        "airport":{
        "0":"Lakefront Updated",
        "1":"Fake airport"
        },
        "city":{
        "0":"New Orleans",
        "1":"Nowhere"
        },
        "state":{
        "0":"LA",
        "1":"NO"
        },
        "country":{
        "0":"USA",
        "1":"USA"
        },
        "lat":{
        "0":30.04242056,
        "1":0.0
        },
        "lon":{
        "0":-90.02825694,
        "1":0.0
        }
    }
}
```

We note that the `data` is in standard Pandas JSON format for easy conversion. We can post this data from Postman to our new endpoint and see the new data be merged into our existing table:

![alt="Screenshot of Postman sending JSON to update our airport table"](imgs/post-update.png)

And with that we have a functioning Create, Update and Delete API!

```python
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

    # Use our engine to execute our drop statement
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

```
