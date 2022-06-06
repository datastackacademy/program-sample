import json
import sys
import logging
from flask import Flask, request


# setup logging and logger
logging.basicConfig(format='[%(levelname)-5s][%(asctime)s][%(module)s:%(lineno)04d] : %(message)s',
                    level=logging.INFO,
                    stream=sys.stderr)
logger: logging.Logger = logging

# Create our Flask app
app = Flask(__name__)


# Specify that our route supports GET and POST methods
@app.route("/", methods=["GET", "POST"])
def print_data():
    """
    Simple function that prints the supplied data
    """
    # If we receive a GET method, we want to respond saying how to use the POST method
    if request.method == "GET":
        return "Please send a POST message to this endpoint and we will print the supplied data", 200
    else:
        # Get the type of data from the headers if supplied
        data_type = str(request.headers.get("Content-Type", None)).lower()
        logger.info(f"Our Content-Type is: {data_type}")
        # response json result as a dict
        result = {"status": "success"}

        # If we got form data, print with nice formatting and return success
        if data_type.startswith("multipart/form-data"):
            # empty dict to hold input form data
            result["input_data"] = {}
            for key, val in dict(request.form).items():
                logger.info(f" form {key}: {val}")
                result["input_data"][key] = val
        # If we receive JSON data, print it and return success
        elif data_type == "application/json":
            json_data = request.json
            logger.info(json.dumps(json_data, indent=2))
            result["input_data"] = json_data
        
        # add the request length and send back the response
        logger.info(f"POSTed {len(request.data)} bytes")
        result["input_data_length"] = len(request.data)
        # send the response back as json
        return result, 200, {"Content-Type": "application/json"}


if __name__ == "__main__":
    # run flask app on port 5050
    app.run('0.0.0.0', 5050)