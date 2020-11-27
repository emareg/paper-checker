import re
import os
import sys
import zipfile

from papercheck.lib.nlp import *  # language functions
from papercheck.pos.tags import *

DIC_DIR = __file__.replace("pos/posdic.py", "dictionary/")
POS_DIR = DIC_DIR + "pos/"

G_posdic = {}
G_tagcons = False


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


def addWord(posdic, word, tag):
    if word not in posdic.keys():
        posdic[word] = []
    if tag not in posdic[word] and tag != "X":
        # if tag == 'X' and len(posdic[word]) > 0: return
        posdic[word].append(tag)
        # if 'X' in posdic[word] and len(posdic[word]) > 1:
        #   posdic[word].remove('X')


def read_txtlist(posdic, txtfile, tag):
    text = read_file_or_zip(txtfile)

    for line in text.splitlines():
        words = line.strip().split(" ")
        for word in words:
            addWord(posdic, word, tag)
    return posdic


def parse_affix(dic, word, affix):
    addwords = []
    pfxwords = [word]
    prefixes = [c for c in affix if c in "AIUCEFK"]
    suffixes = [c for c in affix if c not in "AIUCEFK"]

    for char in prefixes:
        if char == "A":
            pfxwords.append("re" + word)
        elif char == "I":
            pfxwords.append("in" + word)
        elif char == "U":
            pfxwords.append("un" + word)
        elif char == "C":
            pfxwords.append("de" + word)
        elif char == "E":
            pfxwords.append("dis" + word)
        elif char == "F":
            pfxwords.append("con" + word)
        elif char == "K":
            pfxwords.append("pro" + word)

    for pfxword in pfxwords:
        for char in suffixes:
            if char == "V":
                newword = re.sub("e$|$", "ive", pfxword)
                addWord(dic, newword, POS_TAG_ADJECTIVE)
            elif char == "N":
                newword = re.sub(
                    r"(?<!ion)$",
                    "en",
                    re.sub("y$", "ication", re.sub("e$", "ion", pfxword)),
                )
                addWord(dic, newword, POS_TAG_NOUN)
            elif char == "X":
                newword = re.sub(
                    r"(?<!ions)$",
                    "ens",
                    re.sub("y$", "ications", re.sub("e$", "ions", pfxword)),
                )
                addWord(dic, newword, POS_TAG_NOUN_PL)
            elif char == "H":
                addWord(dic, re.sub(r"y$", "ie", pfxword) + "th", "X")  #
            elif char == "Y":
                addWord(dic, adverb(pfxword), POS_TAG_ADVERB)
            elif char == "G":
                addWord(dic, pfxword, POS_TAG_VERB)
                addWord(dic, gerund(pfxword), POS_TAG_VERB)
            elif char == "J":
                addWord(dic, gerund(pfxword), POS_TAG_NOUN)
                addWord(dic, gerund(pfxword) + "s", POS_TAG_NOUN_PL)
            elif char == "D":
                addWord(dic, past(pfxword), POS_TAG_VERB)
            elif char == "T":
                addWord(dic, pfxword, POS_TAG_ADJECTIVE)
                addWord(dic, superlative(pfxword), POS_TAG_ADJECTIVE)
            elif char == "R":
                addWord(dic, comperative(pfxword), POS_TAG_ADJECTIVE)
            elif char == "Z":
                addWord(dic, comperative(pfxword), POS_TAG_NOUN)
                addWord(dic, comperative(pfxword) + "s", POS_TAG_NOUN_PL)
            elif char == "S":
                newword = plural(pfxword)
                if "M" in suffixes or pfxword + "'s" in dic:
                    addWord(dic, newword, POS_TAG_NOUN_PL)
                if "G" in suffixes:
                    addWord(dic, newword, POS_TAG_VERB)
                else:
                    addWord(dic, newword, POS_TAG_NOUN_PL)
            elif char == "P":
                newword = re.sub(r"(?<=[^aeiou])y$", "i", pfxword) + "ness"
                addWord(dic, newword, POS_TAG_NOUN)
            elif char == "M":
                addWord(dic, pfxword, POS_TAG_NOUN)
                addWord(dic, possessive(pfxword), POS_TAG_NOUN)
            elif char == "B":
                newword = re.sub(r"(?<=[^e])e$", "", pfxword) + "able"
                addWord(dic, newword, POS_TAG_ADJECTIVE)
            elif char == "L":
                addWord(dic, pfxword + "ment", POS_TAG_NOUN)

        if pfxword[-1:] == "'" or pfxword[-2:] == "'s":
            addWord(dic, pfxword, "N")
            addWord(dic, re.sub(r"'s?", "", pfxword), "N")
        else:
            addWord(dic, pfxword, "X")
    # if word=='provide': print("word-entry:", word, prefixes, suffixes, dic["provide"])


def parse_dicfile(posdic, dicfile):
    if dicfile[-4:] != ".dic":
        print("ERROR: Not a .dic file:", dicfile)
    text = read_file_or_zip(dicfile)

    for line in text.splitlines():
        word, _, affix = line.strip().partition("/")
        parse_affix(posdic, word, affix)


def build_dictionary():
    posdic = {}

    read_txtlist(posdic, POS_DIR + "en_basic.txt", POS_TAG_BASE_VERB)
    read_txtlist(posdic, POS_DIR + "en_modal.txt", POS_TAG_MODAL_VERB)
    read_txtlist(posdic, POS_DIR + "en_adverbs.txt", POS_TAG_ADVERB)
    read_txtlist(posdic, POS_DIR + "en_adjectives.txt", POS_TAG_ADJECTIVE)
    read_txtlist(posdic, POS_DIR + "en_conjunction.txt", POS_TAG_CONJUNCTION)
    read_txtlist(posdic, POS_DIR + "en_letters.txt", POS_TAG_SYMBOL)
    read_txtlist(posdic, POS_DIR + "en_determiners.txt", POS_TAG_DETERMINER)
    read_txtlist(posdic, POS_DIR + "en_adposition.txt", POS_TAG_PREPOSITION)
    read_txtlist(posdic, POS_DIR + "en_pronoun.txt", POS_TAG_PRONOUN)
    read_txtlist(posdic, POS_DIR + "en_irregular_verbs.txt", POS_TAG_VERB)

    # print('POS:', posdic['a'])

    noun_dict = {}
    read_txtlist(noun_dict, POS_DIR + "en_proper_nouns.txt", POS_TAG_NOUN)
    for noun in noun_dict:
        addWord(posdic, noun, POS_TAG_NOUN)
        addWord(posdic, plural(noun), POS_TAG_NOUN_PL)

    parse_dicfile(posdic, DIC_DIR + "en-Academic.dic")
    # parse_dicfile(posdic, DIC_DIR + "en_US.dic") # should only add tags to new words

    return posdic


def getDict():
    global G_posdic
    if not G_posdic:
        G_posdic = build_dictionary()
    return G_posdic
