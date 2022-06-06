"""
Process JSON Row profiles into an OK and Reject file.

Args:
    file_name: _description_
    print_lines: either true or false to print ok lines. 
"""

# imports
import sys
import re
import json
from json import JSONEncoder
from datetime import datetime
import shortuuid


# STAGES -------------------
#   0) read the file into json rows
#   1) add metadata columns


# get a unique ID for this ETL batch (script)
BATCH_ID = shortuuid.uuid()

def add_metadata(row:dict) -> None:
    """
    Adds ETL metadata columns to a row. Follwing metadata columns 
    are added:
        - modified_timestamp: current datetime
        - batch_id: unique ETL batch_id
        - tags: a key/value dict to store various data tags
        - tags.errors: a list of error message encountered while processing this row

    Args:
        row (dict): data row
    """
    global BATCH_ID
    now_utc = datetime.utcnow()
    # add timestamps for when we have processed this row
    row["modified_timestamp"] = now_utc
    # add the ETL (script) batch_id
    row["batch_id"] = BATCH_ID
    # a series of additional processing tags 
    row["tags"] = {
        # other tags can go here, for example:
        "security_level": "high",
        "allow_user_groups": ["admin",]
    }

# STAGES -------------------
#   0) read the file into json rows
#   1) add metadata columns
#   2) Data Quality checks:
#       - schema check
#       - null check


# define a set of required fields (or keys)
#   static variable (all caps) used as the default value in `schema_check()` function
REQUIRED_SCHEMA_FIELDS = {'uid','name', 'email', 'birthdate', 'credit_cards', 'address', 'gender', 'geo_location', 'modified_timestamp', }

def schema_check(row:dict, fields=REQUIRED_SCHEMA_FIELDS) -> bool:
    """
    Checks if all required fields (dict) are present in a dict or JSON row. Any 
    missing fields will cause a KeyError exception.

    Args:
        row (dict): data row
        fields (set, optional): set of required required fields. Defaults to NOT_NULL_FIELDS.

    Returns:
        bool: True if all fields (keys) are present

    Raises:
        KeyError: if any of the required fields (keys) are missing in row
    """ 
    # loop thru the required fields and make sure they are all present
    for field in fields:
        # if this field is missing in row, raise an exception
        if field not in row:
            raise KeyError(f"Missing required field: {field}")
    # return true if no exceptions
    return True


# default fields to check for null values
NOT_NULL_FIELDS = {'uid','name', 'email', 'birthdate', }

def null_check(row:dict, fields=NOT_NULL_FIELDS) -> bool:
    """
    Checks the row to NOT contain None values for any of the fields provided. 
    Any fields containing None would cause a ValueError exception.

    Args:
        row (dict): data row
        fields (set, optional): list of dict keys to check the value for. Defaults to NOT_NULL_FIELDS.

    Returns:
        bool: True if none of the fields contain None values

    Raises:
        ValueError: if a field contains None
    """    
    for field in fields:
        # check to see if the value of this field is None or null
        if row[field] is None:
            # add an error message to this row
            raise ValueError(f"{field} can NOT be None or null.")
    # otherwise return True
    return True


# STAGES -------------------
#   0) read the file into json rows
#   1) add metadata columns
#   2) Data Quality checks:
#       - schema check
#       - null check
#   5) transformatios:
#       - parse address into street_address, city, state, zip fields
#       - add a num_cards field


def transform_address(row:dict) -> bool:
    """
    Parses the address into street_address, city, state, zip fields. Invalid addresses 
    cause a ValueError exception.

    Args:
        row (dict): data row

    Returns:
        bool: True if address is in valid US address format; otherwise False

    Raises:
        ValueError: Unknown address format.
    """
    # regular expression (regex) to match a US address composed of street_address, city, state, zip
    #   - this regex uses Named Capturing Group feature of regex to assign a name to a matching portion of the string
    #   - the syntax is (?<group_name>...) where ... contains the matching regex for this group
    address_regex = r"(?P<street_address>[a-zA-Z0-9 .]+)\n(?P<city>[a-zA-Z0-9 ]+), (?P<state>[A-Z]{2}) (?P<zip>[0-9]{5})"
    pattern = re.compile(address_regex)
    # match address using regex
    result = pattern.match(row["address"])
    if result:
        # if a possible match found. assign fields based on regex matching named groups
        row["street_address"] = result.group("street_address")
        row["city"] = result.group("city")
        row["state"] = result.group("state")
        row["zip"] = result.group("zip")
        # delete the original address field
        del row["address"]
        return True
    else:
        # if address is not a match, raise an exception
        address = row["address"].strip().replace('\n', ', ')        # remove ENTER from the address
        raise ValueError(f"Unknown address format: {address}")


