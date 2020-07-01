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
    matches = re.findall(r"\\cite\{([^},]+)(?:, ?([^},]+))*\}", text)
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
            r"\\begin\{figure\}|(?<=\n)\s*Fig(?:\.|ure) \d\d?(?:[.:]\s|\n)", text
        )
    )
    figs["tabs"] = len(
        re.findall(
            r"\\begin\{table\}|(?<=\n)\s*(?:Table|TABLE) (?:\d\d?|[IVX]{,4})(?:[.:]\s|\n)",
            text,
        )
    )
    figs["lsts"] = len(
        re.findall(
            r"\\begin\{(?:lstlisting|algorithm|algorithmic|program)\}|(?<=\n)\s*(?:Listing|Algorithm) (?:\d\d?|[IVX]{,4})(?:[.:]\s|\n)",
            text,
        )
    )
    return figs


def calcStats(text):
    # todo: sentences, sentence lengths, words, cohesion, text difficulty

    text = text.strip()

    global G_stats
    # init
    G_stats["words"] = 0
    G_stats["letters_all"] = len(text)
    G_stats["characters_no_white"] = len(re.sub(r"\s+", "", text))
    G_stats["characters_words"] = 0
    G_stats["unique_words"] = 0
    G_stats["word_length_min"] = 1000
    G_stats["word_length_avg"] = 0
    G_stats["word_length_max"] = 0
    G_stats["vague_words"] = 0
    G_stats["male_words"] = 0
    G_stats["female_words"] = 0
    G_stats["neutral_words"] = 0
    G_stats["words_per_sent_min"] = 1000
    G_stats["words_per_sent_max"] = 0
    G_stats["words_per_sent_avg"] = 0
    G_stats["sent_short"] = 0
    G_stats["sent_long"] = 0

    refs = statsReferences(text)
    G_stats["refs_total"] = len(refs.keys())
    G_stats["refs_cites"] = sum(refs.values())

    figs = statsFigures(text)
    G_stats["figs"] = figs["figs"]
    G_stats["tabs"] = figs["tabs"]
    G_stats["lsts"] = figs["lsts"]

    sentences = split2sentences(text)

    G_stats["sentences"] = len(sentences)

    all_words = []
    for sentence in sentences:
        words = split2words(sentence)
        if len(words) < 10:
            G_stats["sent_short"] += 1
        if len(words) > 30:
            G_stats["sent_long"] += 1
        if len(words) < G_stats["words_per_sent_min"]:
            G_stats["words_per_sent_min"] = len(words)
            G_stats["shortest_sent"] = sentence
        if len(words) > G_stats["words_per_sent_max"]:
            G_stats["words_per_sent_max"] = len(words)
            G_stats["longest_sent"] = sentence
        G_stats["words_per_sent_avg"] += len(words) / len(sentences)
        all_words += words

    # look at words
    for word in all_words:

        if word in lstVague:
            G_stats["vague_words"] += 1
        if word in ["he", "his", "him"]:
            G_stats["male_words"] += 1
        if word in ["it", "its"]:
            G_stats["neutral_words"] += 1
        if word in ["she", "her"]:
            G_stats["female_words"] += 1

        G_stats["characters_words"] += len(word)

        if len(word) < G_stats["word_length_min"]:
            G_stats["word_length_min"] = len(word)
        if len(word) > G_stats["word_length_max"]:
            G_stats["word_length_max"] = len(word)
        G_stats["word_length_avg"] += len(word) / len(all_words)

        if len(word) > 5:
            pass

    G_stats["words"] = len(all_words)
    G_stats["unique_words"] = len(set(all_words))
    long_words = [x.lower() for x in all_words if len(x) > 5]
    word_count = Counter(long_words)
    G_stats["common_words"] = word_count.most_common(6)


def createStats(text):
    global G_stats
    calcStats(text)

    stats_str = ""
    stats_str += " Characters: {} (incl. spaces)  \n".format(
        G_stats["letters_all"])
    stats_str += "             {} (excl. spaces)  \n".format(
        G_stats["characters_no_white"]
    )
    stats_str += "             {} (only words)    \n".format(
        G_stats["characters_words"]
    )
    stats_str += "                                \n"
    stats_str += "      Words: {} (total)         \n".format(G_stats["words"])
    stats_str += "             {} (unique, {} %)  \n".format(
        G_stats["unique_words"], round(
            100 * G_stats["unique_words"] / G_stats["words"])
    )
    stats_str += "             chars per word: {} .. {} ({:.2f} avg.)\n".format(
        G_stats["word_length_min"],
        G_stats["word_length_max"],
        G_stats["word_length_avg"],
    )
    stats_str += "                                \n"
    stats_str += "  Sentences: {} (total)         \n".format(
        G_stats["sentences"])
    stats_str += "             {} short, {} long  \n".format(
        G_stats["sent_short"], G_stats["sent_long"]
    )
    stats_str += "             words per sent: {} .. {} ({:.2f} avg.)\n".format(
        G_stats["words_per_sent_min"],
        G_stats["words_per_sent_max"],
        G_stats["words_per_sent_avg"],
    )
    stats_str += "                                \n"
    stats_str += "Vague words: {}                 \n".format(
        G_stats["vague_words"])
    stats_str += "    Genders: {} he, {} it, {} she\n".format(
        G_stats["male_words"], G_stats["neutral_words"], G_stats["female_words"]
    )
    stats_str += " References: {} refs, {} times cited\n".format(
        G_stats["refs_total"], G_stats["refs_cites"]
    )
    stats_str += "    Figures: {} figs, {} tables, {} listings\n".format(
        G_stats["figs"], G_stats["tabs"], G_stats["lsts"]
    )
    # stats_str += "                                \n"
    # stats_str += "Most Freq. Words: {}\n".format(G_stats["common_words"])
    # stats_str += "Longest Sentence: '{}...'\n".format(G_stats["longest_sent"][:50])

    return stats_str
