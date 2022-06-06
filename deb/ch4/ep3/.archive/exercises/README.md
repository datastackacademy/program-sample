# Challenge Questions for Ch. 4, Ep. 3 - APIs

Today's exercises will use the Lego data to give you more practice in building APIs. We will be expanding on the Lego store kiosk database that you built for Chapter 3, Episode 2. Use the `start_db.sh` script or the VSCode extension to connect to the Docker container. Once you have initiated the database connection, do `use lego;` at the MySQL prompt to switch to the Lego database.

We will be applying what we have learned about APIs this week to make the views of the Lego tables available. And now that we know how to create POST routes, we will incorporate adding some new data to our existing dataset.

1. Create routes to GET info from the Lego database
    1. GET a part with a part ID
    1. GET a set with a set ID
    1. GET a list of the ten top-rated sets
    1. GET a list of the ten sets with the most parts
    1. GET all sets that include a provided search string in their name

1. Use what you learned in today's lesson to add a POST route to add a new set to the database.

1. Implement authentication so only authorized users can access the API.