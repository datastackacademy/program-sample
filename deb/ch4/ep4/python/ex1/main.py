
from flask import Flask
import pandas as pd

app = Flask(__name__)


@app.route("/")
def index():
    # a few favorite metallica songs dataframe!
    df = pd.DataFrame([
        {"artist": "Metallica", "song": "Creeping Death", "album": "Ride The Lightning"},
        {"artist": "Metallica", "song": "Battery", "album": "Master Of Puppets"},
        {"artist": "Metallica", "song": "Fade To Black", "album": "Ride The Lightning"},
        {"artist": "Metallica", "song": "Orion", "album": "Master Of Puppets"},
    ])
    # convert the songs into a json dict and respond
    return {
        "metallica_songs": df.to_dict(orient='records')
    }, 200, {"content-type": "application-json"}


if __name__ == '__main__':
    app.run('0.0.0.0', 8080)
