


SENTENCES_MAX = 7   # maximum analyzed sentences per document
QUERY_WAIT_SECONDS = 2  # wait time between google queries

SIMILAR_THRESHOLD = 0.7 



# imports
import re, sys, time
import html

from collections import Counter
from lib.stripper import *
from lib.nlp import *


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
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'de-DE,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }


def google_search( searchstr, num=10 ):
    import requests
    import urllib
    q = urllib.parse.quote_plus(searchstr)
    # todo: improve query: %2Bterm?


    #print("Requesting: ", q)
    s = requests.Session()
    url = 'https://www.google.com/search?q=' + q + '&ie=utf-8&oe=utf-8'    # &num={}'.format(num)
    html_res = s.get(url, headers=headers_Get).text


    RES_START='>Webergebnisse</h2>'             # '<div id="search">'
    RES_END='<div id="foot'
    ENTRY_DEL='<div class="g">'
    html_res = html_res[html_res.index(RES_START)+len(RES_START):html_res.index(RES_END)]

    output=[]

    results = re.findall( r'<div class="g">(.*?)(?=><div class="g">)', html_res, re.DOTALL)
    for result in results:
        #print("Result:", result)
        title = re.findall( r'<h3 class=.*?>(.*?)</h3>', result, re.DOTALL)[0]
        url = re.findall( r'<div class="r">.*?<a href="(.*?)"', result, re.DOTALL)[0]
        desc = re.findall( r'<span class="st">(?:<span class="f">.*?</span>)?(.*?)</span>', result, re.DOTALL)[0]
        output.append({'title': title, 'url': url, 'desc': desc})

    return output




def findSignificantSentences( text ):
    sentences = split2sentences( text )
    all_words = []
    for sentence in sentences:
        words = split2words( sentence )
        all_words += [x.lower() for x in words]

    ##print(all_words)
    unique_words = set(all_words)
    long_words = [ x for x in all_words if len(x) > 5 ]
    word_counts = Counter(long_words)
    common_word_counts = word_counts.most_common(8)
    #print("Significant Words: ", common_word_counts)

    common_words = [wc[0] for wc in common_word_counts]

    significant_sentences = []
    for idx, sentence in enumerate(sentences):
        words = split2words( sentence )
        if len(words) < 17 or len(words) > 20: continue
        if not any(w.lower() in common_words for w in words): continue
        if re.findall(r'\\cite|\[\d\d?\]', sentence): continue # citation in sentence
        if re.findall(r'\\cite|\[\d\d?\]\.\s+'+sentence, text, re.DOTALL): continue  # citation in previous sentence
        if re.findall(r'\W(?:paper|authors?|et\. al\.)\W', sentence): continue  # untypical words
        significant_sentences.append(sentence)

    return significant_sentences



def merge_ems( span ):
    lsSmall = r'(?:a|an|at|is|in|of|to|,|-)'
    span = re.sub(r'</em>( ?'+lsSmall+r' ?)<em>', r'\1', span)
    return span


def compare_and_decide( sent_doc, sent_web ):
    # either one  long or several small bolds
    doc_words = split2words( sent_doc )
    #long_words = [ x for x in doc_words if len(x) > 2 ]

    is_plagiarsim = 0
    sent_web = merge_ems(sent_web)
    bold_spans = re.findall(r'<em>(.*?)</em>', sent_web)
    total_bold_words = 0
    long_bolds = 0
    for bold in bold_spans:
        bold_words = split2words(bold)
        word_count = len(bold_words)
        total_bold_words += word_count
        if word_count >= 2 and all(len(w) > 2 for w in bold_words): long_bolds += 1
        if word_count >= 4 and bold in sent_doc: is_plagiarsim = True
        if word_count >= 6 : is_plagiarsim = True


    if total_bold_words > len(doc_words)*SIMILAR_THRESHOLD and long_bolds > 3:
        is_plagiarsim = True

    return is_plagiarsim


def checkPlagiarismSentence ( sent ):

    results = google_search(sent)

    is_plagiarsim = False
    for res in results:
        html_text = merge_ems(res['desc'])
        desc_text = html.unescape(html_text)
        if compare_and_decide( sent, desc_text ):
            is_plagiarsim = True
            print('\n\033[1mPotential Plagiarism!\033[0m')
            google_sent = re.sub('<em>(.*?)</em>', '\033[95m'+r'\1'+'\033[0m', desc_text)
            print('Document: "{}"'.format(sent))
            print('Web:      "{}"\n{}\n'.format(google_sent, res['url']))

    if not is_plagiarsim:
        print('\033[32mSentence OK\033[0m: "{}..."'.format(sent[:min(len(sent), 80)]))



# ===========================================================
# Main
# ===========================================================




def checkPlagiarism( text ):


    sigsentences = findSignificantSentences(text)
    #[print(s) for s in sigsentences]

    num_sentences = min(SENTENCES_MAX, len(sigsentences))
    print("\n\nChecking for plagiarism...\n----------------------------------------------------")
    print("Found {} significant sentences, checking {} of them...".format(len(sigsentences), num_sentences))

    for sent in sigsentences[:num_sentences]:
        checkPlagiarismSentence(sent)
        time.sleep(2)








