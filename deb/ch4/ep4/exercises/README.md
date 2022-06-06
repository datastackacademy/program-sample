# Daily Exercises

## Exercise #1: Hello World AppEngine Deploy

Create new app directory and develop a simple `Hello World` Flask app:

1. Add a simple index route to your Flask App
2. Return _anything_ you like!
3. Create a `.gcloudignore` and `requirements.txt` file for you app
4. Populate an `app.yaml` with your service configurations. You have two options here:
   1. Deploy your app with a different service name
   2. Or re-deploy using the _default_ service name which will overwrite your (amazing) Metallica app!
5. Deploy your app to AppEngine and test it using Postman
6. Do **NOT** forget to stop (or delete) the version that you just deployed

**NOTE**: practice stopping (or deleting) your apps after you are done developing them. You will run our of your Cloud credit if you forget to do this!

<br>

## Exercise #2: Aircraft AppEngine Route

Add another route to our service to query the _aircrafts_ table for a registered aircraft by its _n-number_ identification code.

- Return basic aircraft information such as: _registrant name, city, state, status, manufacturer name and model, speed, and thrust_
- Query BigQuery using parametrized SQL and return the results as JSON content-type
- Be sure to modify your `config.yml` and `app.yaml` files to contain correct information
- Test your app locally before publishing to AppEngine
- Deploy your app using `gcloud` and test it via Postman
- **Be sure** to **stop** and **delete** your app at the end
