# own functions
from papercheck.lib.nlp import *  # language functions
from papercheck.lib.cli import *
from papercheck.pos.posdic import getDict
from papercheck.pos.tags import *
import re
import os
import zipfile
import sys


def read_file_or_zip(filename):
    lines = ""
    try:
        fh = open(filename, "r", encoding="utf8")
        lines = fh.read()
        fh.close()
    except (FileNotFoundError, NotADirectoryError):
        try:
            arch = zipfile.ZipFile(sys.argv[0], "r")
            fh = arch.open(filename, "r")
            lines = fh.read().decode("utf-8")
            fh.close()
        except FileNotFoundError:
            print("ERROR: File '{}' not found.".format(filename))
    return lines


def read_acronyms(acronyms, acronymfile):
    text = read_file_or_zip(acronymfile)

    for line in text.splitlines():
        line = line.strip()
        acronym = re.match(r"\W([A-Z0-9]{2,})", line)
        if acronym != None:
            acronyms[acronym] = ""


class Correction:
    def __init__(self, line, column, match, suggestion, description):
        self.line = line
        self.col = column
        self.match = match
        self.sugg = suggestion
        self.desc = description


# todo: show Capital errors only IF there is a one edit suggestion, otherwise it is probably a name and correct
def check_words(dictionary, text):
    lines = text.splitlines(True)

    word_counter = {}
    corrections = []
    for idx, line in enumerate(lines):
        words = split2words(line)
        for word in words:
            if word.isupper() or isNum(word) or len(re.findall(r"[A-Z]", word)) != 0:
                continue
            isCorrect = word in dictionary
            if not isCorrect:
                if word[0].isupper():
                    lowword = word[0].lower() + word[1:]
                    isCorrect = lowword in dictionary
                if not isCorrect and len(word) > 2:
                    matches = re.findall(r"\W" + word + r"\W", line)
                    match = " " + word + " " if len(matches) == 0 else matches[0]
                    if match[-1] == "-" and word in [
                        "anti",
                        "bio",
                        # "dis",
                        "inter",
                        "intra",
                        # "mis",
                        "multi",
                        "non",
                        "pre",
                        "quasi",
                        "re",
                        "semi",
                        "sub",
                    ]:
                        continue
                    sugg = suggest(dictionary, word)
                    if sugg == "" and word[0].isupper():
                        continue  # do not show capital errors without suggestion
                    if word not in word_counter.keys():
                        word_counter[word] = 0
                    if word_counter[word] < 1:
                        word_counter[word] += 1
                        corrections.append(
                            Correction(
                                idx + 1, 0, match, sugg, "Possibly misspelled word."
                            )
                        )
                        askAction(idx, "Maybe misspelled word.", match, sugg)
                # print("Typo: '{}',  Sugg: {}".format(word, suggest(dictionary, word)))

    return corrections


def edits1(word):
    "All edits that are one edit away from `word`."
    letters = "esianrtolcdugmphbyfvkwz"
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    capital = [word[0].upper() + word[1:]]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    deletes = [L + R[1:] for L, R in splits if R]
    return list(set(capital + transposes + replaces + inserts + deletes))


def suggest(dictionary, wrong):
    suggs = list(set(w for w in edits1(wrong) if w in dictionary.keys()))
    return "" if len(suggs) == 0 else suggs[0]


def checkSpelling(text):

    print(
        "\n\nChecking Spelling:\n----------------------------------------------------"
    )
    # print("CWD:", os.getcwd())

    dictionary = {}
    dictionary = getDict()

    read_acronyms(dictionary, "papercheck/dictionary/acronyms.md")

    # DEBUGGING ONLY
    # text = ""
    # for word in dictionary.keys():
    #     text += word+"\n"
    # with open("dictionary_list.log", "w+") as f:
    #     f.write(text)

    if dictionary == {}:
        return
    corrections = check_words(dictionary, text)
    return corrections
