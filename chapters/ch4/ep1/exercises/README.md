# Daily Exercises: Intro to APIs

Today's exercises focus on making sure that you feel comfortable accessing and retrieving data from an external API. For this purpose, we will use the [Spotify Web API](https://developer.spotify.com/documentation/web-api/reference/#/).

The goal is to connect to the Spotify API, GET some new data, and prepare and merge this data into our existing Spotify dataset. You can download the Spotify csv files using the `data/get_data.sh` script.

1. Set up access and authentication to the Spotify API (we walked through this in lecture, but here are the details again)
    1. If you do not have free a [Spotify](www.spotify.com) account, set one up.
    1. Take a few minutes to review the [Web API Basics](https://developer.spotify.com/documentation/web-api/), which will familiarize you with how to properly form requests, and how the API will handle them.
    1. Ensure that you have [authentication set up](https://developer.spotify.com/documentation/general/guides/authorization-guide/) so you can access the API.

2. Load the spotify artist data from its csv file. ou can download the Spotify csv files using the `data/get_data.sh` script. 

3. Now that you have access to the API, use it to get some data:
    1. Use a [GET Artist](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-an-artist) request to retrieve a few new artists. For this, you will need some Artist IDs - there are two ways to get some:
        1. Use search feature in the [web player](https://open.spotify.com/search) to find some of your favorite artists, and copy the Artist ID from the **URL** of the artist page
        2. (Bonus challenge): use the ['search for item' API endpoint](https://developer.spotify.com/documentation/web-api/reference/#/operations/search) (with Postman) to search for artists and retrieve a list of IDs from the API
    2. Check each artist to ensure that they are not already present in the artists table (you might do this by looping through the list of Artist IDs you just retrieved and using Pandas conditional selection or simply using the `in df.column` syntax
    3. Add the new artists to the artists DataFrame (you could do this a row at a time with `append()` or all at once with `concatenate()`; think about why the latter might be a better option when working with a lot of data)

4. Time permitting, let's also do something similar for albums and tracks

5. Write the updated data to CSV file(s)