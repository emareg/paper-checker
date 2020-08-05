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

# process: 1. tag words, 2. resolve tags (select one), 3. chunk tags 4. analyze structure


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
        chunks = []
        for sentence in ses:
            words = splitWords(sentence)
            tw = tagWords(words)
            chunks.append(chunckTags(tw))
            # analyzeTags(tw)
        print(chunks)
        print("========\n")


def analyzeSentences(text):
    # sentences = re.split(r"(?<=[^A-Z][^A-Z][.?!:])\s+(?=[A-Z])", text)
    sentences = split2sentences(text)
    for sentence in sentences[:-20]:
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
    lstFragments = re.split("[,;:]", sentence)
    # lstFragments = re.split( '\(([^)]+)\)', sentence, 1 )
    # print(lstFragments)
    return lstFragments


def findSubject(sentence):
    reDeterminer = "(" + "|".join(lstDeterminers) + ")"
    re.search(reDeterminer)


def splitWords(sentence):
    lstWords = re.split("\s+|[,;:.]", sentence)
    if "" in lstWords:
        lstWords.remove("")
    return lstWords


def tokenize(text):
    sentences = re.split(r"(?<=[^A-Z][^A-Z][.?:])\s+(?=[A-Z])", text)


# guess POS tag based on word pattern
def guessTag(word):
    if word == "":
        return "X"
    if len(word) == 1:
        if word in ".,!?":
            tag = POS_TAG_PUNCTUATION
        else:
            tag = POS_TAG_SYMBOL
    elif word[0].isupper():
        if word[-1] == "s":
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
    for word in words:
        if len(word) == 0:
            continue
        if word in G_posdic and G_posdic[word]:
            taglist.append((word, G_posdic[word]))
        elif word.lower() in G_posdic and G_posdic[word.lower()]:
            taglist.append((word, G_posdic[word.lower()]))
        else:
            guess = guessTag(word)
            taglist.append((word, [guess]))
            # print("POS_TAG_X: ", word, guess)

    return taglist


def analyzeTags(tw):
    # wrongs = [x[1] for x in tw if len(x[1]) == 0]
    # print("wrongs:", wrongs)
    tags = [x[1][0] for x in tw]
    tagstring = "".join(tags)
    # print(tagstring)

    # if('Nn' in tagstring):
    # print(tw)
    # if re.match("m[^b]", tagstring):  # modal without verb
    #     print(tw)
    # if(re.match('.*j*n*[nN][^p]b', tagstring)):
    # print(tw)
    # if( 'NNP,VB' in tagstring ):
    # print(tags)
    # todo: re.finiter

    # DET X X NN/NNP
    # 1.NN [^PP]+ VB (is/are)
    # NN (that/which) VB
    # with/be NN


def chunckTags(tw):
    """ will chunk tags together such as 'the red apple' being a noun phrase.
    The function will also report simple mistakes found during chunking. """
    chunks = [x[1][0] for x in tw]
    chunks = resolveTags(tw)

    if "X" in chunks:
        print("Unable to analyze: ", [x[0] for x in tw if x[1][0] == "X"])
        return  # cannot analyze...

    sent = [x[0] for x in tw]

    # Determiner chunks
    while True:
        m = re.search(r"D[D]+", "".join(chunks))
        if m == None:
            break
        dets = " ".join(sent[m.start() : m.end()])
        if dets not in ["all the", "the most", "all of"]:
            print("potential mistake:", dets)
        sent[m.start() : m.end()] = []
        chunks[m.start() : m.end()] = ["D"]

    # Verb as Adjective Chunks VN=N
    m = re.search(r"[DP]J?V([NS])", "".join(chunks))
    if m != None:
        print("Adjective:", m.group(0))
        if re.search(r" \w+(?:ed|ing) \w+$", " ".join(sent[m.start() : m.end()])):
            sent[m.start() : m.end()] = [" ".join(sent[m.start() : m.end()])]
            chunks[m.start() : m.end()] = [m.group(1)]

    # Noun chunks
    # todo: [^ND]N+[^NS] is probably missing a determiner 'making protocol interactive'
    while True:
        m = re.search(r"D?J*N*([NS])(?:CD?J*N*([NS]))?", "".join(chunks))
        if m == None:
            break
        tag = m.group(1).lower()
        if m.group(2):
            if m.group(1) == "S" and m.group(2) == "N":
                print("TAG-ERR: Nouns should both be plural or singular:", m.group(0))
            else:
                tag = m.group(2).lower()
        sent[m.start() : m.end()] = [" ".join(sent[m.start() : m.end()])]
        chunks[m.start() : m.end()] = [tag]

    # Verb chunks
    while True:
        m = re.search(r"M?B?A?V|M?A?BA?J?", "".join(chunks))
        if m == None:
            break
        sent[m.start() : m.end()] = [" ".join(sent[m.start() : m.end()])]
        chunks[m.start() : m.end()] = ["v"]

    # meta chunk nPn ('stack usage of the implementation')
    while True:
        m = re.search(r"([ns])P[ns]", "".join(chunks))
        if m == None:
            break
        if "of" in sent[m.start() : m.end()]:
            sent[m.start() : m.end()] = [" ".join(sent[m.start() : m.end()])]
            chunks[m.start() : m.end()] = [m.group(1)]
        else:
            break

    # meta chunk vv if second v is 'to X'
    while True:
        m = re.search(r"v(v)", "".join(chunks))
        if m == None:
            break
        if sent[m.start() + 1] != "to":
            print("TAG-ERR: Probably wrong verb structure:", m.group(0))
        sent[m.start() : m.end()] = [" ".join(sent[m.start() : m.end()])]
        chunks[m.start() : m.end()] = ["v"]

    # print(sent)
    # print("".join(chunks))

    return list(zip(sent, chunks))


def resolveTags(tw):
    """ function that tries to decide which POS tag to use """
    tags = [x[1] for x in tw]
    ws = [x[0] for x in tw]

    for i, tag in enumerate(tags):
        if len(tag) == 1:
            tags[i] = tags[i][0]
            continue
        if "V" in tag:
            w1 = ws[max(i - 1, 0)]
            w2 = ws[max(i - 2, 0)]
            t1 = tags[max(i - 1, 0)][0]
            t2 = tags[max(i - 2, 0)][0]

            if (
                "of" in [w1, w2]
                or t1 == "D"  # a N
                or (t2 == "D" and t1 == "J")  # the red N
                or (w2 == "to" and t1 == "V")
            ):  # to store N
                if "N" in tag:
                    tags[i] = "N"
                elif "S" in tag:
                    tags[i] = "S"
                elif "J" in tag:
                    tags[i] = "J"

            elif "to" in [w1, w2]:
                tags[i] = "V"
            elif t1 in "MR":
                tags[i] = "V"
            print("## Resolved: ", tw[i], tags[i])
        else:
            print("UNKNOWN TAG COMBINATION:", ws[i], tag)

        tags[i] = tags[i][0]
    return tags
