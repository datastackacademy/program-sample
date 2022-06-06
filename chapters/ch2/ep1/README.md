# Working With Files - part 1

## Intro

In this lesson you'll learn how to read and write to files in Python. 

Reading and writing to data files are one of the most fundamental skills as a data engineer. You're always working with files. Some common data engineering tasks are:
- Reading data files
- Checking the schema (or format) of each row
- Parsing rows of data and ensuring key fields are present and valid
- Transforming rows and fields to apply business logic or to validate their content with other reference sources
- Writing the output to a database or data file formats more suited for the Cloud or Big Data tools

Let's get started!

### Simple File I/O: Speaking to the Can! 

In this section you'll learn to write a simple message to a data file; open it and read the message back. This is what we call _"speaking to the can"_ where the can is the file that you will create.

Let's look at the most simple example to write a message to a file:


```python

with open("./data/can.txt", "w") as myfile:
    msg = "Only from the heart can you touch the sky. -Rumi"
    myfile.write(msg)

```

Let's digest our code:
- The Python's built-in `open()` method allows us to open a file for reading and writing
- This method returns a file object or commonly also called a _file handle_. We assign this file object to a variable called `myfile` in our code. You can name this object anything you like but the handle is a special object that allows you to do operation (such as read and write) to the file
- The `open()` method takes two required positional parameters. The first parameter is the file **path** while the second parameter is the **mode** for our file operation.
- In this example, we open the file with `w` for _write_ mode.
- There are other common modes such as `r` for _read_ mode or `a` for _append_ mode
- The `with` is a special Python convention commonly used when working with files. This statement allows us to write a code block (indented by a tab)
- The file handle `.write()` method write any content to the file

Simple, right?!

It's important to note that the `with` statement knows to automatically close our file when the code is ended (unintended back). It's very important to always close files after you're done working withing with them. Open file handles take up operating resources. Most operating systems have a finite limit on how many open file handles they can handle; so by not closing files you will risk reaching this limit. Additionally (most) operating systems lock a file when your program is using them; meaning that no other program can work with the same file until it's closed by your program.

Let's examine this:


```python
with open("./data/can.txt", "w") as myfile:
    msg = "Only from the heart can you touch the sky. -Rumi"
    myfile.write(msg)
    # pay attention that the file is still open inside the with block
    print("is file closed (inside with)? ", myfile.closed)

# outside of the with block, the file is closed
print("is file closed (outside with)? ", myfile.closed)

```

Now, let's open our file back in **read** mode and read back out content:


```python
with open("./data/can.txt", "r") as myfile:
    msg = myfile.read()
    print(msg)
```

You can see that now:
- We open the file in `r` or _read_ mode
- The file object `read()` method reads the entire content of the file (to the end) and returns the content
- We assign the content to a variable called `msg` and print it

**NOTE:** a few important points:
- Opening a file in `w` mode completely over writes its previous content. If you open a file and don't write anything, then you'll end up with an empty file.
- If you like to add content to a file then use `a` or _append_ mode


The `read()` method without an argument reads the entire file to the end. Since the file content is read into the memory, if you read a very large file it might cause your computer to run out of memory! Therefore its better practice to read files in certain chunks. You'll see more examples later using the `readline()` method. 

For now, let's look at another example where we only read certain number of characters from our file and close it:


```python
with open("./data/can.txt", "r") as myfile:
    # read 10 characters
    msg = myfile.read(10)
    print(f"read: '{msg}' len={len(msg)}")
    # read the next 9 characters
    msg = myfile.read(9)
    print(f"read: '{msg}' len={len(msg)}")
```

#### Exercise

- Open a file and write another Rumi quote
- Open the file again and read your quote


```python
# open the file for writing

# open the file for reading
```

### File Encoding

It's important to note another `open()` method parameter called `encoding`. A file encoding is how the computer encodes and decodes the text into binary format. At the end of the day everything in computers is binary. There are two very common file encoding formats called `utf-8` and `utf-16`. The _utf-8_ formatting refers to the ASCII standard 8bit encoding which covers most of latin characters. The _utf-16_ is a broader 16bit encoding which covers all other languages characters such as Farsi letters (the original language of the poet Rumi) or Chinese letters. You can refer to the [ASCII Table](https://www.asciitable.com/) to see how characters are encoded into binary numbers.

