# Challenge questions for Ch. 4, Ep. 4

This exercise will give you more practice in building cloud APIs. In today's lesson, we looked at implementing a cloud version of the airline API we have been building. Today's exercise will do the same thing for the Lego API that we built in yesterday's exercises. We will follow the steps from today's lecture closely.

1. Replace the SQL Alchemy engine in your Lego database with BigQuery.
    1. Replace references to `conn.execute()` with `client.query()`, etc. 

1. Set up to host your API on GCP AppEngine
    1. Update the `main.py` file provided in today's lecture to work with your Lego database
    1. Copy the `requirements.txt` file, which is needed by AppEngine
    1. Create your app.yaml file

1. Deploy your API using `gcloud app deploy`. Troubleshoot any issues and ask for help if you need it.

1. Use Postman and/or cURL to verify that the routes in your Lego API are all working. Postman is easier to use, but it's good to know how to use cURL, so make sure that you test at least one of your routes that way.

1. After you have verified that your API is working completely, clean up after yourself by disabling the application in the GCP console, so that there is no possibility of unexpected billing to our account. 
