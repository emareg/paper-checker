
# Simple Paper Checker
This python script finds simple grammar mistakes in scientific english texts. Unlike other grammar checkers it is free and tailored for scientific texts, such as papers. It might find words that pass a spell check but are most likely not be intended in a scientific context. For example: angel vs. angle

## Features


### Reliable (almost no false positives/negatives)

* detection of of doubled words
* detection misuse of "a" or "an"
* numbers below 12 are written as digits


### Working (few false positives, maybe many false negatives)
* misused plural (e.g. “a cars”)
* wrong person-verb combination (e.g. “This were”)
* wrong words in scientific context (e.g. “angle” vs. “angel”)
* misuse of “then” vs. “than”
* missing commas 
* doubled auxilary verbs (e.g. “is are”)
* non explained acronyms


### Experimental
* improve less formal/scientific words (e.g. “entire” instead of “whole”)



## Usage
```
python3 paper-check.py YOURFILE 
```


## Feature Wishlist
* wrong passive/perfect (“to shown”)
* LaTeX improvements



