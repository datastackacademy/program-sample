# Vehicles Pipeline

Today's lesson is only an exercise to create an end-to-end data pipeline to ingest a series of vehicle registration records. The goal is use your knowledge of the previous lesson to create this pipeline. You are given very limited instructions to simulate a real world project, working as a data engineer.

The vehicle records are included in our source file: _`data/vehicles\_complex.json`_

This is a JSON Row file where each line contains a vehicle registration information.

Let's assume that you have been hired by the Department of Motor Vehicles (DMV) as their brand new Junior Data Engineer. Your first assignment would be to process this file and apply a series of transformation rules to prepare it for ingestion into their main database. You are given a series of requirements by your manager (below). We are sorry! These instructions are intentionally left a little vague.

## The Assignment

You are given the following requirements by your manger in an email. Of course, you want to make a great first impression at the DMV 😀 Make sure your code meets all these:

1. Separate the good and bad records into two separate files. The records we receive from the field always has issues. Try the following...
2. Reject any rows that does not meet any of the requirements below:
   1. missing any of the following fields: _license plate, make and model, year, registered name, date or address_
   2. Make sure any of the above fields don't include Nulls. 
   3. **BUT** if you're missing the registered name and you do have sales records, you can use the name with the most recent sale date and use that as the registered name. You don't reject the row in this case.
   4. Make sure all the addresses are valid. Reject them if they are empty or invalid.
3. Apply the following transformations:
   1. Break down the addresses into _street address, city, state, zip_
   2. Break down the _make\_model_ field into two separate fields
   3. Add two new fields called _original\_sale\_price_ and _original\_sale\_date_ from the oldest sales record
   4. If you are missing sales records, it means this is the original/current owner. Add a sale record for this row. Set the previous owner to Null, use the registered name as new owner, set sale date to today's date and sale price to -$1.00.
   5. Set any Null colors to "N/A"
4. Create a JSON Row file with all the rejects and the reason for why they contained bad registration information
5. Create a JSON Row file with all passing records

**Bonus:**
Sometimes we have a gap in the sales records; meaning one of the new owner fields doesn't match the previous owner. See if you can write these rows into a separate file.

**Double Bonus!**
Create two CSV files with containing the good records:
- Create a flattened vehicle registration CSV file excluding the hierarchal sales records
- Create a separate vehicle sales CSV file including a row for each sale of the vehicle and its license plate. This means that if a vehicle has 3 sale records, there will be 3 separate CSV lines. This file would have the following fields: license plate, new owner, previous owner, sale date, and sale price.

## Acceptance Criteria
- You should submit either a notebook or `.py` module
- Create a separate git repo for this project
- Submit a requirements.txt, README.md, and .gitignore file with your repo
- Document your code thoroughly
