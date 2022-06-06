# Read and write from BigQuery
With our API up and running with our local SQL database, we can now consider how to add cloud integration into our API. We will do this in two steps; the first is to so replace our local SQL and SQLAlchemy engine with our BigQuery dataset and client. Once we have our routes updated to work with BigQuery, we can then learn to host our API on Google App Engine.

## Replace engine with Client
Following Chapter 3, we have a version of our airline data uploaded to a BigQuery dataset. We are going to convert our API to read from this data source instead of our local SQL. To do this, we first need to replace our local SQLAlchemy engine with a BigQuery client. We will start by making a directory called `python/ex1` and adding a `config.yml` with the following two values:

```json
project: <your project id>
dataset: <your dataset id>
```

As we know from the last chapter, these are the two values we need to set up a BigQuery client. Start a file called `main.py`. We will be copying the functionality of our previous unauthenticated APIs, both the GET and POST routes into this new API. We start by setting things up as usual but won't bother with arg parsing this time but conclude our setup with the BigQuery client:

```python
import logging
import argparse
import yaml
import sys
from typing import List
from logging import DEBUG, INFO, log
from pandas import DataFrame
from google.cloud import bigquery as bq
from google.oauth2 import service_account
from flask import Flask, current_app, request

# setup logging and logger
logging.basicConfig(format='[%(levelname)-5s][%(asctime)s][%(module)s:%(lineno)04d] : %(message)s',
                    level=INFO,
                    stream=sys.stderr)
logger: logging.Logger = logging


def load_config(path_to_yaml):
    """
    Function to parse args out of a yaml file
    """
    with open(path_to_yaml) as open_yaml:
        return yaml.full_load(open_yaml)


# load configuration from the config.yml
conf = load_config("config.yml") 
logger.info(f"starting flask app")

# create flask app and BigQuery client
app = Flask(__name__)
# Use credential file if provided, if not use credential set in environment
creds = conf.get('creds', None)
if creds is not None:
    creds = service_account.Credentials.from_service_account_file(creds, 
        scopes=["https://www.googleapis.com/auth/cloud-platform"])
project = conf['project']
logger.info(f" Creating Client on project {project}")
dataset = conf['dataset']

client = bq.Client(project=project, credentials=creds)
app.config['client'] = client
```

With our app ready to go, let's look at updating our first route to use this client.

## Update queries

We will still be using SQL queries but now executing them with `client.query()`. The first change to note is our query strings will now include our `dataset`. The next is instead of `conn.execute` inside a `while` statement, we just use `client.query()` and call the `results()` method to execute the query. We can see these two changes with our route that returns all airline routes:

```python
@app.route('/')
def all_routes():
    """main GET route to return all routes"""
    client = current_app.config['client']
    logger.info(f"query db for all routes")
    # Return all routes from our database
    logger.info(f"returning all routes")
    route_query = f"select route_index, airline, src, dest, codeshare, stops, equipment from {dataset}.routes order by airline"
    query_job = client.query(route_query)
    rows = query_job.result()
    return {
        'results': [{k: v for k, v in row.items()} for row in rows]
    }
````

We will follow this pattern of using Python format strings strings to make our SQL queries and then execute them with our `client.query().results()`. The remaining two GET routes update quiet straightforwardly:

```python
@app.route('/airports')
def airport():
    """ GET route to search and return a airport by iata code"""
    iata = request.args.get('iata', default=None)
    client = current_app.config['client']
    if iata is not None:
        # search for specific iata airport code
        query_job = client.query(f"select iata, airport, city, state, country, lat, lon from {dataset}.airports where iata = \"{iata}\"")
        try:
            # return a single airport result
            row = next(query_job.result())
            return {
                'iata' : iata,
                'results': [{k: v for k, v in row.items()}]
            } 
        except StopIteration:
            # airport code not found, return empty list
            return {
                'iata' : iata,
                'results': []
            } 
    else:
        # no iata code provided, return all airports
        logger.info(f"returning all airports")
        query_job = client.query(f"select iata, airport, city, state, country, CAST(lat AS CHAR) lat, CAST(lon AS CHAR) lon from {dataset}.airports order by iata")
        rows = query_job.result()
        return {
            'iata' : iata,
            'results': [{k: v for k, v in row.items()} for row in rows]
        }


