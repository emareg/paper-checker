# Part of Speech (POS) module

# Despite the fact


from papercheck.pos.dictionary import *
from papercheck.pos.posdic import getDict
from papercheck.pos.POS_en import *
from papercheck.pos.tags import *

from papercheck.lib.nlp import *


##########################################################################
# adj: tal
# noun: mn|son|ton|age|ipe|ime|[^n]g
# verb: ify|erve|[^aouie]ect|[^w]ide|
# singular noun with s: 'mars|mess'

# verb-noun: ence


# idea: posdict.py => one dict for all
# * check units:  13 ms OK

# process: 1. tag words, 2. resolve tags (select one), 3. 

class entry:
    pos=[] #tags
    base=""  # only for irreg verbs?


import re


reGerundExceptions = r"bring|ring|sing|"  # shorter than 2 chars prefix


# should be auto generated, or easy categorizing


lstIntroductoryPhrase = [
    "Actually",
    "As a result",
    "Additionally",
    "Afterwards",
    "Consequently",
    "However",
    "Hence",
    "Finally",
    "First",
    "Furthermore",
    "Therefore",
    "Third(?:ly)?",
    "For example",
    "For (?:this|that) reason",
    "Generally",
    "In general",
    "In fact",
    "In (?:18|19|20)\d\d",
    "In the past",
    "Instead(?! of)",
    "On the other hand",
    "Nevertheless",
    "Nowadays",
    "On the contrary",
    "Recently",
    "Second(?:ly)?",
    "What is more",
]





G_posdic = getDict()


######################################################################################





def analyzeSentence(sentence):
    if isValidSentence(sentence):
        sentence = stripSimpleIntroductory(sentence)
        ses = splitSubsentences(sentence)
        for sentence in ses:
            words = splitWords(sentence)
            tw = tagWords(words)
            print(tw, "\n=====\n")
            analyzeTags(tw)


def analyzeSentences(text):
    # sentences = re.split(r"(?<=[^A-Z][^A-Z][.?!:])\s+(?=[A-Z])", text)
    sentences = split2sentences(text)
    for sentence in sentences[:6]:
        analyzeSentence(sentence)


def isValidSentence(sentence):
    return len(sentence) > 25 and len(sentence) < 500


def stripSimpleIntroductory(sentence):
    reIntro = "(?:" + "|".join(lstIntroductoryPhrase) + "),\s+"
    lstFragments = re.split(reIntro, sentence, 1)
    if len(lstFragments) > 1:
        return lstFragments[1]
    else:
        return lstFragments[0]


def splitSubsentences(sentence):
    lstFragments = re.split("[,;]", sentence)
    # lstFragments = re.split( '\(([^)]+)\)', sentence, 1 )
    # print(lstFragments)
    return lstFragments


def findSubject(sentence):
    reDeterminer = "(" + "|".join(lstDeterminers) + ")"
    re.search(reDeterminer)


def splitWords(sentence):
    lstWords = re.split("\s+|[,;:.]", sentence)
    if '' in lstWords: lstWords.remove('')
    return lstWords


def tokenize(text):
    sentences = re.split(r"(?<=[^A-Z][^A-Z][.?:])\s+(?=[A-Z])", text)


# guess POS tag based on word pattern
def guessTag(word):
    if word == '': return 'X'
    if len(word) == 1:
        if word in '.,!?':
            tag = POS_TAG_PUNCTUATION
        else:
            tag = POS_TAG_SYMBOL
    elif word[0].isupper():
        if word[-1] == 's':
            tag = POS_TAG_NOUN_PL
        else:
            tag = POS_TAG_NOUN
    elif word in lstAdv or word[-2:] == "ly":
        tag = POS_TAG_ADVERB
    elif re.match(reAdjective, word) or re.match(r"\w\w+-\w\w+", word):
        tag = POS_TAG_ADJECTIVE
    elif word[-2:] == "ed" or word[-3:] == "ing":
        tag = POS_TAG_VERB
    elif re.match(reNounPl, word):
        tag = POS_TAG_NOUN_PL
    elif re.match(reNounSgl, word):
        tag = POS_TAG_NOUN
    else:
        # stupid guesses
        if word[-1:] == "s": 
            tag = POS_TAG_NOUN_PL
        else:
            tag = "X"
    return tag



def tagWords(words):
    taglist = []
    words[0] = words[0].lower()
    for word in words:
        if word in G_posdic.keys() and G_posdic[word]:
            taglist.append((word, G_posdic[word]))
        else:
            guess = guessTag(word)
            taglist.append((word, [guess]))
            print("POS_TAG_X: ", word, guess)

    return taglist


def analyzeTags(tw):
    wrongs = [x[1] for x in tw if len(x[1]) == 0]
    print("wrongs:", wrongs)
    tags = [x[1][0] for x in tw]
    tagstring = "".join(tags)
    # print(tagstring)
    # if('Nn' in tagstring):
    # print(tw)
    if re.match("m[^b]", tagstring):  # modal without verb
        print(tw)
    # if(re.match('.*j*n*[nN][^p]b', tagstring)):
    # print(tw)
    # if( 'NNP,VB' in tagstring ):
    # print(tags)
    # todo: re.finiter

    # DET X X NN/NNP
    # 1.NN [^PP]+ VB (is/are)
    # NN (that/which) VB
    # with/be NN
