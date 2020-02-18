

# own functions
from lib.nlp import *         # language functions
from lib.cli import *
import re
import os
import zipfile
import sys




def parse_affix(word, affix):
    addwords = []
    pfxwords = [word]
    for char in affix:
        if char in 'AIUCEFK':
            # prefixes
            if char == 'A': pfxwords.append('re'+word) 
            elif char == 'I': pfxwords.append('in'+word)
            elif char == 'U': pfxwords.append('un'+word)
            elif char == 'C': pfxwords.append('de'+word)
            elif char == 'E': pfxwords.append('dis'+word)
            elif char == 'F': pfxwords.append('con'+word)
            elif char == 'K': pfxwords.append('pro'+word)

        # suffix
        else:
            for pfxword in pfxwords:
                if char == 'V': addwords.append(re.sub('e$|$', 'ive', pfxword))
                elif char == 'N': addwords.append(re.sub(r'(?<!ion)$', 'en', re.sub('y$', 'ication', re.sub('e$', 'ion', pfxword))))
                elif char == 'X': addwords.append(re.sub(r'(?<!ions)$', 'ens', re.sub('y$', 'ications', re.sub('e$', 'ions', pfxword))))
                elif char == 'H': addwords.append(re.sub(r'y$', 'ie', pfxword)+'th')  # 
                elif char == 'Y': addwords.append(adverb(pfxword)) # adverb
                elif char == 'G': addwords.append(re.sub(r'e$', '', pfxword)+'ing')  # gerund
                elif char == 'J': addwords.append(re.sub(r'e$', '', pfxword)+'ings')  # gerund
                elif char == 'D': addwords.append(re.sub(r'e$', '', re.sub(r'(?<=[^aeiou])y$', 'i', pfxword))+'ed') # past
                elif char == 'T': addwords.append(superlative(pfxword)) # superlative
                elif char == 'R': addwords.append(re.sub(r'e$', '', re.sub(r'(?<=[^aeiou])y$', 'i', pfxword))+'er')
                elif char == 'Z': addwords.append(re.sub(r'e$', '', re.sub(r'(?<=[^aeiou])y$', 'i', pfxword))+'ers')
                elif char == 'S': addwords.append(plural(pfxword))  # plural
                elif char == 'P': addwords.append(re.sub(r'(?<=[^aeiou])y$', 'i', pfxword)+'ness')  # 
                elif char == 'M': addwords.append(pfxword+'\'s') # noun
                elif char == 'B': addwords.append(re.sub(r'(?<=[^e])e$', '', pfxword)+'able') # adjective
                elif char == 'L': addwords.append(pfxword+'ment') # noun
        #elif char == 'R': addwords.append(comperative(word)) # comparative

    addwords += pfxwords    
    return addwords



def read_pos_dictionaries(folder):
    dictionary = {}
    files = [ 
        'en_basic.txt',
        'en_modal.txt',
        'en_adjectives.txt',
        'en_conjunction.txt',
        'en_letters.txt',
        'en_determiners.txt',
        'en_adposition.txt',
        'en_pronoun.txt',
        'en_irregular_verbs.txt',
        'en_regular_verbs.txt',
        'en_proper_nouns.txt',
        'en_nouns_extra.txt',
    ]

    folder = re.sub(r'/$', '', folder)
    for file in files:
        dictionary = read_dictionary(dictionary, folder+'/'+file)

    regverb_dict = {}
    read_dictionary(regverb_dict, folder+'/'+'en_regular_verbs.txt')
    for regverb in regverb_dict:
        dictionary[past(regverb)] = ''
        dictionary[plural(regverb)] = ''
        dictionary[gerund(regverb)] = ''

    noun_dict = {}
    read_dictionary(noun_dict, folder+'/'+'en_proper_nouns.txt')
    for noun in noun_dict:
        dictionary[plural(noun)] = ''


    return dictionary 



def read_dictionary(dictionary, dictfile):
    lines = ""
    try:
        fh = open(dictfile, 'r', encoding='utf8')
        lines = fh.read()
        #print(lines); return
        fh.close()
    except FileNotFoundError:
        try:
            arch = zipfile.ZipFile(sys.argv[0], 'r')
            fh = arch.open(dictfile[4:], 'r')
            lines = fh.read().decode("utf-8")
            fh.close()
        except FileNotFoundError:
            print("ERROR: Dictionary File '{}' not found. Install hunspell.".format(dictfile))


    for line in lines.splitlines():
        if dictfile[-4:] == '.dic':
            word, _, affix = line.strip().partition('/')
            dictionary[word] = ''
            for additional in parse_affix(word, affix):
                dictionary[additional] = ''
        else:
            words = line.strip().split(' ')
            for word in words:
                dictionary[word] = ''

    return dictionary   