@app.route(('/routes'))
def get_route():
    """
    GET route that returns airline routes based on source and destination
    """
    # get src and dest if provided and format a dict for queries
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
```

For our POST routes, we need to update our input JSON with the [BigQuery format for data types](https://cloud.google.com/bigquery/docs/schemas#standard_sql_data_types). Our `table.json` is therefore now:

```json
{
    "name": "testing",
    "columns": [
        "myID INTEGER",
        "myname STRING",
        "height FLOAT64"
    ]
}
```

The `create_table()` method itself just gets the same changes to use `client.query()` and include our `dataset`:

```python
def create_table(table_name: str, columns: List[str]) -> str:
    """
    Function that takes a table name and list of columns and creates a table
    """
    # Format our SQL creation string
    create_sql = f"CREATE TABLE IF NOT EXISTS {dataset}.{table_name} ({', '.join(columns)})"
    logger.info(create_sql)

    # Use our engine to execute our table creation
    client = current_app.config['client']
    query_job = client.query(create_sql)
    query_job.result()

    return f"Created {table_name}"
```

And there is no change to our create route, it simply need to be given the correctly formatted JSON as seen above:

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

Similarly, our drop route gets the expected two updates but nothing further is required:

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
    drop_sql = f"DROP TABLE IF EXISTS {dataset}.{table_name}"
    logger.info(drop_sql)

    # Use our engine to execute our drop statement
    client = current_app.config['client']
    query_job = client.query(drop_sql)
    query_job.result()

    return f"Dropped {table_name}", 200
```

The table updating route does require a bit more work. The temporary table creation can easily be done with the usual two changes. And we can write directly to that table using Pandas thanks to the `pandas-gbq` module in our requirements.txt. However, as we saw last chapter, BigQuery uses different merge syntax that our local MariaDB. Luckily, we can reuse the merge logic there to create our query string and execute it with the client as well. The only additional information we need is the index column for the merge which we can specify in our input JSON. Putting these all together gives us:


```python
@app.route("/update", methods=["POST"])
def update_table():
    # Raise error if we did not get JSON input:
    if not request.is_json:
        return "No JSON supplied", 400

    # get the table name and make a DataFrame the posted data
    json_data = request.json
    table_name = json_data["name"]
    index = json_data["index"]
    df = DataFrame(json_data['data'])
    logger.info(df)

    client = current_app.config['client']
    # clears temporary table if it exists then write to temporary table
    tmp_table = 'tmp_merge'
    drop_statement = f"DROP TABLE IF EXISTS {dataset}.{tmp_table};"
    client.query(drop_statement).result()
    

    # write our data to the temp table
    df.to_gbq(f"{dataset}.{tmp_table}", project_id=project, if_exists='fail', chunksize=2000)

    # merge the data from the tmp table into the target table
    # for a merge statement we need to create a string with our SQL command
    # because we will be updating all columns, we use list comprehension to make
    # the following strings from our column names and insert them into our query
    update_cols = ",".join([f"{col} = tmp.{col}" for col in df.columns])
    insert_cols = ",".join(df.columns.to_list())
    value_cols = ",".join([f"tmp.{col}" for col in df.columns])

    merge_statement = f"""
    MERGE `{project}.{dataset}.{table_name}` AS target
    USING `{project}.{dataset}.{tmp_table}` AS tmp
    ON target.{index} = tmp.{index}
    WHEN MATCHED
    THEN
        UPDATE SET {update_cols}
    WHEN NOT MATCHED
    THEN
        INSERT ({insert_cols})
        VALUES ({value_cols});
    """

    logging.info(merge_statement)
    client.query(merge_statement).result()

    # drop temp table
    client.query(drop_statement).result()
    
    return f"Updated {table_name}", 200
```

With example airport updating JSON file including the `index` column:

```json
{
    "name": "airports",
    "index": "iata",
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


We can now add our final piece:

```python
if __name__ == "__main__":
    # run flask app on port 5000
    app.run('0.0.0.0', 5000)
```

and test just as we did in the previous episodes!

# Host on Google App Engine

Up till now, we've been running our APIs locally via a simple `python main.py` call. This is great for testing but doesn't do a whole lot of good when we actually want them to be used. To host an API, we turn to [Google's App Engine](https://cloud.google.com/appengine/docs/standard/python3). This service allows us to host a Python Flask server on the cloud! We will follow their guide for [building an app]
(https://cloud.google.com/appengine/docs/standard/python3/building-app). If you have not already created a project, do as the first step. The second step is to **write our webapp**. Luckily we've already done the work above! Let's make one change to our code and replace our root route with a simple return so we can quickly check if our app worked without being bombarded by JSON. Add the following change:

```python
@app.route("/")
def hello():
    return "DSA Airspace", 200


