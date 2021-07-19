from collections import Counter

from papercheck.lib.nlp import *
from papercheck.pos.POS_en import *

from papercheck.lib.word_lists import lstVague


# Statistics
##########################
G_stats = {}
G_words = {}


# todo: [13-15] => 3 refs
# test: \cite{barba-to, me14} [BCC+ 16, GESL06, KPP10] analysis
def statsReferences(text):
    div = int(len(text) * 0.7)
    text = text[:div] + re.sub(
        r"(?:R ?EFERENCES|Bibliography|References)(?:.|\n)*", "", text[div:]
    )

    refs = {}
    matches = re.findall(
        r"\\cite\{([^},]+)(?:, ?([^},]+))*\}", text
    )  # removed by tex stripper
    # print("Matches:", matches)
    matches += re.findall(
        r"\s\[((?:[A-Z][\w+ ]{1,3})?\d\d?)(?:(?:, |[…–])([A-Z][\w+ ]{1,3})?\d\d?)*\][.,]?(?=\s[\w[])",
        text,
    )
    for match in matches:
        for ref in match:
            if ref != "":
                refs[ref] = refs[ref] + 1 if ref in refs.keys() else 1
    # print(sorted(refs))
    return refs


# TABLE III
def statsFigures(text):
    figs = {"figs": 0, "tabs": 0, "lsts": 0}
    figs["figs"] = len(
        re.findall(
            r"\\begin\{figure\}|(?<=\n)\s*Fig(?:\.|ure) (?:\d\d?|[0-9A]\.\d\d?)(?:[.:]\s|\n)",
            text,
        )
    )
    figs["tabs"] = len(
        re.findall(
            r"\\begin\{table\}|(?<=\n)\s*(?:Table|TABLE) (?:\d\d?|[0-9A]\.\d\d?|[IVX]{,4})(?:[.:]\s|\n)",
            text,
        )
    )
    figs["lsts"] = len(
        re.findall(
            r"\\begin\{(?:lstlisting|algorithm|algorithmic|program)\}|(?<=\n)\s*(?:Listing|Algorithm) (?:\d\d?|[0-9A]\.\d\d?|[IVX]{,4})(?:[.:]\s|\n)",
            text,
        )
    )
    return figs


def addDicCount(dic, entry):
    if entry in dic.keys():
        dic[entry] += 1
    else:
        dic[entry] = 1


class GenderCounts:
    def __init__(self):
        self.nMaleWords = 0
        self.nFemaleWords = 0
        self.nNeutralWords = 0


class MinMaxCounts:
    def __init__(self):
        self.nMin = 0
        self.nMax = 0
        self.nNeutralWords = 0


class CharCounts:
    def __init__(self):
        self.nTotal = 0
        self.nExclSpaces = 0
        self.nInWords = 0


class WordCounts:
    def __init__(self):
        self.nTotal = 0
        self.nUnique = 0
        self.unique_pcnt = 0
        self.len_avg = 0
        self.longest = ""


class SentCounts:
    def __init__(self):
        self.nTotal = 0
        self.nWordsMin = 1000
        self.nWordsMax = 0


# refactored verson
class TextStats:
    def __init__(self, text=""):

        # count classes
        self.gender = GenderCounts()
        self.char = CharCounts()
        self.word = WordCounts()
        self.sent = SentCounts()

        # payload
        self.words = []
        self.sentences = []
        self.text = ""

        # dict counts
        self.fig = {}
        self.ref = {}
        self.vague = {}
        self.freq = {}

        self.parse(text)

    def parse(self, text):
        text = text.strip()
        self.text = text

        self.char.nTotal = len(text)
        self.char.nExclSpaces = len(re.sub(r"\s+", "", text))

        self.sentences = split2sentences(text)
        self.sent.nTotal = len(self.sentences)
        for sentence in self.sentences:
            words = split2words(sentence)
            self.words += words
            lenW = len(words)

            self.sent.nWordsMin = min(self.sent.nWordsMin, lenW)
            self.sent.nWordsMax = max(self.sent.nWordsMax, lenW)

        # words together
        self.word.nTotal = len(self.words)
        self.word.nUnique = len(set(self.words))
        self.word.unique_pcnt = round(
            100 * self.word.nUnique / self.word.nTotal if self.word.nTotal else 0
        )

        # figures / references
        self.ref = statsReferences(self.text)
        self.fig = statsFigures(text)

        # look at individual words
        for word in self.words:

            if word in lstVague:
                addDicCount(self.vague, word)
            if word in ["he", "his", "him"]:
                self.gender.nMaleWords += 1
            if word in ["it", "its"]:
                self.gender.nNeutralWords += 1
            if word in ["she", "her"]:
                self.gender.nFemaleWords += 1

            self.char.nInWords += len(word)
            self.word.len_avg += len(word) / len(self.words)

            if len(word) > len(self.word.longest):
                self.word.longest = word

    def __str__(self):

        stats_str = ""
        stats_str += " Characters: {} (incl. spaces)\n".format(self.char.nTotal)
        stats_str += "             {} (excl. spaces)\n".format(self.char.nExclSpaces)
        stats_str += "             {} (only words)    \n".format(self.char.nInWords)
        stats_str += "                                \n"
        stats_str += "      Words: {} (total)         \n".format(self.word.nTotal)
        stats_str += "             {} (unique, {} %)  \n".format(
            self.word.nUnique, self.word.unique_pcnt
        )
        stats_str += "                                \n"
        stats_str += "  Sentences: {} (total)         \n".format(len(self.sentences))
        stats_str += "             words per sent: {} .. {} ({:.1f} avg.)\n".format(
            self.sent.nWordsMin,
            self.sent.nWordsMax,
            self.word.nTotal / self.sent.nTotal,
        )
        stats_str += "                                \n"
        stats_str += "Vague words: {}                 \n".format(
            sum(self.vague.values())
        )
        stats_str += "    Genders: {} he, {} it, {} she\n".format(
            self.gender.nMaleWords, self.gender.nNeutralWords, self.gender.nFemaleWords
        )
        stats_str += " References: {} refs, {} times cited\n".format(
            len(self.ref.keys()), sum(self.ref.values())
        )
        stats_str += "    Figures: {} figs, {} tables, {} listings\n".format(
            self.fig["figs"], self.fig["tabs"], self.fig["lsts"]
        )

        return stats_str
