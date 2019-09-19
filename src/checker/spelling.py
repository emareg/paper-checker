
# import hunspell
# spellchecker = hunspell.HunSpell('/usr/share/hunspell/en_US.dic',
#                                  '/usr/share/hunspell/en_US.aff')



# own functions
from lib.nlp import *         # language functions
import re


def linecheck(word, dlist):
    if word in dlist:
        return None
    else:
        return word



def parse_affix(word, affix):
    addwords = []
    for char in affix:
        # prefixes
        if char == 'A': addwords.append('re'+word) 
        elif char == 'I': addwords.append('in'+word)
        elif char == 'U': addwords.append('un'+word)
        elif char == 'C': addwords.append('de'+word)
        elif char == 'E': addwords.append('dis'+word)
        elif char == 'F': addwords.append('con'+word)
        elif char == 'K': addwords.append('pro'+word)
        # suffix
        elif char == 'V': addwords.append(re.sub('e$|$', 'ive', word))
        elif char == 'N': addwords.append(re.sub(r'(<=[^ey])$', 'en', re.sub('y$', 'icaion', re.sub('e$', 'ion', word))))
        elif char == 'X': addwords.append(re.sub(r'(<=[^ey])$', 'ens', re.sub('y$', 'icaions', re.sub('e$', 'ions', word))))
        elif char == 'G': addwords.append(re.sub(r'e$', '', word)+'ing')  # gerund
        elif char == 'J': addwords.append(re.sub(r'e$', '', word)+'ings')  # gerund
        elif char == 'D': addwords.append(past(word)) # past
        elif char == 'S': addwords.append(plural(word))  # plural
        elif char == 'T': addwords.append(superlative(word)) # superlative
        elif char == 'R': addwords.append(re.sub(r'e$', '', re.sub(r'(<=[^aeiou])y$', 'i', word))+'er')
        elif char == 'Z': addwords.append(re.sub(r'e$', '', re.sub(r'(<=[^aeiou])y$', 'i', word))+'ers')
        elif char == 'Y': addwords.append(word+'ly') # adverb
        elif char == 'M': addwords.append(word+'\'s') # noun
        #elif char == 'R': addwords.append(comperative(word)) # comparative
    return addwords


def read_dictionary(dictfile):
    dictionary = {}

    try:
        with open(dictfile, 'r') as f:
            for line in f:
                word, _, affix = line.strip().partition('/')
                #(key) = 
                dictionary[word] = ''
                for additional in parse_affix(word, affix):
                    dictionary[additional] = ''
    except FileNotFoundError:
        print("ERROR: Dictionary File '{}' not found. Install hunspell.".format(dictfile))
    return dictionary   



def check_words(dictionary, text):
    sentences = split2sentences( text )
    for sentence in sentences:  
        words = split2words( sentence )
        words[0] = words[0].lower()
        for word in words:
            if word[0].isupper() or isNum(word): continue
            isCorrect = (word in dictionary)
            if not isCorrect:
                print("Typo: '{}'".format(word))






def checkSpelling( text ):

    dictionary = read_dictionary('/usr/share/hunspell/en_US.dic')
    if dictionary == {}: return
    check_words(dictionary, text)


    # sentences = split2sentences( text )
    # for sentence in sentences:  
    #     words = split2words( sentence )
    #     for word in words:
    #         isCorrect = spellchecker.spell(word)
    #         if not isCorrect:
    #             print("Typo: ", word)
