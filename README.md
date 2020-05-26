# PaperCheck

[![Actions Status](https://github.com/emareg/paper-checker/workflows/CI/badge.svg)](https://github.com/emareg/paper-checker)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

PaperCheck is a python script that searches for simple grammar mistakes in scientific english texts. Unlike other grammar checkers it is free and tailored for scientific texts, such as papers. It might find words that pass a spell check but are most likely not intended in a scientific context, such as "angel" vs. "angle".

## Getting Started

```
git clone git@github.com:emareg/paper-checker.git
cd paper-checker
make setup
```

Afterwards, you can use the script in two ways:

**1. Run the python file**
```
python3 paperchecker.py -sgy example/testfile.tex
```

**2. Compile as a stand-alone executable (Unix only)**
```
make
./paperchecker -sgy example/testfile.tex
```

Supported file types: `.tex .txt .md .pdf`

The found issues are displayed in the terminal and also written into `papercheck_report.html`

### System wide installation

```
make install
```

This will copy the stand-alone executable to `/usr/loca/bin`

## Features

### Spell Checker (`-s` option)
Will highlight spelling errors. The script uses a small basic dictionary plus some additional self-made dictionaries for terms such as

* technical: “microcontroller”, “superframe”, “bitmask”
* mathematical: “eigenvector”, “linearization”
* chemical: todo

The larger standard dictionaries are unsuitable because they

* contain errors such as “longitudianl” or “schemati”
* mask informal plural forms such as “vertexes” which should be “vertices”
* include obsolete forms such as “latence” which should be “latency”

### Grammar Checker (`-g` option)
Will highlight simple grammar mistakes such as

* misuse of “a” or “an”
* doubled auxiliary verbs (e.g. “is are”)
* doubled determiners (e.g. “this the”)
* confused “then” vs. “than”
* confused “to” vs. “too”
* wrong person-verb combination (e.g. “This were”)

### Style Checker (`-y` option)
Will highlight language that could be improved such as

* wrong words in scientific context (e.g. “angle” vs. “angel”)
* non explained acronyms
* improve less formal words (e.g. use “entire” instead of “whole”)
<!-- * numbers below 12 are written as digits -->

### Plagiarism Checker (`-p` option)
**experimental!**

The script will try to find significant sentences, which are then compared to Google search results. This is a very poor approach but useful as a minimal effort with zero cost.

### TeX checker
When you run the script on `.tex` files, it will also check for certain TeX problems such as

* unused labels
* missing periods in figure/table captions
* unused math operators in math mode, e.g. `$sin$` instead of `$\sin$`

## Related Work

* [LanguageTool](https://languagetool.org/): Grammar, Style and Spell Checker written in Java
* [textidote](https://github.com/sylvainhalle/textidote): uses LanguageTool on `.tex` files

So why not use LanguageTool? It is large, slow and not tailored for scientific/technical texts. However, I recommend to use LanguageTool in addition.
