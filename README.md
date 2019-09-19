
# PaperCheck

PaperCheck is a python script that searches for simple grammar mistakes in scientific english texts. Unlike other grammar checkers it is free and tailored for scientific texts, such as papers. It might find words that pass a spell check but are most likely not be intended in a scientific context, such as "angel" vs. "angle".


## Getting Started

```
git clone git@github.com:emareg/paper-checker.git
cd paper-checker
```

Afterwards you can use the script in two ways:

**1. Run the python file**
```
python3 papercheck.py -gs example/testfile.tex
```

**2. Compile as an stand-alone executable (Unix only)**
```
make
./papercheck -gs example/testfile.tex
```

Supported file types: `.tex .txt .md .pdf`

The found issues are displayed in the terminal and also written into `papercheck_report.html`



## Features

### Grammar Checker (`-g` option)
Will highlight simple grammar mistakes such as

* misuse of “a” or “an”
* doubled auxilary verbs (e.g. “is are”)
* doubled determiners verbs (e.g. “this the”)
* confused “then” vs. “than”
* confused “to” vs. “too”
* wrong person-verb combination (e.g. “This were”)



### Style Checker (`-s` option)
Will highlight language that could be improved such as


* wrong words in scientific context (e.g. “angle” vs. “angel”)
* non explained acronyms
* improve less formal words (e.g. use “entire” instead of “whole”)
<!-- * numbers below 12 are written as digits -->


### Plagiarism Checker (`-p` option)
**experimental!**

Will find significant sentences and compare them to google search matches. This is a very poor approach but useful as a minimal effort with zero cost.



### TeX checker
When you run the script on `.tex` files, it will also check for certain TeX problems such as

* unused labels
* missing periods in figure/table captions
* unused math operators in math mode, e.g. `$sin$` instead of `$\sin$` 


## Related Work

* [LanguageTool](https://languagetool.org/): Grammar, Style and Spell Checker written in Java
* [textidote](https://github.com/sylvainhalle/textidote): uses LanguageTool on `.tex` files

So why not use LanguageTool? It is large, slow and not tailored for scientific/technical texts. However, I recommend to use LanguageTool in addition.

