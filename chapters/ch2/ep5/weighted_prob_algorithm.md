## Using Weighted Probability to Choose a Value in a Frequency Dictionary

1. Sum the values in the dictionary

1. Randomly select a number between 0 and that sum

1. For each key-value pair in the dictionary:
    1. If the random number minus the value is less than 0, return that key

    1. Otherwise, subtract the value from the random number, and start again at the top of the loop with that as the new random number

<br>

Let's walk through how this works, using the example dictionary from the `README.md` file:
```python
{'good': {'morning': 3, 'gracious': 1, 'job':1}}
```

- The sum of the values in the inner dictionary is 5

- A number between 0 and 5 is randomly selected. Let's say it's 4.

- The value for the first key ('morning') is 3. 4 - 3 = 1, so our loop continues.

- The value for the second key ('gracious') is 1. Using the output of the previous loop (1), we repeat the operation again: 1 - 1 = 0, but that's not less than 0, so our loop continues.

- The value for the third key is ('job') is 1. Using the output of the previous loop (0), we repeat again: 0 - 1 = -1. That's less than 0, so 'job' is the word we pick.

- Try this with every value between 0 and 5 (not inluding 5). You should get 'morning' 3 times, 'gracious' once, and 'job' once.