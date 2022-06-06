from datetime import datetime
from flask import Flask


# Create our Flask app
app = Flask(__name__)


# Create our function with the @app.route() decorator which specifies the endpoint that will call our function
@app.route("/")
def time_check():
    """
    Simple function that returns the time
    """
    return datetime.now().strftime(format="%A %B %d, %Y")
     

if __name__ == "__main__":
    # run flask app on port 5050
    app.run('0.0.0.0', 5050)