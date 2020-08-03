# universal POS
# S Tag     Meaning      English Examples
# J ADJ     adjective      new, good, high, special, big, local
# P ADP     adposition      on, of, at, with, by, into, under
# A ADV     adverb         really, already, still, early, now
# C CONJ    conjunction      and, or, but, if, while, although
# D DET     determiner, article      the, a, some, most, every, no, which
# N NOUN    noun      year, home, costs, time, Africa
# U NUM     numeral      twenty-four, fourth, 1991, 14:24
# R PRT     particle      at, on, out, over per, that, up, with
# R PRON    pronoun      he, their, her, its, my, I, us
# V VERB    verb      is, say, told, given, playing, would
# S .      punctuation marks      . , ; !
# X X      other      ersatz, esprit, dunno, gr8, univeristy



def regexFromLst(lst):
    # for idx,item in lst:
    reglist = ["[" + x[0] + x[0].upper() + "]" + x[1:] for x in lst]
    return "(?:" + "|".join(reglist) + ")"


## Adposition
# -----------------------------------------------------------
# Definition: includes preposition, postposition, and circumposition
# An adposition does belong to a nound and not a verb (would be particle/adverb)

# lstAdpos = ['about', 'all', 'as', 'at', 'after', 'by', 'between', 'from', 'for', 'in','into', 'of', 'on', 'over', 'per', 'that', 'than', 'through','towards', 'under', 'unless', 'until', 'upon', 'with', 'without']
lstAdpos = [
    "about",
    "at",
    "after",
    "by",
    "between",
    "from",
    "for",
    "in",
    "into",
    "of",
    "on",
    "over",
    "per",
    "than",
    "through",
    "towards",
    "under",
    "unless",
    "until",
    "upon",
    "with",
    "without",
]


reAdpos = regexFromLst(lstAdpos)
rePrep = regexFromLst(lstAdpos)


## Particle
# -----------------------------------------------------------
# particle: belongs to a verb to modify its meaning. E.g. to show off is different from to show

lstParticle = [
    "away",
    "at",
    "back",
    "backwards",
    "down",
    "downwards",
    "forward",
    "from",
    "for",
    "in",
    "of",
    "off",
    "on",
    "out",
    "over",
    "to",
    "through",
    "towards",
    "up",
    "upwards",
]
reParticle = regexFromLst(lstParticle) + "$"
rePart = regexFromLst(lstParticle)


## Pronoun
# -----------------------------------------------------------

lstPron1 = ["I"]
lstPron1 = ["you"]
lstPron3 = ["he", "she", "it"]

lstPronoun = [
    "hers",
    "herself",
    "he",
    "him",
    "himself",
    "hisself",
    "I",
    "it",
    "itself",
    "me",
    "myself",
    "one",
    "oneself",
    "ours",
    "ourselves",
    "ownself",
    "self",
    "she",
    "thee",
    "theirs",
    "them",
    "themselves",
    "they",
    "us",
    "we",
    "who",
    "which",
    "you",
]
lstPronounPos = ["her", "his", "mine", "my", "our", "ours", "their", "your", "its"]
rePronoun = regexFromLst(lstPronoun + lstPronounPos) + "$"


## Quantifiers
# -----------------------------------------------------------
# Definition: before a noun

lstQuantifier = [
    "all",
    "any",
    "enough",
    "less",
    "a lot of",
    "lots of",
    "more",
    "most",
    "no",
    "none of",
    "some",
]
reQuantifier = regexFromLst(lstQuantifier)


## Determiners
# -----------------------------------------------------------
reTheDet = "(:?[Aa]n?|[Aa]nother|[Aa]ny|[Mm]y|[Oo]ur|[Mm]any|[Nn]o|[Ss]ome|[Tt]he|[Tt]heir|[Tt]his|[Tt]hese|[Tt]hose)"

lstDetSgl = ["a", "an", "another", "each", "every", "this"]
lstDetPl = ["all", "both", "many", "most", "several", "some", "these", "those"]
lstDetExtra = ["any", "the", "no"]
# lstDet = [ 'all', 'a', 'an', 'another', 'any', 'both', 'each', 'either', 'every', 'half', 'la', 'less', 'many', 'more', 'most', 'much', 'neither', 'no', 'our', 'several', 'some', 'such', 'that', 'the', 'these', 'this', 'those', 'which']
lstDet = lstDetSgl + lstDetPl + lstDetExtra + lstPronounPos

lstDeterminer = lstDet
# reDeterminer = regexFromLst(lstDet+lstPronounPos)+'$'
reDetSgl = regexFromLst(lstDetSgl)
reDetPl = regexFromLst(lstDetPl)
reDet = regexFromLst(lstDet)


## Numbers
# -----------------------------------------------------------

lstNum = [
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
]

reNum = r"(?:\+?-?\d+(?:\.\d+)?|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen)$"


## Symbols
# -----------------------------------------------------------

rePunctuation = r"[.?!,;:]"
reSym = r'(?:[.,;:!?"\'`(){}]|[\-\+*/%]|[$]|\'\'|``|\-\-)$'


## Conjunction
# -----------------------------------------------------------

