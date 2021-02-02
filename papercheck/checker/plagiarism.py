import time
import sys
import re
from papercheck.lib.nlp import *
from papercheck.lib.stripper import *
from collections import Counter
import html

SENTENCES_MAX = 8  # maximum analyzed sentences per document
QUERY_WAIT_SECONDS = 1.3  # wait time between google queries

SIMILAR_THRESHOLD = 0.7
SENTENCE_WORD_MIN = 12
SENTENCE_WORD_MAX = 22

# imports


# reSuffixNoun = r'\w\w+(?:a|f|i|age|ican|cy|ion|ium|ness|[cl]ity|logy|ism|[lt]ist|here|ment|omy|ver|[ea]nce|ght|ure|one|or|ship|[^o]us|[^aeiou]em|[mnpt]er|[oae][oa][dmnprkt])'
# reSuffixNounPl =  reSuffixNoun.replace('y|', 'ie|')
# reSuffixNounPl =  reSuffixNoun.replace('s|', 'se|')
# reSuffixNounPl =  reSuffixNoun.replace('|', 's|')  #re.sub(r'([^ys])\||\)', '\1s')
# reSuffixNounPl = reSuffixNoun.replace(')', '|ings)')
# reNoun = '(?:' + reSuffixNoun + '|' + reSuffixNounPl + ')$'

# def significantNouns( text ):
#     sentences = split2sentences( text )
#     all_words = []
#     for sentence in sentences:
#         words = split2words( sentence )
#         all_words += [x.lower() for x in words]

#     long_words = [ x for x in all_words if len(x) > 5 ]
#     word_counts = Counter(long_words)
#     common_word_counts = word_counts.most_common(20)
#     common_words = [wc[0] for wc in common_word_counts]

#     print("Significant Nouns: ", common_word_counts)
#     nouns = []
#     for word in common_words:
#         res = re.findall(reNoun, word)
#         print(res)
#         if res != []:
#             nouns.append(word)

#     print("Significant Nouns: ", nouns)


headers_Get = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "de-DE,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def distance(text1, text2):
    words_sent1 = {}
    words_sent1 = {}

    sum1 = sum(i * i for i in dict_file1.values())
    sum2 = sum(i * i for i in dict_file2.values())
    mod_fl1 = sqrt(sum1)
    mod_fl2 = sqrt(sum2)
    dotProduct = 0
    for key in dict_file2:
        if key in dict_file1:
            dotProduct += dict_file1[key] * dict_file2[key]
        distance = acos(dotProduct / int(mod_fl1 * mod_fl2))
    if distance == 0:
        print("Complete Match found")
    elif distance > 0 and distance <= (
        1 / sqrt(2)
    ):  # setting the threshold to 45 degrees
        print("Partial Match Found")
    else:
        print("No Match Found")


def google_search(searchstr):
    import requests
    import urllib

    q = urllib.parse.quote_plus(searchstr)
    # todo: improve query: %2Bterm?

    # print("Requesting: ", q)
    s = requests.Session()
    url = (
        "https://www.google.com/search?q=" + q + "&ie=utf-8&oe=utf-8"
    )  # &num={}'.format(num)
    html_res = s.get(url, headers=headers_Get).text
    s.close()

    RES_START = ">Webergebnisse</h2>"  # '<div id="search">'
    RES_END = '<div id="foot'
    html_res = html_res[
        html_res.index(RES_START) + len(RES_START) : html_res.index(RES_END)
    ]

    output = []

    # print("HTML:", html_res, "\n\n")
    results = re.findall(
        r'<div class="g">(.*?)(?=><div class="g">)', html_res, re.DOTALL
    )
    for result in results:
        # print("Result:", result, "\n\n")
        title = re.findall(r"<h3 class=.*?>(.*?)</h3>", result, re.DOTALL)[0]
        urls = re.findall(
            # r'<div class="rc?"[^>]*?>.*?<a href="(.*?)"', result, re.DOTALL
            r'<a href="(https?.*?)"',
            result,
            re.DOTALL,
        )
        url = urls[0] if len(urls) != 0 else ""
        desc = re.findall(
            # r'<span class="st">(?:<span class="f">.*?</span>)?(.*?)</span>',  # span with classes
            r'<span class="aCOpRe">(?:<span class="f">.*?</span>)?(.*?)</span>',  # span with classes
            # r'<span[^>]*?>(?:<span class="f">.*?</span>)?(.*?)</span>',  # span that contains <em>
            result,
            re.DOTALL,
        )[0]
        output.append({"title": title, "url": url, "desc": desc})

    return output


