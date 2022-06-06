from datetime import datetime
from flask import Flask, request


# Create our Flask app
app = Flask(__name__)


# Create our function with the @app.route() decorator which specifies the endpoint that will call our function
@app.route("/")
def time_check():
    """
    Simple function that returns the time. Can accept a format string.
    Returns a raw sting unless the header specifies JSON
    """
    # We can access the request args via flask.request.args. We get() the desired format and specify a default if the arg is not provider
    date_format = request.args.get("format", default="%A %B %d, %Y")
    
    cur_day =  datetime.now().strftime(format=date_format)
    # The request headers are accessible through flask.request.headers. We use .get() to see if it only accepts JSON
    if request.headers.get('Accept', default=None) == 'application/json':
        # return a dict which flask interprets as json
        # in this case, the client gets back a json payload (body)
        return {
            'date': cur_day
        }
    else:
        # in this case, the client gets back just a text payload (body) just like console print
        return cur_day


if __name__ == "__main__":
    # run flask app on port 5050
    app.run('0.0.0.0', 5050)