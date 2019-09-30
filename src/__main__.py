# TechTeXTagger
# TechTexCheck
# TechDocCheck
# ScriptCheck
# techtextcheck
# papercheck
#
# Quick & dirty python script to check a paper for common English mistakes


# Feature Wishlist:
# - detection of american or british english
# - detection Titles and consistent style (capital or not)  .
# - detection of I/We 
# - detection of grammar errors with be/was/were   DONE
# - detection of plural errors "a cars"          DONE
# - check "to" + passive
# - check "to small, to large"                  DONE
# - check confused verb/noun: the/a + verb
# - check for unnecessary terms: "it is clear", "and so on"  DONE
# - check vague quantifiers such as  "very", "most", "many" "a large number"
# - check Figure in capital
# - check for inconsistent terms:  block chain, blockchain, block-chain, chain of blocks

# - check adposition at the end
# - check noun cluster

# command line argument: improvements or only mistakes

# if im präsens → 2. teil in future; if im perfekt → 2. teil in präsens
# If $\Delta t$ is passed as argument, the time dependence is made obvious for the caller. 
# If someone looks over the code later, subprograms that depend on time will be easy to spot.



# not found:  
# ... by but ... => comma or mistake
# is spend => is spent
# paranthesis => parantheses
# ... consensus based ... consensus-based (always -based?)


# Statistics: http://textalyser.net/index.php?lang=en#analysis



# Settings
#===========================================

ANALYZE_SENTENCE = False   # analyze sentence structure, experimental
CFG_INTERACTIVE = False   # ask for action after each error
CFG_PRINT_INPUT = False   # print the intput after pre-processing



# import
#===========================================

import fileinput
import sys
import os
import re
from argparse import ArgumentParser



# own functions
from checker.grammar import checkGrammar, checkStyle
from checker.tex import checkTeX
from checker.spelling import checkSpelling
from checker.plagiarism import checkPlagiarism

from lib.stripper import *
from textstats import showStats



# global state variables
# ==========================================================
outputLines = []
wasCorrectionMade = False




# helper functions
######################################################################################



def readInputFile( fileName ):
    ext = fileName.lower().split('.')[-1]
    inFileHandler = open(fileName,'rb')

    if ext == "pdf":
        import os, subprocess
        SCRIPT_DIR = os.getcwd()
        args = ["/usr/bin/pdftotext", '-enc', 'UTF-8', "{}/{}".format(SCRIPT_DIR, fileName), '-']
        res = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        text = res.stdout.decode('utf-8')
        text = re.sub(r'(?<=\n)\w\w?(?=\n)', '', text)

    elif ext in ["txt", "tex", "md"]:     
        text = inFileHandler.read().decode("utf-8")
        inFileHandler.close()

    else:
        raise ValueError("unknown extension: "+ext)


    text = re.sub(r'\s(\w{2:7})-\n(\w{2:7})\s', r' \1\2\n', text)

    return text



def writeOutputFile( fileName, text ):
    reply = ''
    while( reply == '' ):
        reply = input("Should the output file "+fileName+" be written? [y/n]")
    if(reply == "y"):
        with open(fileName, "w+") as f:
            f.write(text)



def markCorrections( lines, corrections, cssclass):
    corrected_linenums = ()
    lines = ''.join(lines)
    #print(lines)

    for corr in corrections:
        corrected_linenums += (corr.line,) 
        lines = lines.replace(corr.match, "<span class=\"corr "+cssclass+"\" title=\"{}\">{}</span>".format(corr.desc+" Suggestion: '"+corr.sugg.replace('\n', ' ').strip()+"'", corr.match)) 


        # print("CORR:", corr.line, lines[corr.line], corr.match)
        # print("lines[corr.line-1]", lines[corr.line-1])
        
        # corrected_line = lines[corr.line-1].replace(corr.match, " <span class=\"corr "+cssclass+"\" title=\"{}\">{}</span>".format(corr.desc+" Suggestion: '"+corr.sugg.strip()+"'", corr.match)) 
        # if corrected_line == lines[corr.line-1]:
        #     corr.match = corr.match.replace('\n', ' ')
        #     twolines = ''.join(lines[corr.line-1:corr.line+1])
        #     twolines = twolines.replace(corr.match, " <span class=\"corr "+cssclass+"\" title=\"{}\">{}</span> ".format(corr.desc+" Suggestion: '"+corr.sugg.strip()+"'", corr.match))
        #     print(twolines)
        #     lines[corr.line-1], lines[corr.line] = twolines.splitlines(True)
        # else:
        #     lines[corr.line-1] = corrected_line

    lines = lines.splitlines(True)
    return lines, corrected_linenums