lstSubConjunction = [
    "as",
    "after",
    "although",
    "as \w\w+ as",
    "because",
    "before",
    "but",
    "even",
    "how",
    "if",
    "in order to",
    "once",
    "since",
    "so that",
    "that",
    "though",
    "unless",
    "until",
    "when",
    "where",
    "whether",
    "why",
]
reSubConjunction = regexFromLst(lstSubConjunction)  # FIX: +'$'

lstConjunction = [
    "and",
    "minus",
    "nor",
    "or",
    "plus",
    "so",
    "times",
    "versus",
    "vs.",
] + lstSubConjunction
reConjunction = regexFromLst(lstConjunction) + "$"


## Adverb
# -----------------------------------------------------------
# Definition: belongs to a verb

# prefix: re pro in
reAdverb = r"\w\w+ly"  # exceptions: fly, comply, (only), apply, rely
lstAdvTime = [
    "again",
    "first",
    "later",
    "never",
    "now",
    "often",
    "seldom",
    "still",
    "soon",
    "then",
]
lstAdvPlace = ["around", "everywhere", "here", "there", "nearby", "outside"]
lstAdvDegree = [
    "almost",
    "always",
    "also",
    "enough",
    "further",
    "least",
    "many",
    "not",
    "too",
    "quite",
    "rather",
    "very",
]
lstAdvMisc = ["due", "far", "thus", "yet", "well"]
lstAdv = lstAdvTime + lstAdvPlace + lstAdvDegree + lstAdvMisc
reAdv = r"(?:\w\w+ly|" + regexFromLst(lstAdv) + r")"


## Adjective
# -----------------------------------------------------------
# todo: more words with 'al'
# hypen words: hash-based
# check ent, like

lstAdjectiveExtra = [
    "able",
    "bad",
    "false",
    "few",
    "general",
    "great",
    "good",
    "large",
    "long",
    "new",
    "only",
    "other",
    "own",
    "same",
    "small",
    "smaller",
    "true",
]

reAdjectiveExtra = regexFromLst(lstAdjectiveExtra)
reSuffixAdjective = r"\w{3,}-\w{3,}ed|\w\w+(?:ous|ant|[liur]ent|bare|[ai]ble|[st]ive|ful|\wless|[^i]ty|ic|ial|ian|ical|[mnrt]al|some|ional|[^e]ry|ish)"

reAdjective = "(?:" + reAdjectiveExtra + "|" + reSuffixAdjective + ")"


## Verb
# -----------------------------------------------------------

lstVerbBase = [
    "be",
    "been",
    "is",
    "are",
    "was",
    "were",
    "has",
    "have",
    "had",
    "need",
    "get",
    "got",
    "do",
    "does",
    "did",
    "done",
    "make",
    "makes",
    "made",
]
lstVerbCommon = [
    "give",
    "gave",
    "given",
    "go",
    "see",
    "seen",
    "seem",
    "set" "show",
    "work",
    "use",
]

lstModal = [
    "can",
    "cannot",
    "could",
    "may",
    "might",
    "must",
    "shall",
    "should",
    "will",
    "would",
]
lstAux = lstModal + lstVerbBase  # modal + be, do, have
reModal = regexFromLst(lstModal)
reAux = regexFromLst(lstAux)


reInfinitve = r"\w\w+(?:yze|lize|cate|ise|ify|ose|ive|rve|ate|re|mit)"
reGerund = r"\w\w\w+ing"  # exceptions: xxthing, during, timing
rePerfect = r"\w\w\w+ed|\w\w+ied"
reVerb3rd = r"\w\w+es|\w\w+ies"
reSuffixVerb = r"(\w\w+ed|\w\wied|\w\w+(?:yze|lize|cate|ise|ify|ose|ive|rve|ate|re|mit)|\w\w\w+ing)$"

reVerb = (
    "(?:"
    + reSuffixVerb
    + "|"
    + regexFromLst(lstVerbBase + lstVerbCommon + lstAux)
    + ")$"
)


## Noun
# -----------------------------------------------------------

# check: me, ery, [siv]al, ity,ty , sis, ngle, eer, ict 	EX: resource, protocol, candidate
# Wrongs: Thus, they, However


reSuffixNoun = r"\w\w+(?:a|f|i|cy|me|or|age|ion|ium|omy|ver|ism|ght|ure|one|[ltr]ist|[ea]nce|[cn]ess|ican|[clv]ity|logy|ship|here|ment|[^o]us|[^aeiou]em|[emnpt]er|[oae][oa][dmnprkt]|[gwy]ear)"
rePrefixNoun = r"(?:[A-Z][a-z]{3,}|[A-Z]{2,4})"
reSuffixNounPl = reSuffixNoun.replace("i|", "")  # 'is'
reSuffixNounPl = reSuffixNoun.replace("y|", "ies|")
reSuffixNounPl = reSuffixNounPl.replace("s|", "se|")
reSuffixNounPl = reSuffixNounPl.replace(u"|", "s|")  # re.sub(r'([^ys])\||\)', '\1s')
reSuffixNounPl = reSuffixNounPl.replace(")", "|ings)")

reNounSgl = "(?:" + rePrefixNoun + "|" + reSuffixNoun + ")"
reNounPl = "(?:" + rePrefixNoun + "s|" + reSuffixNounPl + ")"
reNoun = "(?:" + reSuffixNoun + "|" + reSuffixNounPl + r")"
