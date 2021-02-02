# own functions
from papercheck.lib.nlp import *  # language functions
from papercheck.lib.cli import *
from papercheck.pos.posdic import getDict
from papercheck.pos.tags import *
import re
import os
import zipfile
import sys
import pathlib

DIC_DIR = pathlib.Path("dictionary")


def read_file_or_zip(filename):
    abs_filepath = pathlib.Path(__file__).resolve().parent.parent.joinpath(filename)

    lines = ""
    try:
        fh = open(abs_filepath, "r", encoding="utf8")
        lines = fh.read()
        fh.close()
    except (FileNotFoundError, NotADirectoryError):
        try:
            zip_filepath = pathlib.Path("papercheck").joinpath(filename)
            arch = zipfile.ZipFile(sys.argv[0], "r")
            fh = arch.open(str(zip_filepath), "r")
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
                    matches = re.findall(r"(?:\W|^)" + word + r"\W", line)
                    match = " " + word + " " if len(matches) == 0 else matches[0]
                    if match[0].isalpha():
                        match = "\n" + match
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
    replaces = [L + c + R[1:] for L, R in splits[1:] if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    deletes = [L + R[1:] for L, R in splits if R]

    special = []
    if len(word) > 5 and word[-2:] == "ic": special.append(word+"al")
    if len(word) > 7 and word[-4:] == "ical": special.append(word[:-2])
    if len(word) > 7 and word[-4:] == "icly": special.append(word[:-2]+"ally")
    return list(set(capital + transposes + replaces + inserts + deletes + special))


    


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

    read_acronyms(dictionary, DIC_DIR.joinpath("acronyms.md"))

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