def read_acronyms(acronyms, acronymfile):
    try:
        with open(acronymfile, 'r') as f:
            for line in f:
                line = line.strip()
                acronym = re.match(r'\W([A-Z0-9]{2,})', line)
                if acronym != None:
                    acronyms[acronym] = ''
    except FileNotFoundError:
        print("ERROR: Acronym File '{}' not found.".format(acronymfile))


class Correction:
     def __init__(self, line, column, match, suggestion, description):
        self.line = line
        self.col = column
        self.match = match
        self.sugg = suggestion
        self.desc = description


# todo: check hypen prefixes: semi- pre- intra- inter- re- dis mis- quasi- multi-
def check_words(dictionary, text):
    lines = text.splitlines(True)
    sentences = split2sentences( text )
    # for sentence in sentences:  
    #     words = split2words( sentence )   
    word_counter = {}
    corrections = [] 
    for idx,line in enumerate(lines):
        words = split2words( line )    
        for word in words:
            if word.isupper() or isNum(word): continue
            isCorrect = (word in dictionary)
            if not isCorrect:
                if word not in word_counter.keys(): 
                    word_counter[word] = 1
                else:
                    word_counter[word] += 1
                if word[0].isupper(): 
                    lowword = word[0].lower() + word[1:]
                    isCorrect = (lowword in dictionary)
                if not isCorrect and len(word) > 2:
                    matches = re.findall(r'\W'+word+r'\W', line)
                    match = ' '+word+' ' if len(matches) == 0 else matches[0]
                    sugg = suggest(dictionary, word)
                    if word_counter[word] < 5:
                        corrections.append(Correction(idx+1, 0, match, sugg, 'Possibly misspelled word.'))
                        askAction( idx, "Maybe misspelled word.", match, sugg)
                # print("Typo: '{}',  Sugg: {}".format(word, suggest(dictionary, word)))

    return corrections


def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'esianrtolcdugmphbyfvkwz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    capital = [word[0].upper()+word[1:]]
    return set(deletes + transposes + replaces + inserts + capital)


def suggest(dictionary, wrong):
    suggs = list(set(w for w in edits1(wrong) if w in dictionary))
    return '' if len(suggs) == 0 else suggs[0]



def checkSpelling( text ):

    print('\n\nChecking Spelling:\n----------------------------------------------------')

    dictionary = {}
    # dictionary = read_dictionary(dictionary, 'src/dictionary/en_US-scowl-70.dic')
    # dictionary = read_dictionary(dictionary, 'src/dictionary/en_US-scowl-60.dic')
    dictionary = read_dictionary(dictionary, 'src/dictionary/en_US-scowl-35.dic')
    #dictionary = read_dictionary(dictionary, '/usr/share/en_US.dic')
    dictionary = read_dictionary(dictionary, 'src/dictionary/academic.dic')
    dictionary = read_dictionary(dictionary, 'src/dictionary/en_US_names.dic')
    dictionary = read_dictionary(dictionary, 'src/dictionary/en_US_tech.dic')
    dictionary = read_dictionary(dictionary, 'src/dictionary/en_US_unit.dic')
    dictionary = read_dictionary(dictionary, 'src/dictionary/en_US_math.dic')
    dictionary = read_dictionary(dictionary, 'src/dictionary/names_geo.dic')
    dictionary = read_dictionary(dictionary, 'src/dictionary/names_people.dic')
    # dictionary = read_pos_dictionaries('src/dictionary/pos')
    #dictionary = read_dictionary(dictionary, 'src/dictionary/google-10000-english-usa-no-swears.txt')

    read_acronyms(dictionary, 'src/dictionary/acronyms.md')
    if dictionary == {}: return
    corrections = check_words(dictionary, text)
    return corrections


    # sentences = split2sentences( text )
    # for sentence in sentences:  
    #     words = split2words( sentence )
    #     for word in words:
    #         isCorrect = spellchecker.spell(word)
    #         if not isCorrect:
    #             print("Typo: ", word)
