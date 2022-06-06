Here are more detailed steps on one way to organize input text into a word sequence frequency lookup. When you're trying to solve a complicated code challenge like the one here, it can be useful to first describe the steps needed the way you'd describe them to a friend.

1. Let's put this whole process into a function with no parameters, called `markov_dict()`

1. Within the `markov_dict()` function, assign an empty dictionary to a variable called `word_freqs`. Each key in this dictionary will be a word from our input text.

1. Still within `markov_dict()`, start a new block of code using `with open('sonnets.txt') as file_object:`

1. Within that block, we need a variable to hold the value of the last word we encountered. Let's call it `past_word`. Since our code hasn't gone through the loop yet, give `past_word` an initial value of an empty string.

1. Below that, we need to go through each line of the text 
    > hint: this is an excellent use for a `for` loop

1. For each word in that line:
    > hint: Python's [`.split()` method](https://docs.python.org/3/library/stdtypes.html#string-methods) could be useful here

    1. If `past_word` is already in the `word_freqs` dictionary, create a variable called `frequency` and assign `word_freqs[past_word]` (this is the dictionary the key in the outer dictionary already has as its value)

    1. Otherwise ("`else`"), create a variable called `frequency` assign an empty dictionary as its value.  Add a key-value pair to the `word_freqs` dictionary, with `past_word` as the key and `frequency` (the variable you just made holding an empty dictionary) as the value

    1. If the word you're on is already in the `frequency` dictionary, create a variable called `occurrances` and assign its value as the value of the current word in the `frequency` dictionary

    1. Otherwise ("`else`"), create a variable called `occurrances` and assign its value to 0

    1. Outside the last if/else block, add 1 to the value of the current word in the `frequency` dictionary

    1. Remember the variable `past_word` we made at the beginning of this block, to hold the value of the last word we encountered? Now that we've completed one round of this loop, set its value equal to the current word. 

    1. Once the function has looped over every word in every line, have it return the value of the `word_freqs` dictionary. Now it contains each word in your input data, followed by the frequency of the words that follow it!

<br>

For the sake of illustration, let's walk through the steps above with the simple input text as "the cup, the saucer".

#### Loop 1
- For the first iteration of this loop, `word_freqs` starts with an empty dictionary, and `past_word` starts with an empty string.
- `past_word` isn't already in `word_freqs`, so we assign it as a key, with an empty dictionary as its value:
- `word_freqs = {"": {}}`
- Since the word we're currenly looping over ("the") isn't already in the inner dictionary, we add it as a key, with 1 as its value:
-  `word_freqs = {"": {"the": 1}}`
- After the loop, we assign the word we're currently on as the new value of `past_word`:
- `past_word = "the"`

#### Loop 2
- Now `past_word` = "the", and we're looping over the word "cup"
- Since `past_word` isn't already a key in the `word_freqs` outer dictionary, so we assign it as a key, with an empty dictionary as its value:
-  `word_freqs = {"": {"the": 1}, "the": {}}`
- Since the word we're currenly looping over ("cup") isn't already a key in the "the" dictionary, we add it as a key, with 1 as its value:
-  `word_freqs = {"": {"the": 1}, "the": {"cup": 1}}`
- After the loop, we assign the word we're currently on as the new value of `past_word`:
- `past_word = "cup"`

#### Loop 3
- Now `past_word` = "cup", and we're looping over the word "the"
- Since `past_word` isn't already a key in the `word_freqs` outer dictionary, so we assign it as a key, with an empty dictionary as its value:
-  `word_freqs = {"": {"the": 1}, "the": {"cup": 1}, "cup": {}}`
- Since the word we're currenly looping over ("the") isn't already a key in the "cup" dictionary, we add it as a key, with 1 as its value:
-  `word_freqs = {"": {"the": 1}, "the": {"cup": 1}, "cup": {"the": 1}}`
- After the loop, we assign the word we're currently on as the new value of `past_word`:
- `past_word = "the"`

#### Loop 4
- Now `past_word` = "the", and we're looping over the word "saucer"
- Since `past_word` _is_ already a key in the `word_freqs` outer dictionary, we don't need to give it a new value
-  `word_freqs = {"": {"the": 1}, "the": {"cup": 1}, "cup": {"the": 1}}`
- Since the word we're currenly looping over ("saucer") isn't already a key in the "the" dictionary, we add it as a key, with 1 as its value:
-  `word_freqs = {"": {"the": 1}, "the": {"cup": 1, "the": 1}, "cup": {"the": 1}}`
- After the loop, we assign the word we're currently on as the new value of `past_word`:
- `past_word = "saucer"`


...and now that our function has looped over every word in our input, it returns `word_freqs`. When there's more input and more repetition, the values start to increase from 1, according to how often one word follows another.

<br>

#### Exercise
The walk-through above mimics the VS Code debugger. While you're writing the code for a word frequency dictionary, run the debugger with break points that will allow you to inspect the state of the variables as you loop through the input text, and watch those variable change in the debugger sidebar. If you need a refresher about debugging, revisit the lesson in [ch1/ep4](https://github.com/datastackacademy/data-engineering-bootcamp/tree/main/deb/ch1/ep4).