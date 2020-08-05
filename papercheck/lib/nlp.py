# natural language processing

import re


def split2sentences(text):
    final_sents = []
    #  sents = re.split(r'(?<![.](?:\w\.))(?<![A-Z][a-z][a-z][.])(?<![A-Z][a-z][.])(?<=[.!?])(?:\s+(?=[A-Z][^.,\d])|\s*\n\s*\n(?![a-z]))', text)
    sents = re.split(
        r"(?<![.](?:\w\.))(?<![A-Z][a-z][a-z][.])(?<![A-Z][a-z][.])(?<![A-Z][.])(?<=[.!?])(?:“?”?\s+(?=„?“?[A-Z][^.,\d])|\s*\n\s*\n(?![a-z]))",
        text,
    )
    for idx, sent in enumerate(sents):
        new_sents = re.findall(
            r"(?:\s|^)([A-Z][^.,\d].*?\S\S[.?!])(?=>\s+[A-Z]|\W*\n\n|\s*$)",
            sent,
            re.DOTALL,
        )  # double check
        if new_sents:
            final_sents += new_sents
    return final_sents


def split2tokens(sentence):
    return list(
        filter(
            None,
            re.split(
                r'\s+|((?<=\s)[(\[\{"\'](?=\w)|(?<=\w)[?!:;,\-\)\]\}"\'](?=\s)|(?<=\w)[/](?=\w)|(?<=\w)[.]$)',
                sentence,
            ),
        )
    )


def split2words(sentence):
    # return re.findall(r'(?<=[\s,.!?“”\"\'\(\)\[\]\{\}])[a-zA-Z][0-9a-zA-Z\'\-]*(?=[\s,.!?“”\"\'\(\)\[\]\{\}])', sentence)
    return re.findall(r"-?\d+(?:\.\d+)?|[a-zA-Z][0-9a-zA-Z\']*", sentence)  # \-


def singular(string):
    if len(string) > 4 and string[-3:] == "ies":
        return string[:-3] + "y"
    else:
        return string[:-1]


def plural(string):
    """ returns the plural of a word """
    splural = ""
    if string[-1] in "sxz" or (string[-1] == "h" and string[-2] in "sc"):
        splural = string + "es"
    elif string[-1] == "y" and string[-2] not in "aeiou":
        splural = string[:-1] + "ies"
    else:
        splural = string + "s"
    return splural


def past(string):
    if len(string) < 3:
        return string
    past = ""
    if string[-1] == "e":
        past = string + "d"
    elif string[-1] == "y" and string[-2] not in "aeiou":  # y -> ied
        past = string[:-1] + "ied"
    # elif(string[-2] == 'n' and string[-1] == 'd'):    # nd -> nt
    #     past=string[:-1]+'t'
    # elif (
    #     string[-2] in "aeiou"
    #     and string[-1] not in "aeiouxw"
    #     and string[-3] not in "aeiou"
    # ):  # double consonant
    #     if string[-1] == "c":
    #         past = string + "ked"
    #     else:
    #         past = string + string[-1] + "ed"
    else:
        past = string + "ed"
    return past


def adverb(word):
    if word[-2:] == "ic":
        return word + "ally"
    elif len(word) > 5 and word[-3:] == "ble":
        return word[:-2] + "ly"
    elif word[-1] == "y":
        return word[:-1] + "ily"
    else:
        return word + "ly"


def gerund(word):
    result = ""
    if word[-1] == "e":
        if word[-2] == "i":
            result = word[:-2] + "ying"
        elif word[-2] not in "eoy":
            result = word[:-1] + "ing"
        else:
            result = word + "ing"
    else:
        result = word + "ing"
    return result


def comperative(word):
    cmprv = ""
    if word[-1] == "e":
        cmprv = word + "r"
    elif word[-1] == "y" and word[-2] not in "aeiou":
        cmprv = word[:-1] + "ier"
    else:
        cmprv = word + "er"
    return cmprv


def superlative(word):
    sup = ""
    if word[-1] == "e":
        sup = word + "st"
    elif word[-1] == "y" and word[-2] not in "aeiou":
        sup = word[:-1] + "iest"
    else:
        sup = word + "est"
    return sup


def possessive(word):
    if word[-1] in "sz":
        return word + "'"
    else:
        return word + "'s"


def syllables(word):
    # count vowels, split by consonants
    # if last letter is vowel, does not count, except there are 3 consonants before it: e.g. simple
    # hire, me, file
    count = 0
    vowels = "aeiouy"

    if word is None:
        return 0
    if len(word) == 0:
        return 0
    word = word.lower()

    #                      1 syllable                   | ex.  | ending  e  e.g. move                               |   cvc (cv)                                          |  cle  e.g. sim-ple
    syls = re.findall(
        r"(^[^aeiouy]*[aeiouy]+[^aeiouy]*$|nique$|[^aeiouy]*[aeiouy]+(?:[^aeiouy]*[^aeiouyl]e|le|ved)$|[^aeiouy]*[aeiouy]+[^aeiouy]*?(?=[^aeiouy][aeiouy]|$)|[^aeiouy]le$)",
        word,
    )
    if len(syls) == 0:
        syls = [word]

    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    if len(re.findall("[aeiouy]le$|[^l]e$", word)) > 0:
        count -= 1
    if count == 0:
        count = 1  # e.g. 'the'

    # if len(syls) != count: print (word+', '+str(count)+', '+str(syls))
    return len(syls)


def infinitive(word):
    infinitive = ""
    if word[-1] == "d" and word[-2] == "e":
        infinitive = word[:-2]
    return infinitive


def isNum(word):
    return len(re.findall(r"-?\d+(?:\.\d+)?", word)) != 0


def num2word(num):
    if isinstance(num, str):
        num = int(num)
    if 0 <= num <= 12:
        words = [
            "zero",
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
            "ten",
            "eleven",
            "twelfe",
        ]
        return words[num]