def add_num_cards(row:dict) -> None:
    """
    Adds a field call num_cards with the total number of credit cards in this row.

    Args:
        row (dict): data row.
    """
    if "credit_cards" in row and isinstance(row["credit_cards"], list):
        row["num_cards"] = len(row["credit_cards"])
    else:
        row["num_cards"] = 0




class DatetimeEncoder(JSONEncoder):
    """
    Custom JSON Encoder class to properly encode datetime fields. All other fields are encoded with 
    their default formatting. This class inherits the default json.JSONEncoder class.
    """

    def default(self, value):
        """Encodes values to JSON. Adds special formatting for datetime fields.

        Args:
            value (object): field to encode

        Returns:
            object: encoded json string
        """
        # check for datetime type
        if isinstance(value, datetime):
            # format the datetime string
            dtfmt = "%Y-%d-%m %H:%M:%S.%f %z"
            return datetime.strftime(value, dtfmt)
        # all other data types default to the JSONEncoder parent class formatting
        super(DatetimeEncoder, self).default(value)


def run(file_name:str, print_lines:bool=False) -> None:
    """
    Reads user profiles from a JSON row formated file.

    Args:
        file_name (str): file path to read
        print_lines (bool): print lines to console
    """
    # keep track or row counts
    line_num = 0            # total number of rows
    ok_count = 0            # number of rows without errors
    reject_count = 0        # number of rows with errors

    # prepare a ok & reject file
    # -------------------------------------
    # add a timestamp to files
    file_timestamp = datetime.utcnow().strftime("%Y%m%d")
    # get the file name without it's extension
    file_name_without_extension = file_name.rpartition('.')[0]      # from the right of the string, partition by '.' and take the first partition
    # create ok and reject file names inclusing the timestamp
    ok_file_name = f"{file_name_without_extension}_{file_timestamp}_ok.json"
    reject_file_name = f"{file_name_without_extension}_{file_timestamp}_reject.json"
    # open files for writing
    ok_file = open(ok_file_name, "w", encoding="utf-8")
    reject_file = open(reject_file_name, "w", encoding="utf-8")

    with open(file_name, "r") as json_file:
        for line in json_file:
            try:
                row = json.loads(line.strip())
                # checks & transformations
                add_metadata(row)
                schema_check(row)
                null_check(row)
                transform_address(row)
                add_num_cards(row)
                # write to ok file
                json.dump(row, ok_file, cls=DatetimeEncoder)     # write the json row
                ok_file.write("\n")         # write endline character

                if print_lines:
                    print(f"[{line_num:02d}][OK]: {row}")
                ok_count += 1
            except Exception as err:
                # add error and line number to the json row
                err_msg = f"[{line_num:02d}][ERR]: {str(err)}"
                row["error"] = err_msg
                # write the error line to reject file
                json.dump(row, reject_file, cls=DatetimeEncoder)
                reject_file.write('\n')
                print(err_msg, row)
                reject_count += 1
            finally:
                line_num += 1
    # print line count summary at the end
    print(f"Read {line_num} rows")
    print(f"OK rows: {ok_count:02d}, Rejected rows: {reject_count:02d}")
    # close files
    ok_file.close()
    reject_file.close()


def main():
    """
    The main execution method. Get command line args and call the `run()` method.
    """
    args = sys.argv     # command line arguments into our script
    if len(args) != 3:
        # print help
        help = "usage: python3.7 process_profiles.py file_name print_lines\nprint_lines can be 'yes' or 'no'"
        print(help)
        sys.exit(1)
    # get the command line args
    file_name = args[1]
    print_lines = str(args[2]).lower() in {'yes', 'true'}     # see if second argument is either true or yes, otherwise False
    # call our run method
    run(file_name, print_lines)


# call our main function to parse command line args
if __name__ == '__main__':
    main()
