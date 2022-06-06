
import sys
import logging
import pandas as pd
from flask import Flask, request


# setup python logger: log into console at INFO level
logging.basicConfig(format='[%(levelname)-5s][%(asctime)s][%(module)s:%(lineno)04d] : %(message)s',
                    level=logging.INFO,
                    stream=sys.stderr)
logger: logging.Logger = logging


# our mock dataframe database
INITIAL_DATA = [
    {"name": "Megan", "job": "Community Education Officer", "age": 24},
    {"name": "Christopher", "job": "Translator", "age": 37},
    {"name": "Linda", "job": "Illustrator", "age": 69},
]
# dataframe database
people_df = pd.DataFrame(INITIAL_DATA)
# set the name as index but keep the column
people_df.set_index(keys="name", drop=False, inplace=True)

# create the app and set the database
app = Flask(__name__)
app.config["db"] = people_df



# CRUD READ METHOD ---
@app.route("/people", methods=["GET"])
def read():
    """
    HTTP GET: Query for a person by name
    """
    # get the mock db from flask cache
    global people_df
    # get the URL params
    name = request.args.get("name", default=None)
    logger.info(f"query for {name}")
    # narrow down results by the name provided; otherwise return the entire dataframe
    # result_df = df[df["name"] == name] if (name is not None) else df
    if name is not None:
        result_df = people_df.loc[people_df["name"] == name]
    else:
        result_df = people_df
    # create the response json
    #   - remember: to_dict() dataframe method with orient=records return a list of dicts
    #   - see documentation: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_dict.html
    resp_json = {
        "query_name": name,
        "result": result_df.to_dict(orient="records"),
    }
    # response headers
    resp_headers = {
        "content-type": "application/json",
    }
    # return
    return resp_json, 200, resp_headers



# CRUD CREATE METHOD ---
@app.route("/people", methods=["POST"])
def create():
    """
    HTTP POST: add a new person to the database
    """
    # get the mock db from flask cache
    global people_df
    try:
        # placeholders to return what we did at the end
        inserted_people = []   
        rejected_people = []

        # iterate through the request json 
        # remember:
        #   - incoming data is a list of person dicts
        #   - check to see if the new person has all the required columns
        data = request.json
        for person in data:
            # check to see if this person has the required columns
            if ("name" in person) and ("job" in person) and ("age" in person):
                logger.info(f"adding new person: {person}")
                # create a new index for this person and use .loc[] to append a new row
                index = person["name"]
                people_df.loc[person["name"]] = person
                # add the person to our return list
                inserted_people.append(person)
            else:
                # add the person to our rejected list
                rejected_people.append(person)
        logger.info(f"inserted {len(inserted_people)} and rejected {len(rejected_people)}")
        # generate the response
        resp_json = {
            "records_inserted" : len(inserted_people),
            "result": inserted_people,
            "rejects": rejected_people,
        }
        # response headers
        resp_headers = {
            "content-type": "application/json",
        }
        # return ok status
        return resp_json, 200, resp_headers
    except Exception as err:
        # return error status if something went wrong
        return {"status": "error", "error_msg": str(err)}, 400, {"content-type": "application/json"}



# CRUD UPDATE METHOD ---
@app.route("/people", methods=["PATCH"])
def update():
    """
    HTTP PATCH: update a person in the database
    """
    # get the mock db from flask cache
    global people_df
    try:
        # placeholders to return what we did at the end
        updated_people = []
        rejected_people = []
        # iterate through the request json 
        data = request.json
        for person in data:
            # check to see if this person has the name column
            if "name" in person:
                logger.info(f"updating person: {person}")
                # update our df using the index and .loc[]
                index = person["name"]
                people_df.loc[index] = person
                # add to our list of updated people
                updated_people.append(person)
            else:
                rejected_people.append(person)
        logger.info(f"updated {len(updated_people)} and rejected {len(updated_people)}")
        # generate the response
        resp_json = {
            "records_updated" : len(updated_people),
            "result": updated_people,
            "rejects": rejected_people,
        }
        # response headers
        resp_headers = {
            "content-type": "application/json",
        }
        # return ok status
        return resp_json, 200, resp_headers
    except Exception as err:
        # return error status if something went wrong
        return {"status": "error", "error_msg": str(err)}, 400, {"content-type": "application/json"}



# CRUD DELETE METHOD ---
@app.route("/people", methods=["DELETE"])
def delete():
    """
    HTTP DELETE: delete a person from the database
    """
    # get the mock db from flask cache
    global people_df
    try:
        # keep track of deleted indexes
        deleted_indexes = []
        # iterate through the request json 
        data = request.json
        for person in data:
            # check to see if this person has the name column
            if "name" in person:
                logger.info(f"deleting person: {person['name']}")
                # delete using the index
                index = person["name"]
                people_df.drop(index=index, inplace=True, errors="ignore")
                # add to our delete list
                deleted_indexes.append(index)
        # people_df = people_df.drop(index=del_indexes, errors="ignore")
        logger.info(f"deleted {len(deleted_indexes)}")
        # generate the response
        resp_json = {
            "records_deleted" : len(deleted_indexes),
            "results": deleted_indexes,
        }
        # response headers
        resp_headers = {
            "content-type": "application/json",
        }
        # return ok status
        return resp_json, 200, resp_headers
    except Exception as err:
        # return error status if something went wrong
        return {"status": "error", "error_msg": str(err)}, 400, {"content-type": "application/json"}



# run the app
if __name__ == '__main__':
    app.run('0.0.0.0', 5050)