@app.route('/all_routes')
def all_routes():
```

This way we can use our browser or Postman to quickly check when our service is up. The full code of our web service in `main.py` now consists of this:

```python
"""
DSA - Ch4Ep4
Create a Flask server that can return routes and airports, create and drop tables, and update data
"""

import logging
import argparse
import yaml
import sys
from typing import List
from logging import DEBUG, INFO, log
from pandas import DataFrame
from google.cloud import bigquery as bq
from google.oauth2 import service_account
from flask import Flask, current_app, request

# setup logging and logger
logging.basicConfig(format='[%(levelname)-5s][%(asctime)s][%(module)s:%(lineno)04d] : %(message)s',
                    level=INFO,
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
creds = conf.get('creds', None)
if creds is not None:
    creds = service_account.Credentials.from_service_account_file(creds, 
        scopes=["https://www.googleapis.com/auth/cloud-platform"])
project = conf['project']
logger.info(f" Creating Client on project {project}")
dataset = conf['dataset']

client = bq.Client(project=project, credentials=creds)
app.config['client'] = client


@app.route("/")
def hello():
    return "DSA Airspace", 200


@app.route('/all_routes')
def all_routes():
    """main GET route to return all routes"""
    client = current_app.config['client']
    logger.info(f"query db for all routes")
    # Return all routes from our database
    logger.info(f"returning all routes")
    route_query = f"select route_index, airline, src, dest, codeshare, stops, equipment from {dataset}.routes order by airline"
    query_job = client.query(route_query)
    rows = query_job.result()
    return {
        'results': [{k: v for k, v in row.items()} for row in rows]
    }


@app.route('/airports')
def airport():
    """ GET route to search and return a airport by iata code"""
    iata = request.args.get('iata', default=None)
    client = current_app.config['client']
    if iata is not None:
        # search for specific iata airport code
        query_job = client.query(f"select iata, airport, city, state, country, lat, lon from {dataset}.airports where iata = \"{iata}\"")
        try:
            # return a single airport result
            row = next(query_job.result())
            return {
                'iata' : iata,
                'results': [{k: v for k, v in row.items()}]
            } 
        except StopIteration:
            # airport code not found, return empty list
            return {
                'iata' : iata,
                'results': []
            } 
    else:
        # no iata code provided, return all airports
        logger.info(f"returning all airports")
        query_job = client.query(f"select iata, airport, city, state, country, CAST(lat AS CHAR) lat, CAST(lon AS CHAR) lon from {dataset}.airports order by iata")
        rows = query_job.result()
        return {
            'iata' : iata,
            'results': [{k: v for k, v in row.items()} for row in rows]
        }


@app.route(('/routes'))
def get_route():
    """
    GET route that returns airline routes based on source and destination
    """
    # get src and dest if provided and format a dict for queries
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


def create_table(table_name: str, columns: List[str]) -> str:
    """
    Function that takes a table name and list of columns and creates a table
    """
    # Format our SQL creation string
    create_sql = f"CREATE TABLE IF NOT EXISTS {dataset}.{table_name} ({', '.join(columns)})"
    logger.info(create_sql)

    # Use our engine to execute our table creation
    client = current_app.config['client']
    query_job = client.query(create_sql)
    query_job.result()

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
    drop_sql = f"DROP TABLE IF EXISTS {dataset}.{table_name}"
    logger.info(drop_sql)

    # Use our engine to execute our drop statment
    client = current_app.config['client']
    query_job = client.query(drop_sql)
    query_job.result()

    return f"Dropped {table_name}", 200


@app.route("/update", methods=["POST"])
def update_table():
    # Raise error if we did not get JSON input:
    if not request.is_json:
        return "No JSON supplied", 400

    # get the table name and make a DataFrame the posted data
    json_data = request.json
    table_name = json_data["name"]
    index = json_data["index"]
    df = DataFrame(json_data['data'])
    logger.info(df)

    client = current_app.config['client']
    # clears temporary table if it exists then write to temporary table
    tmp_table = 'tmp_merge'
    drop_statement = f"DROP TABLE IF EXISTS {dataset}.{tmp_table};"
    client.query(drop_statement).result()
    

    # write our data to the temp table
    df.to_gbq(f"{dataset}.{tmp_table}", project_id=project, if_exists='fail', chunksize=2000)

    # merge the data from the tmp table into the target table
    # for a merge statement we need to create a string with our SQL command
    # because we will be updating all columns, we use list comprehension to make
    # the following strings from our column names and insert them into our query
    update_cols = ",".join([f"{col} = tmp.{col}" for col in df.columns])
    insert_cols = ",".join(df.columns.to_list())
    value_cols = ",".join([f"tmp.{col}" for col in df.columns])

    merge_statement = f"""
    MERGE `{project}.{dataset}.{table_name}` AS target
    USING `{project}.{dataset}.{tmp_table}` AS tmp
    ON target.{index} = tmp.{index}
    WHEN MATCHED
    THEN
        UPDATE SET {update_cols}
    WHEN NOT MATCHED
    THEN
        INSERT ({insert_cols})
        VALUES ({value_cols});
    """

    logging.info(merge_statement)
    client.query(merge_statement).result()

    # drop temp table
    client.query(drop_statement).result()
    
    return f"Updated {table_name}", 200

if __name__ == "__main__":
    # run flask app on port 5000
    app.run('0.0.0.0', 5000)
```

In addition to this `main.py`, we need a couple more files, first of all is the `requirements.txt` containing all the python modules we used. Luckily, there is a copy of this at the chapter level, simply copy it to this directory. The last piece we need is a file called `app.yaml` which Google App Engine will use to configure our service.

## app.yaml
As we are running a relatively simple API, our `app.yaml` will consist of the following:

```yaml
runtime: python37

service: dsa-airspace

instance_class: B1

manual_scaling:
  instances: 1
```

To explain each one:
- `runtime: python37` tell App Engine ot use Python 3.7
- `service: dsa-airspace` gives our API a more specific name
- `instance_class: B1` tell App Engine to make a Basic 1 instance to keep costs down
- `manual_scaling`, `instances: 1` further tells app engine to make a single instance so as to keep costs down.

There are [many other parameters that can be set in our `app.yaml`](https://cloud.google.com/appengine/docs/standard/python3/config/appref) but these basic ones will suffice to get our api started.

With this file created, our directory, including our test JSON files we've been using will look like:

```txt
python
└── ex1
    ├── app.yaml
    ├── config.yml
    ├── main.py
    ├── new_airports.json
    ├── requirements.txt
    └── table.json
```

App Engine needs the `main.py`, `app.yaml`, and `requirements.txt` in place to deploy our API. It will include the other files so our local import of `config.yml` will still work.

## Deploy
The next step is to deploy our app. 
>Note: currently, once an app has be deployed on a project, it cannot be fully deleted. Our service `dsa-airspace` can be deleted but to avoid being charged, the app must be disabled or billing disabled as covered in the cleanup section below. It is important to note the before deploying though in case this may cause difficulties if you are using your project for multiple apps.

Deploying our app is quite easy! Just run the following in your `ex1` directory:

```bash
gcloud app deploy
```

and respond `Y` to the prompt if everything looks good. Part of the deployment message is the **target url**. Once your app is deployed, either navigate to this url in your browser, make a Postman GET request with no arguments, or `cURL` this url

```bash
curl https://dsa-airspace-dot-deb-01.wl.r.appspot.com
DSA Airspace
```

and we see our default text response! This means our API is up and running. Using Postman or `cURL`, test the functionality of your routes just like we did locally. For example, here is the GET request for routes from DEN to LGA:

![alt="screenshot of Postman GET request for routes from DEN to LGA showing the JSON resent with a few different airline's routes"](imgs/post-routes.png)


We can also monitor traffic to our API from the App Engine home page in the Cloud Console. Simply select `dsa-airspace` as the service in the drop down and you can see your traffic!

![alt="screenshot of the app engine home page showing a little traffic to dsa-airspace"](imgs/app.png)

We can also check the individual services we've deployed, monitor their logs, see their source code, etc from the **Services** option in the side bar.

![alt="screenshot of the services page with dsa-airspace selected"](imgs/services.png)

This view also takes us nicely into how to clean up our app

## Clean up
[As noted, there is no way to delete an app currently on GCP](https://cloud.google.com/appengine/docs/standard/python3/building-app/cleaning-up). As you can see in the above screenshot, you can select our `dsa-airspace` service and delete it making it inaccessible. However, your App Engine is still enabled and there are billing possibilities. The two choices for this are to delete the entire project or simply disable this app. If you want to continue using the same project for the course, disable they app using the Cloud Console by selecting **Settings** in the side bar and disabling the app:

![alt="screenshot of the settings tab with disable button"](imgs/disable.png)

You have now gone from learning what an API is all the way to hosting your own on Google Cloud!
