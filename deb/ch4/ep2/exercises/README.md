# Daily Exercises

Today we have already looked at filling out our API with route and airport data. For this exercise, we are going to continue that process with the rest of our flights tables (airlines and aircraft). The MariaDB container in this lesson has the following tables: _routes, airports, aircraft, airlines_. This exercise will use that same Docker container and will further build APIs to access the _airlines_ and _aircrafts_ tables.

1. Make sure you to start the MariaDB instance using the `db_start.sh` script. Query the _airlines_ and _aircrafts_ tables to inspect their content.

1. Add a route for aircraft (`/aircraft`) to your API which accepts a GET request. This route should accept the following optional parameter: `aircraft_id`. If this parameter is omitted from the request, then the API should return the top 100 aircraft in our database. Do **NOT** return all the aircraft, there's just too many in our database for our API to handle.

4. Add a route for airlines which also accepts a GET request and the following optional parameters:
    2. `iata` (exact match)
    3. `country` (partial match)
    4. The API should return the exact airline if the _iata_ parameter is defined. Otherwise, return all airlines where the country starts with the value provided (hint: you should use the SQL _LIKE_ clause to get all the airlines starting with the country value)

5. Use both Postman and cURL to test submitting requests on both routes with different combinations of parameters to ensure that your API is working as required.