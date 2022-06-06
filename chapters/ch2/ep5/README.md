# Markov Chains

One major application of big data is to use data about the past to make predictions about the future; based on the patterns of what's happened before, you can guess what's likely to happen next. The more data you have, the more accurate your guesses can be. [Predictive analytics](https://en.wikipedia.org/wiki/Predictive_analytics) are used in every field that can gather a lot of data, like healthcare, professional sports, and economics. While this falls more often to data analysts than data engineers, it's still useful for data engineers to understand the ways in which data is consumed, so data can best be organized and cleaned for end use.

A Markov chain is one kind of predictive model that guesses the next event based on the current event. Markov chains are used by cell phones, for instance, to guess which word you're going to type into a text next. Here's how it works: each time a word is encountered, the Markov chain keeps a tally of how often different words follow it. For example, let's say you sent the following four texts:
- "good morning"
- "good gracious"
- "good morning"
- "good job"

We see that the word 'good' was followed by 'morning' twice, by 'gracious' once, and by 'job' once. How can we organize this information for use in a Markov chain? One way is with nested dictionaries, like this:
```python
{current_word1: {following_word1: num_of_times, following_word2: num_of_times, following_word3: num_of_times}}
```
...in our example, it would look like:
```python
{'good': {'morning': 2, 'gracious': 1, 'job':1}}
```
What if we then sent another text, reading "good morning, sunshine"? Now we have 'good' followed by 'morning' another time, and 'morning' followed by 'sunshine' once. So now our nested dictionary looks like this:
```python
{'good': {'morning': 3, 'gracious': 1, 'job':1}, 'morning':{'sunshine': 1}}
```
To summarize:
- The outer dictionary contains each word from the input text as a key, followed by an inner dictionary as a value
- Each inner dictionary contains as keys the words that can follow each key in the outer dictionary, with the number of times they actually follow that word as the value

In this challenge, we'll take some Shakespeare sonnets as our input data, organize our data by the frequency with which one word follows any other, and then use those frequencies to generate a new Shakespeare-sounding text. It'll be gibberish, but could pass as something spoken by a person. Here's an example:

"Summer on to hideous winter, and she in thy husbandry? Or ten of thy glass, and tell the tyrants to breed another thee, or ten times refigured thee: then what could death do if thou some vial; treasure thou art, if ten times happier, be death’s conquest and she so fond will be the tillage of glass"

<br>

### Step 1: Cleaning the Data

- Check out your input data and make sure it has the kind of values you want (in this case, the words of the sonnets). If there's anything in there you don't want, write some code to clean it up. 

- The same word will be treated as two different words if there are differences in capitalization or punctuation. Decide if you want to keep it that way or to make the input data more uniform (for instance by stripping the punctuation and making all words lowercase.) You can do this before any other code is run, or do it within the dictionary-making code, to avoid looping over all the text twice.

### Step 2: Creating A Nested Dictionary From Input Data

- For the first stage of this challenge, use the `with open(<FILE_NAME>) as <FILE_OBJECT>` to open the input file `sonnets.txt`.

- Go through each word of the input text and make it the key in a dictionary. For each of those keys, assign as a value a dictionary containing the words following it as keys, with frequency as values. It'll look something like this:
```python
{'': {'Those': 1}, 'Those': {'hours,': 1}, 'hours,': {'that': 1}, 'that': {'with': 3, 'unfair': 1, 'pay': 1, 'face': 1, 'my': 2, 'which': 1, 'thou': 3, 'bosom': 1, 'beauteous': 2, 'I': 1}, 'with': {'gentle': 3, 'frost,': 1, 'beauty': 1, 'winter': 1, 'thee.': 1, 'thyself': 1, 'thee,': 1, 'toil,': 1, 'travel': 1, 'sweets': 3, 'pleasure': 1, 'murderous': 1} ...
# etc.
```
If you want to try this step on your own, go for it! If you'd like some more detailed instructions, see `input_to_nested_dict.md`.


### Step 3: Weighted Probabilities

We can see in our above example that the word "good" is three times more likely to be followed by "morning" than by "gracious" or "job". So if we're trying to create an output that mimics the pattern of the input data, we want "morning" to follow "good" three-fifths of the time, "gracious" to follow it one-fifth of the time, and "job" to follow it one-fifth of the time. We want the choice to be random, but weighted in favor of the more common outcomes.

You can think of it as similar to making a program that predicts future weather patterns based on past weather pattern data. We know from experience that a warm, sunny day is most likely to be followed by another warm, sunny day, but it _could_ sometimes be followed by a cold, rainy day. There are predictable patterns, and within those patterns, randomness. This makes the output data more realistic, and keeps it from getting stuck in a single state.

Python has a built-in [`random`](https://docs.python.org/3/library/random.html) module that can pick random numbers within a given range, or a random value from a sequence (like a list) of values. The Numpy library also has a [`random`](https://numpy.org/doc/stable/reference/random/index.html) module that includes some bonus functionality useful for more sophisticated math and science applications. Whichever you use, remember to import it at the top of the script.

> Sidebar: Generating truly random sequences is harder than it might seen, and Python's `random()` actually generates pseudo-random numbers, whose pattern can be discerned. For cryptographically strong random numbers that would be safe for passwords, account authentication, or security tokens, use Python's [secrets module](https://docs.python.org/3/library/secrets.html)

A few options for using the values in your Markov frequency dictionary to choose, using weighted probability, a key in that dictionary:

1. Calculate what percent of the time a word appears in the frequency dictionary (its value divided by the sum of the values), and use these as the arguments for probability values in `random.choices()` or `numpy.random.choice()`

1. Or, use this weighted probability algorithm outlined in the `weighted_prob_algorithm.md` file.

1. Or, come up with your own solution! 


### Step 4: Writing the Output

The hard part's done; now you just need to piece together to functions you wrote above so that each word chosen by your weighted probability function is concatenated to the word chosen before it. A few other things to consider for your program:

1. The first word in your output will have to be selected at random, so there's somewhere to start.

1. To clean up your output, try writing a function that capitalizes a word if it's the first word a sentence, and makes other words lowercase.