def findSignificantSentences(text):
    sentences = split2sentences(text)
    all_words = []
    for sentence in sentences:
        words = split2words(sentence)
        all_words += [x.lower() for x in words]

    # print(all_words)
    unique_words = set(all_words)
    long_words = [x for x in all_words if len(x) > 5]
    word_counts = Counter(long_words)
    common_word_counts = word_counts.most_common(10)
    # print("Significant Words: ", common_word_counts)

    common_words = [wc[0] for wc in common_word_counts]

    significant_sentences = []
    for idx, sentence in enumerate(sentences):
        words = split2words(sentence)
        if len(words) < SENTENCE_WORD_MIN or len(words) > SENTENCE_WORD_MAX:
            continue
        if not any(w.lower() in common_words for w in words):
            continue
        if re.findall(r"\\cite|\[\d\d?\]", sentence):
            continue  # citation in sentence
        if re.findall(r"\\cite|\[\d\d?\]\.\s+" + re.escape(sentence), text, re.DOTALL):
            continue  # citation in previous sentence
        if re.findall(
            r"\W(?:|[Ww]e|paper|authors?|et\. al\.|Section|Table|Figure)\W", sentence
        ):
            continue  # untypical words
        significant_sentences.append(sentence)

    return significant_sentences


def merge_ems(span):
    lsSmall = r"(?:a|an|at|are|for|is|can|in|of|to|,|-)"
    span = re.sub(r"</em>( ?" + lsSmall + r" ?)<em>", r"\1", span)
    return span


def compare_and_decide(sent_doc, sent_web):
    # either one  long or several small bolds
    doc_words = split2words(sent_doc)
    # long_words = [ x for x in doc_words if len(x) > 2 ]
    # print("sent_web:", sent_web)

    is_plagiarsim = 0
    sent_web = merge_ems(sent_web)
    bold_spans = re.findall(r"<em>(.*?)</em>", sent_web)
    total_bold_words = 0
    long_bolds = 0
    for bold in bold_spans:
        # print("bold-span:", bold)
        bold_words = split2words(bold)
        word_count = len(bold_words)
        total_bold_words += word_count
        if word_count >= 2 and all(len(w) > 2 for w in bold_words):
            long_bolds += 1
        if word_count >= 4 and bold in sent_doc:
            is_plagiarsim = True
        if word_count >= 6:
            is_plagiarsim = True

    if total_bold_words > len(doc_words) * SIMILAR_THRESHOLD and long_bolds > 3:
        is_plagiarsim = True

    return is_plagiarsim


def checkPlagiarismSentence(sent):

    results = google_search(sent)
    output = ""
    plagtext = ""

    is_plagiarsim = False
    for res in results:
        html_text = merge_ems(res["desc"])
        desc_text = html.unescape(html_text)
        if compare_and_decide(sent, desc_text):
            is_plagiarsim = True
            print("\n\033[1mPotential Plagiarism!\033[0m")
            google_sent = re.sub(
                "<em>(.*?)</em>", "\033[95m" + r"\1" + "\033[0m", desc_text
            )
            print('Document: "{}"\n'.format(sent))
            print('Web:      "{}"\n{}\n'.format(google_sent, res["url"]))
            plagtext += '<li>"{}"\n<a href="{}">{}</a></li>\n'.format(
                desc_text, res["url"], res["url"]
            )

    if is_plagiarsim:
        output += '<strong class="crit">Web Matches:</strong> "{}…"\n'.format(
            sent[: min(len(sent), 120)]
        )
        output += "<ul>" + plagtext + "</ul>"
    else:
        output += '<strong class="good">No Matches:</strong> "{}…"\n'.format(
            sent[: min(len(sent), 120)]
        )
        print('\033[32mSentence OK\033[0m: "{}..."'.format(sent[: min(len(sent), 80)]))
    return output


# ===========================================================
# Main
# ===========================================================

import random


def checkPlagiarism(text):

    # strip references
    div = int(len(text) * 0.7)
    text = text[:div] + re.sub(
        r"(?:R ?EFERENCES|Bibliography|References)(?:.|\n)*", "", text[div:]
    )

    sigsentences = findSignificantSentences(text)
    # [print(s) for s in sigsentences]

    num_sentences = min(SENTENCES_MAX, len(sigsentences))
    print(
        "\n\nChecking for plagiarism...\n----------------------------------------------------"
    )
    output = "Found {} significant sentences, checking {} of them...\n".format(
        len(sigsentences), num_sentences
    )
    print(output)

    for sent in random.sample(sigsentences, num_sentences):
        sent = sent.replace("\n", " ")
        output += checkPlagiarismSentence(sent)
        time.sleep(QUERY_WAIT_SECONDS)

    return output