Let's see this in practice:


```python
with open("./data/can.txt", "w", encoding="utf-8") as myfile:
    msg = "Your heart knows the way. Run in that direction. -Rumi"
    myfile.write(msg)

print("file is written! Now reading:")
with open("./data/can.txt", "r", encoding="utf-8") as myfile:
    msg = myfile.read()
    print(msg)
```

**NOTE:** It's important to note that you should always open files in the same encoding format that they were originally written in; otherwise you'll get very funny looking characters or a `UnicodeError`. 

See the example below where we intentionally read/write with different encodings:


```python
# !!! this code will throw a UnicodeError since we are writing and reading with different encoding types !!!

with open("./data/can.txt", "w", encoding="utf-16") as myfile:
    msg = "Your heart knows the way. Run in that direction. -Rumi"
    myfile.write(msg)

print("file is written! Now reading:")
with open("./data/can.txt", "r", encoding="utf-8") as myfile:
    msg = myfile.read()
    print(msg)
```

#### Exercise

- Write and read to a file 5 times. Find whatever you want to read/write!
- Try doing special things like writing a message with endline characters: `"this is \n a multi line \n text"`


```python
# write your code here
```

### Resources

Additional reading:
- [Python Documentation: File I/O](https://docs.python.org/3/tutorial/inputoutput.html#tut-files)

<br/><br/>

## Reading/Writing Multiple lines

Thus far, we have been reading/writing only a single line to a file but data files often have multiple lines or _rows_ for data. In this lesson, we're going to cover the other file object methods that allow us to write with larger files.



### Generating Random Data

Before we get into reading & writing files, let's take a look at interesting pypi library called **[Faker](https://pypi.org/project/Faker/)**. This is a really handy library to generate random data. A lot of times as data engineers we need to generate random data to test our data pipelines and this library provides an extensive number of methods to generate all sort of data like people, vehicles, credit cards, and emails in multiple languages.

Go ahead and install this package on your _virtual environment_. This package is already installed via the `requirements.txt` file for this lesson, don't be surprised if nothing happens:


```python
%pip install Faker
```

**NOTE:** 

In Jupyter notebooks if you start a code cell with a percentage `%` or exclamation point `!`, the code cell is as a bash terminal instead of the default python kernel.

You can read the [documentation](https://faker.readthedocs.io/en/stable/index.html) for Faker to better understand how to use this module. Here's we're going to use a simple method called `.name()` to generate some random names:


```python
from faker import Faker

# create a fake class
fake = Faker()

# generate 10 names
for i in range(10):
    name = fake.name()      # this method return a random name
    print(name)
```

Please note that:
- We create a new `Faker()` object called `fake`
- This object provides extensive methods to generate fake data. One of these methods is called `.name()` to return random full names
- [Explore](https://faker.readthedocs.io/en/stable/index.html) the Faker module. There are many other methods such as `.email()` or `.phone_number()`
- You can even set up Faker to generate names or addresses from other countries by passing the locale argument when instantiating the class: `fake = Faker(locale=['it_IT', 'en-US'])`. Read the docs! This will generate fake data for both USA and Italy.

### Writing Multiple Lines

Now, let's try to write our randomly generated names into a file where each name is on a separate _row_:


```python
from faker import Faker

# create a fake class
fake = Faker()

# open the file as before
with open("./data/names.txt", "w", encoding="utf-16") as output_file:
    # loop to generate 10 names
    for i in range(10):
        name = fake.name()
        content = f"{name}\n"           # we must add an endline (ENTER) character to the end of our content
        output_file.write(content)      # write the content to file

print("done!")
```

Pay attention to some minor detail here:
- We open our file and create a file object (or handle) called `output_file`
- Since the `for` loop is inside our `with` block, the `.write()` method would be called 10 times resulting in writing 10 rows of names to our file
- Most _importantly_, we add an `\n` string literal (for ENTER) to the end of each line. You must write your own line terminators to the file. Enter or newline is commonly used as a _line terminator_ but other data formats could choose to have different terminators.

<br/>

It's important to see that we could also write multiple lines as once using the `writelines()` method of a file. The following code has the same results as before but now using the `writelines()` method instead:


```python

# open the file as before
with open("./data/names.txt", "w", encoding="utf-16") as output_file:
    # store multiple lines into a list
    lines = []
    # loop to generate 10 names
    for i in range(10):
        name = fake.name()
        content = f"{name}\n"       # we must add an endline (ENTER) character to the end of our content
        lines.append(content)       # append to our list of lines to write

    # outside of the for loop, write all the 10 lines at once
    output_file.writelines(lines)


print("done!")
```

Open the file and examine its content. Since the data is randomly generated, you should get a different content every time you write your file.

#### Exercise

- Using the [Faker module documentation](https://faker.readthedocs.io/en/stable/index.html), generate two other random pieces of information such as email or phone_number for each person. Do **NOT** use the `.address()` method since these addresses can include newline characters that separates the street_address from city, state, zip.
- Write the name and these additional information on each line separated by a comma. For example a single like might look like this: `Clayton Stephenson,vaughnjanet@example.org,+1-150-770-2326x20019`
- Be sure to write 30 rows
- You can use either `.write()` or `writelines()`
- **PLEASE** change your file name to something different


```python
# make a new Faker object

# open file and write 30 rows
```

#### Exercise

Do it again! This time you can write different lyrics of your favorite song into a file. Be sure to create a list with different lines of the song.


```python
# write out the lyrics for your favorite song
```

### Reading Multiple Lines

In this example, we're going to see how to read the same file containing our randomly generated names.

Python makes reading lines from a file extremely easy. You can loop over the file object itself to read its content line by line. Think of the file object as a _collection of lines_ (or list of lines).

Let's see this in action:


```python
# open our file for reading
with open("./data/names.txt", "r", encoding="utf-16") as input_file:
    for line in input_file:
        line = line.rstrip()
        print(line)
```

Let's digest this code quickly:
- You can see that by looping over our file object, we read individual lines from our file
- Python returns the line content **_including_** the terminating newline (\n) character
- We use the `str.rstrip()` method to remove the trailing newline character from our lines

**NOTE:** The file object return the line **_including_** the terminating newline (\n) character. To eliminate these, we can use the `str.rstrip()` method which remove trailing whitespace characters from the right of the string. 


#### Exercise

- Read the content of `/data/biggie_smalls_juicy.txt` line by line
- Extra points: try to do some fun stuff:
  - Count the number of lines
  - Count the number of words (hint: use `str` built-in methods to split a line into words)
  - Count the number of characters
  - Print the line number where Salt-n-pepa is mentioned


```python
# your code here

```

#### Exercise

TBD... Add 2pac's Changes file.

<br/>

#### Alternatively: Using the `readline()` method

It's important to note that you can also use the file object `readline()` or `readlines()` to read lines from a file. 

Let's see both these in action:


```python
# open our file for reading
with open("./data/names.txt", "r", encoding="utf-16") as input_file:
    line = input_file.readline()            # read the first line
    line_number = 1                         # keep track of line numbers
    while line:
        line = line.rstrip()                # drop the trailing newline
        print(f"{line_number}: {line}")
        line = input_file.readline()        # read the next line
        line_number += 1                    # incr. line number

```

    1: Tina Sparks
    2: Linda Cisneros
    3: April Stevens
    4: Spencer Crane
    5: Mrs. Jill Smith
    6: Patricia Jensen
    7: Stephanie Carr
    8: Joshua Perez DDS
    9: Tiffany Murray
    10: Tracey Adams


Let's take a closer look at our code:
- In this example, we use the `while` loop to read our file
- The `readline()` method returns an empty string when it reaches the end of the file. This allows us to check for empty string in our `while` condition. Remember, empty strings in Python always evaluate to the boolean value `False`
- The rest is simple, we continue reading the next line until we encounter the end.

#### Exercise

- Read back the same file that you generated earlier with multiple random fields per person
- Split your lines by `,` to get back the original fields


```python
# enter your code here
```

<br/><br/>

## Working with CSVs

### CSV Overview

CSVs are the simplest and the most commonly used data format. CSV stands for _Comma Separated Values_. CSVs contain rows of data where each line is _terminated_ by a newline character (`\n`) and columns within a row are _delimited_ (or _separated_) by commas (`,`). You might be familiar with this format from working with Excel files. CSVs are commonly used by Excel to import/export data.

You can see that commas and newline characters are special characters; therefore if a field contains these characters, it needs to be wrapped by another special character called the _Enclosing Character_. This is typically set by double quotes (`"`). For example to following line represents 3 fields: _name, home\_town, genre_ where the address field is wrapped in quotes to include a comma:

```text
name,home_town,genre
Biggie Smalls,"Brooklyn, NY",hip hop
```

Optionally, to be safe, all string or text fields could be wrapped in quotes.

There's another special character called the _Escape Character_; commonly set as backslash (`\`). This character is used to escape the _Enclose_ character; allowing a text field to include a quote. Yes, we almost get into an endless cycle! If we need a single backslash in the text, we should enter double backslashes: '\\'. Take a look at the example below. This example contains a lyric field that includes both a quote and backslash:

```text
name,lyric
Biggie Smalls, "The song Juicy includes: \"Salt-n-Pepa \\ Heavy D up in the limousine\" -the end"
```

Luckily, you don't have to worry about these as much. Python automatically takes care of escaping or enclosing fields. Just know that there are these special characters which you can change:

| Name | Default Character |
| --- | --- |
| Delimiter | `,` (comma) |
| Line Terminator | `\n` (enter or newline) |
| Enclosing or Quoting | `"` (double quote) |
| Escape | `\` (backslash) |

It's important to mention that there's another similar file type called TSV or _Tab Separated Values_ where fields are terminated by tabs (`\t`).

### Basic CSV I/O

In this lesson we'll follow some simple examples to read/write CSV rows from a file. 

Python provides a built-in `csv` module. This module comes equipped with a `DictWriter` and a `DictReader` class to write/read CSV files. These classes automatically take care of CSV formatting including adding delimiters, parsing fields, and escaping special characters. Life is easy with Python 😉

Let's see these classes in action. The following code writes a series of rows from a list into CSV format:


```python
from csv import DictWriter


# csv header fields
header = ["name", "home_town"]
# rows to write, each row includes a dict of values
rows = [
    {"name": "Biggie Smalls", "home_town": "Brooklyn, NY"},
    {"name": "Queen Latifah", "home_town": "Newark, NJ"},
    {"name": "Salt-N-Pepa", "home_town": "Queens, NY"},
    {"name": "Tupac Shakur", "home_town": "Harlem, NY"},
]

# open a file for writing
with open("./data/hiphop_legends.csv", "w") as csv_file:
    # create a csv writer with header fields
    csv_writer = DictWriter(csv_file, fieldnames=header, dialect="unix")
    # write our header row
    csv_writer.writeheader()
    # iterate through rows and write to file
    for row in rows:
        csv_writer.writerow(row)

print("done!")
```

Let's take a closer look here:
- We open a file for writing as before
- We use a spacial `csv` module class called `DictWriter`. This class writes dicts into CSV format. The dict fields map one-to-one to the CSV fields written.
- `DictWriter` take a list of `fieldnames`. This is the list of dict keys to write into the file; and is also used for the CSV header column names.
- The `dialect=unix` indicates Unix formatting which includes a single newline (`\n`) character as the line terminator. You also use the `excel` dialect to include Windows newline terminators. Yes, Unix and Windows have different line terminators. This is typically very annoying!
- The `writerow()` method write a dict to our file in CSV format

<br/>

Now, let's read our rows back using a similar `csv` module class called `DictReader`:


```python
from csv import DictReader


# open our file for reading
with open("./data/hiphop_legends.csv", "r") as csv_file:
    # create a csv reader and pass any special args
    csv_reader = DictReader(csv_file, dialect="unix")
    for row in csv_reader:
        # get the current line number
        line_num = csv_reader.line_num
        # access fields as a dict
        name = row["name"]
        home_town = row["home_town"]
        print(f"lineno: {csv_reader.line_num} - name: {name} home_town: {home_town}")
```

It's important to note that:
- `DictReader` automatically detects if our file includes a header row. This row is used as field names and sets the keys for the parsed dict rows. Pay attention that this row is skipped as a data row. Therefore, printing the line numbers starts from the second line of the CSV file.
- You can use the `DictReader` object itself as an iterator. Iterating over this object returns a dict object corresponding to each row of the CSV file.
- The `DictReader` takes a series of optional constructor parameters such as `dialect`. Read the docs! There are other parameters to change the delimiter, quoting character, or other CSV special characters.
- The `DictReader` returns an `OrderedDict` object. This is a special dict object which retains the keys in the same order in which they were entered.


### Reading/Writing Lists

The built-in `csv` module has two other classes to work with CSV files which that do NOT contain a header row. These classes read/write the fields into a `list` object instead of a `dict`. These classes are simply called `csv.writer` and `csv.reader`. You can read the docs to familiarize yourself with them. 

The example below shows how to work with there classes:


```python
import csv

# our rows are defined as list of values (instead of dicts)
rows = [
    ['Biggie Smalls', 'Brooklyn, NY'], 
    ['Queen Latifah', 'Newark, NJ'], 
    ['Salt-N-Pepa', 'Queens, NY'], 
    ['Tupac Shakur', 'Harlem, NY']
]

# write data to csv
with open("./data/hiphop_legends.tsv", "w") as csv_file:
    # we change our delimiter to tabs and only use enclosing characters when necessary
    csv_writer = csv.writer(csv_file, dialect="unix", delimiter="\t", quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerows(rows)

print("done writing!")

# open and the file back for reading
with open("./data/hiphop_legends.tsv", "r") as csv_file:
    csv_reader = csv.reader(csv_file, dialect="unix", delimiter="\t", quoting=csv.QUOTE_MINIMAL)
    for row in csv_reader:
        # we read back lists (instead of dicts)
        print(row)

```

A few things to notice here:
- Our rows are now a list of lists
- We also pass a few more parameters to change the delimiter to tabs (making this a TSV file) and set the quoting to only when necessary (minimal)

#### Exercise

- Read the file `./data/deb-routes.csv` using the `csv.DictReader`
- Print each the fields in each row
- Store each row into a list
- Open another file for writing using the `csv.DictWriter`
- Store the rows back into CSV format


```python
# import both DictReader and DictWriter

# declare a list to store your rows

# open the file for reading using DictReader
# loop throw all the rows and append them to your list


# open the a file for writing using DictWriter
# loops through your list and write them into csv

```

### Generating Random Person Profile

Before we get into reading/writing CSV files, let's use the Faker module to generate a series of random person profiles. We use various methods for the `Faker` class to generate random people. We save each person in a corresponding dict.

Let's see this in action:


```python
from faker import Faker

fake = Faker()

# a list to contain our profiles
profiles = []

for i in range(30):
    person = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "street_address": fake.street_address(),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "zip": fake.zipcode_in_state(),
        "email": fake.free_email(),
        "birth_date": fake.date_of_birth(),
    }
    print(person)
    profiles.append(person)
```

#### Exercise (Writer)

1. Write the profiles into a CSV file using the `DictWriter` class
2. Be sure to include a header row


```python

# get our field names from the data
field_names = list(profiles[0].keys())

# write profiles into a CSV file

```

#### Exercise (Reader)

1. Read the profiles back from using the `DictReader`
2. Print a few of the fields
3. **Bonus**: When reading each row, add some post processing to parse the _birth\_date_ column as datetime objects

#### Exercise - Bonus Points

1. Write and read the profiles again but this time with the `csv.reader` and `csv.writer` classes instead.
2. Remember, these classes work with rows as a `list` of fields instead of a `dict`. You must use the profile `dict.values`.
3. Set the delimiter character to tabs (`'\t'`); making this a TSV file. Read the docs to find the correct parameter to set.


```python
# write the profiles into a TSV file

# read teh profiles from a TSV file
```
