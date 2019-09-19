
# Part of Speech (POS) module

# Despite the fact


from pos.dictionary import * 
from pos.POS_en import *

from lib.nlp import *




##########################################################################
# adj: tal
# noun: mn|son|ton|age|ipe|ime|[^n]g
# verb: ify|erve|[^aouie]ect|[^w]ide|

# verb-noun: ence


import re





reGerundExceptions = r'bring|ring|sing|'  # shorter than 2 chars prefix


# should be auto generated, or easy categorizing


lstIntroductoryPhrase = [ 'Actually','As a result','Additionally','Afterwards','Consequently','However','Hence','Finally','First','Furthermore','Therefore','Third(?:ly)?','For example','For (?:this|that) reason','Generally','In general','In fact','In (?:18|19|20)\d\d','In the past','Instead(?! of)','On the other hand','Nevertheless','Nowadays','On the contrary','Recently','Second(?:ly)?','What is more']



######################################################################################





def analyzeSentence( sentence ):
	if( isValidSentence(sentence) ):
		sentence = stripSimpleIntroductory(sentence)
		ses = splitSubsentences( sentence )
		for sentence in ses:
			words = splitWords( sentence )
			tw = tagWords (words )
			print(tw, "\n=====\n")
			analyzeTags( tw )



def analyzeSentences(text ):
	sentences = re.split(r'(?<=[^A-Z][^A-Z][.?!:])\s+(?=[A-Z])', text)
	for sentence in sentences:
		analyzeSentence( sentence )

def isValidSentence( sentence ):
	return ( len(sentence) > 25 and len(sentence) < 500)


def stripSimpleIntroductory( sentence ):
	reIntro = '(?:'+'|'.join(lstIntroductoryPhrase)+'),\s+'
	lstFragments = re.split( reIntro, sentence, 1 )
	if(len(lstFragments) > 1):
		return lstFragments[1]
	else: return lstFragments[0]


def splitSubsentences( sentence ):
	lstFragments = re.split( '[,;]', sentence )
	#lstFragments = re.split( '\(([^)]+)\)', sentence, 1 )
	#print(lstFragments)
	return lstFragments


def findSubject( sentence ):
	reDeterminer = '('+'|'.join(lstDeterminers)+')'
	re.search(reDeterminer)

def splitWords( sentence ):
	lstWords = re.split( '\s+|[,;:.]', sentence )
	return lstWords


def tokenize( text ):
	sentences = re.split(r'(?<=[^A-Z][^A-Z][.?:])\s+(?=[A-Z])', text)




# guess POS tag based on word pattern
def guessTag( word ):
	if(word in lstAdv or word[-2:] == 'ly'):
		tag = POS_TAG_ADVERB
	elif(re.match(reAdjective, word) or re.match(r'\w\w+-\w\w+', word)):
		tag = POS_TAG_ADJECTIVE
	elif(word[-2:] == 'ed' or word[-3:] == 'ing'):
		tag = POS_TAG_VERB
	elif(re.match(reNounPl, word)):
		tag = POS_TAG_NOUN_PL
	elif(re.match(reNounSgl, word)):
		tag = POS_TAG_NOUN
	else:
		tag = 'X'
	return tag



# universal
# Tag     Meaning      English Examples
# ADJ     adjective      new, good, high, special, big, local
# ADP     adposition      on, of, at, with, by, into, under
# ADV     adverb         really, already, still, early, now
# CONJ    conjunction      and, or, but, if, while, although
# DET     determiner, article      the, a, some, most, every, no, which
# NOUN    noun      year, home, costs, time, Africa
# NUM     numeral      twenty-four, fourth, 1991, 14:24
# PRT     particle      at, on, out, over per, that, up, with
# PRON    pronoun      he, their, her, its, my, I, us
# VERB    verb      is, say, told, given, playing, would
# .      punctuation marks      . , ; !
# X      other      ersatz, esprit, dunno, gr8, univeristy


POS_TAG_ADJECTIVE = 'J'
POS_TAG_ADVERB = 'ADV'
POS_TAG_CONJUNCTION = 'CONJ'
POS_TAG_NOUN = 'N'
POS_TAG_NOUN_PL = 'NPL'
POS_TAG_VERB = 'V'
POS_TAG_BASE_VERB = 'VB'
POS_TAG_MODAL_VERB = 'M'
POS_TAG_DETERMINER = 'DET'
POS_TAG_SYMBOL = 'SYM'
POS_TAG_PREPOSITION = 'ADP'
POS_TAG_PRONOUN = 'PRON'
POS_TAG_TO = 'TO'


POS_TAG_VERB_GERUND = 'g'



def tagWords( words ):
	taglist = []
	words[0] = words[0].lower()
	for word in words:
		if(word in lstDet):
			taglist.append( (word, POS_TAG_DETERMINER))
		elif(word in lstAdpos):
			taglist.append( (word, POS_TAG_PREPOSITION))
		elif(word in lstVerbBase):
			taglist.append( (word, POS_TAG_BASE_VERB))
		elif(word in lstAux):
			taglist.append( (word, POS_TAG_MODAL_VERB))
		elif(word in lstPronoun):
			taglist.append( (word, POS_TAG_PRONOUN))
		elif(word in lstSubConjunction or word in lstConjunction):
			taglist.append( (word, POS_TAG_CONJUNCTION))
		elif(word in lstAdjectives):
			taglist.append( (word, POS_TAG_ADJECTIVE))
		elif(word in lstRegularVerbs or word in [x[0] for x in lstIrregularVerbs]):  # check each element
			taglist.append( (word, POS_TAG_VERB))	
		elif(word[-2:] == 'ly' or word in lstAdv):
			taglist.append( (word, POS_TAG_ADVERB))
		elif(word in lstPropperNoun):
			taglist.append( (word, POS_TAG_NOUN))
		elif(word in [plural(x) for x in lstPropperNoun]):
			taglist.append( (word, POS_TAG_NOUN_PL))
		elif(word == 'to'):
			taglist.append( (word, POS_TAG_TO))
		else:
			guess = guessTag(word)
			taglist.append( (word, guess ))
			print("POS_TAG_X: ", word, guess)
	return taglist


def analyzeTags( tw ):
	tags = [x[1] for x in tw]
	tagstring = ''.join(tags)
	#print(tagstring)
	#if('Nn' in tagstring):
		#print(tw)
	if(re.match('m[^b]', tagstring)):  # modal without verb
		print(tw)
	#if(re.match('.*j*n*[nN][^p]b', tagstring)):
		#print(tw)
	#if( 'NNP,VB' in tagstring ):
		#print(tags)
		# todo: re.finiter

		# DET X X NN/NNP 
		# 1.NN [^PP]+ VB (is/are)
		# NN (that/which) VB
		# with/be NN 


