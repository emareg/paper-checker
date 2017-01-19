# Paper check
#
# Quick & dirty python script to check a paper for common English mistakes


reDoubled = r" ((\w+)\s+\2) "

reHyphen = r'(worst case|run time|high level|safety critical)'

reCommaBefore = r'\w+\s+(which|such as|because)\s+'

reNoCommaAfter = r'\w+\s+(that)\s+'

reCommaAfterDot = r'\.\s+(First|Additionally|However|Furthermore|As a result|For example|In general)\s+(\w+)'


nonScientific = [
	("ass", "as"), 
	('angel', 'angle'),
	('fir', 'for')
	]


COL_RED = '\033[93m'
COL_NONE = '\033[0m'

def red( string ):
	return '\033[91m'+string+'\033[0m'


def readInputFile( fileName ):
	# Open file as file object and read to string
	sourceFile = open(fileName,'r')

	# Read file object to string
	sourceText = sourceFile.read()

	# Close file object
	sourceFile.close()

	# return
	return sourceText



def askAction( ln, msg, match, replace):
	print ("Line " + str(ln) + ": " + msg + ": " + match)
	
	reply = input("What should we do? (Enter: nothing, r: repair, q:quit) : ")
	if(reply == "r"):
		print ("ok")
	elif(reply == "q"):
		sys.exit(0)


def findRegEx( regex, text ):
	matches = []
	regex = regex + r'|(\n)'
	line_num = 1
	line_start = 0
	for mo in re.finditer(regex, text):
		if mo.group(mo.lastindex) == '\n':
			line_start = mo.end()
			line_num += 1
		else:
			column = mo.start() - line_start
			matches.append( (line_num, column, mo) )	
	return matches


def checkDoubledWords(text, ln):
	matches = re.findall(r" ((\w+)\s+\2) ", text)
	for match in matches:
		askAction( ln, "Found doubled word", match[0], "")


def checkAnA(text, ln):
	#regex finiter: https://docs.python.org/3/library/re.html#writing-a-tokenizer
	matches = re.findall(" ((a) ((?:a|o|i|e[^u]|u[^s])\w+))", text)
	for match in matches:
		askAction( ln, "Possible misuse of \"a\", could be \"an\"", match[0], "")
	matches = re.findall(r' ((an) ((?:[^aoeiu\\]|us)\w+))', text)
	for match in matches:
		askAction( ln, "Possible misuse of \"an\", could be \"a\"", match[0], "")
	matches = re.findall(" (a) (hour)", text)
	for match in matches:
		askAction( ln, "Possible misuse of \"a\", could be \"an\"", match[0], "")

def checkCommas( text ):
	matches = findRegEx( reCommaAfterDot , text )
	for match in matches:
		showLine = ". " + match[2].group(1) + red(", ") + match[2].group(2)
		askAction( match[0], "Possible missing comma: ", showLine, "")


def checkHyphen( text ):
	matches = findRegEx( reHyphen , text )
	for match in matches:
		showLine = match[2].group(0).replace(" ", red("-"))
		askAction( match[0], "Possible missing hyphen: ", showLine, "")	

def checkCapitalPeriod( text ):
	matches = findRegEx( "(\w\w+(?:\.|!)\s+[a-z]\w+)" , text )
	for match in matches:
		askAction( match[0], "Possibly missing capital letter after period: ", match[2].group(0), "")	


def checkNonScientific( text ):
	#if any(word[1] in text for i, word in enumerate(nonScientific)):
	lines = text.split('\n')
	for i, word in enumerate(nonScientific):
		for num, line in enumerate(lines):
			if( " "+word[0]+" " in line ):
				askAction( num, "Non scientific word \"" + word[0] +"\": \n", line, word[1])	





def checkLine( text, ln ):
	checkDoubledWords(text, ln)
	checkAnA(text, ln)
	




def parseFile( fileName ):
	text = readInputFile( fileName )

	#checkCommas( text )
	checkHyphen( text )
	checkNonScientific( text )
	checkCapitalPeriod( text )

	# read file
	with open(fileName) as fp:
		for i, line in enumerate(fp):
			checkLine( line, i )


# Main Program
#############################################
import fileinput
import sys
import os
import re


# check arguments
args = sys.argv[1:]
if len(args) == 0:
	print("Usage: python paper-check.py FILE")
	sys.exit(0)

for arg in args:
	parseFile(arg)