def writeHTMLreport( lines, crit_linenums = [], warn_linenums = [] ):
    head = '''
<html>
  <head>
    <title>Report of papercheck</title>
    <style>body{{font-family: monospace;}}
    body{ font-family: monospace; } 
    td{ vertical-align: top; } 
    .ln{display: inline-block;width: 50px;user-select: none;}
    .corr{font-weight:bold;cursor:pointer;}
    .corr:hover {background-color: yellow;}
    span.err{color:Magenta;}
    span.crit{color:red;}
    span.warn{color:orange;}
    </style>
  </head>
    '''


    out_lines = "<table><tbody>"
    for num,line in enumerate(lines):
        if num+1 in crit_linenums: 
            out_lines += "<tr><td><span class=\"ln crit\">" + str(num+1) + "</span></td><td>" + line + "</td>\n"
        elif num+1 in warn_linenums: 
            out_lines += "<tr><td><span class=\"ln warn\">" + str(num+1) + "</span></td><td>" + line + "</td>\n"
        else:
            out_lines += "<tr><td><span class=\"ln\">" + str(num+1) + "</span></td><td>" + line + "</td>\n"
 
    out_lines += "</table></tbody>"


    out_lines = re.sub(r'(\\\w+)(?=\W)', r'<span style="color:blue;">\1</span>', out_lines)
    #out_lines = re.sub(r'(\n[^%]*?)([{}])', r'\1<span style="color:blue;">\2</span>', out_lines)
    out_lines = re.sub(r'(\\\\)', r'<span style="color:blue;">\1</span>', out_lines)
    out_lines = re.sub(r'(?<=[^\\])(%.*?)(?=\n)', r'<span style="color:gray;">\1</span>', out_lines)


    output = head + "<body>\n{}</body>\n</html>".format(out_lines)
    with open('papercheck_report.html', "w+") as f:
        f.write(output)    





# main parsing function
######################################################################################

def parseFile( fileName, args ):
    fileBaseName, ext = os.path.splitext(fileName)

    text = readInputFile( fileName )


    global outputLines
    outputLines = text.splitlines(True)
    crit_linenums = ()
    warn_linenums = ()


    # process TeX
    if fileName.endswith('.tex'):
        checkTeX( text )  
        text = stripTeX( text, True )


    if CFG_PRINT_INPUT:
        for idx, line in enumerate(outputLines):
            print("#{}: {}".format(idx, line), end='')
        

    # show stats
    showStats(text)

    #regex finiter: https://docs.python.org/3/library/re.html#writing-a-tokenizer
    if ANALYZE_SENTENCE:
        checkSentences( text )


    # spell check
    if args.spell:
        corrections = checkSpelling(text)
        outputLines, linenums = markCorrections(outputLines, corrections, "err")
        warn_linenums += linenums


    # grammar check
    if args.grammar:
        corrections = checkGrammar( text )
        outputLines, linenums = markCorrections(outputLines, corrections, "crit")
        crit_linenums += linenums

    # style check
    if args.style:
        corrections = checkStyle( text )
        outputLines, linenums = markCorrections(outputLines, corrections, "warn")
        warn_linenums += linenums

    # plagiarism check
    if args.plagiarism:
        checkPlagiarism( text )


    # report
    if args.style or args.grammar or args.spell:
        writeHTMLreport( outputLines, crit_linenums, warn_linenums )



# Main Program
#############################################



argparser = ArgumentParser(description='Checks papers and other technical texts for grammar, plagiarism and style.')
argparser.add_argument("-g", "--grammar", action='store_true', help="check grammar")
argparser.add_argument("-p", "--plagiarism", action='store_true', help="check plagiarism")
argparser.add_argument("-s", "--spell", action='store_true', help="check spelling")
argparser.add_argument("-y", "--style", action='store_true', help="check language style")
argparser.add_argument("-o", "--output", dest="filename",
                    help="write report to FILE", metavar="FILE")
argparser.add_argument("-q", "--quiet",
                    action="store_false", dest="verbose", default=True,
                    help="don't print messages to stdout")
argparser.add_argument("files", nargs='+')


args = argparser.parse_args()

for file in args.files:
    parseFile(file, args)




