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
# - resolve input/include/subfile or do not require \begin{document} for tex files

# - check adposition at the end
# - check noun cluster


# command line argument: improvements or only mistakes

# if im präsens → 2. teil in future; if im perfekt → 2. teil in präsens
# If $\Delta t$ is passed as argument, the time dependence is made obvious for the caller.
# If someone looks over the code later, subprograms that depend on time will be easy to spot.


# not found:
# a honor,   a utility
# ... by but ... => comma or mistake
# the all the (the all)?
# "a XX a" / "the XX the" is probably wrong
# is spend => is spent
# paranthesis => parantheses
# ... consensus based ... consensus-based (always -based?)


# Statistics: http://textalyser.net/index.php?lang=en#analysis


# Settings
# ===========================================

from papercheck.textstats import createStats
from papercheck.lib.stripper import *
from papercheck.checker.plagiarism import checkPlagiarism
from papercheck.checker.spelling import checkSpelling
from papercheck.checker.tex import checkTeX
from papercheck.checker.grammar import checkGrammar, checkStyle, checkSentences
from pathlib import Path
import argparse
import os
import sys
ANALYZE_SENTENCE = False  # analyze sentence structure, experimental
CFG_INTERACTIVE = False  # ask for action after each error
CFG_PRINT_INPUT = False  # print the intput after pre-processing


# import
# ===========================================


# own functions


# global state variables
# ==========================================================
outputLines = []
wasCorrectionMade = False
G_filename = ""

# helper functions
######################################################################################


def writeOutputFile(fileName, text):
    reply = ""
    while reply == "":
        reply = input("Should the output file " +
                      fileName + " be written? [y/n]")
    if reply == "y":
        with open(fileName, "w+") as f:
            f.write(text)


def markCorrections(lines, corrections, cssclass):
    corrected_linenums = ()
    lines = "".join(lines)
    # print(lines)

    for corr in corrections:
        corrected_linenums += (corr.line,)
        lines = lines.replace(
            corr.match,
            '<span class="corr '
            + cssclass
            + '" title="{}">{}</span> '.format(
                corr.desc
                + " Suggestion: '"
                + corr.sugg.replace("\n", " ").strip()
                + "'",
                corr.match,
            ),
        )

    lines = lines.splitlines(True)
    return lines, corrected_linenums


def createHTMLreport(lines, linenums=[[], [], []], stats="", plag=""):

    grammar_linenums = linenums[0]
    style_linenums = linenums[1]
    spell_linenums = linenums[2]

    head = """
<html>
  <head>
    <title>Report of papercheck</title>
    <style>body{{font-family: monospace;}}
    body{ font-family: monospace; }
    td{ vertical-align: top; }
    em{ font-weight: bold; }
    .ln{display: inline-block;width: 50px;user-select: none;}
    .corr{font-weight:bold;cursor:pointer;}
    .corr:hover {background-color: yellow;}
    .err{color:Magenta;}
    .crit{color:red;}
    .warn{color:orange;}
    .good{color:green;}
    </style>
  </head>
    """

    top_header = "<h1>PaperCheck Report for {}</h1><hr>".format(G_filename)

    html_stats = "<h2>Text Statistics</h2><pre>{}</pre><hr>".format(stats)

    if plag != "":
        html_stats += "<h2>Plagiarism Report</h2><pre>{}</pre><hr>".format(
            plag)

    out_lines = """
<h2>Text Analysis</h2>
<p>Color Legend:</p>
<ul>
<li><span class="crit">Grammar Mistake</span></li>
<li><span class="warn">Style Improvement</span></li>
<li><span class="err">Spelling</span></li>
</ul>
<table><tbody>"""

    open_tag = None
    for num, line in enumerate(lines):

        # resolve open tags
        if open_tag != None:
            line = open_tag + line
        open_tag = re.search(r"(<span[^>]+>)[^<]*$", line)
        if open_tag:
            open_tag = open_tag.group(1)
            line += "</span>"

        if num + 1 in grammar_linenums:
            out_lines += (
                '<tr><td><span class="ln crit">'
                + str(num + 1)
                + "</span></td><td>"
                + line
                + "</td>\n"
            )
        elif num + 1 in style_linenums:
            out_lines += (
                '<tr><td><span class="ln warn">'
                + str(num + 1)
                + "</span></td><td>"
                + line
                + "</td>\n"
            )
        elif num + 1 in spell_linenums:
            out_lines += (
                '<tr><td><span class="ln err">'
                + str(num + 1)
                + "</span></td><td>"
                + line
                + "</td>\n"
            )
        else:
            out_lines += (
                '<tr><td><span class="ln">'
                + str(num + 1)
                + "</span></td><td>"
                + line
                + "</td>\n"
            )

    out_lines += "</table></tbody>"

    out_lines = re.sub(
        r"(\\\w+)(?=\W)", r'<span style="color:blue;">\1</span>', out_lines
    )
    # out_lines = re.sub(r'(\n[^%]*?)([{}])', r'\1<span style="color:blue;">\2</span>', out_lines)
    out_lines = re.sub(
        r"(\\\\)", r'<span style="color:blue;">\1</span>', out_lines)
    out_lines = re.sub(
        r"(?<=[^\\])(%.*?)(?=\n)", r'<span style="color:gray;">\1</span>', out_lines
    )

    output = head + "<body>\n{}</body>\n</html>".format(
        top_header + html_stats + out_lines
    )
    return output


# main parsing function
######################################################################################


def parseFile(fileName, args):
    fileBaseName, ext = os.path.splitext(fileName)
    fileBaseName = os.path.basename(fileBaseName)

    text = readTextFromFile(fileName)

    global outputLines
    global G_filename

    G_filename = fileBaseName
    outputLines = text.splitlines(True)
    grammar_linenums = ()
    style_linenums = ()
    spell_linenums = ()
    plag = ""

    # check if silent
    if not args.verbose:
        sys.stdout = open(os.devnull, "w")

    # process TeX
    if fileName.endswith(".tex"):
        checkTeX(text)
        text = stripTeX(text, True)

    if CFG_PRINT_INPUT:
        for idx, line in enumerate(outputLines):
            print("#{}: {}".format(idx, line), end="")

    # show stats
    stats = createStats(text)
    print(stats)

    # regex finiter: https://docs.python.org/3/library/re.html#writing-a-tokenizer
    if ANALYZE_SENTENCE:
        checkSentences(text)

    # spell check
    if args.spell:
        corrections = checkSpelling(text)
        outputLines, linenums = markCorrections(
            outputLines, corrections, "err")
        spell_linenums += linenums

    # grammar check
    if args.grammar:
        corrections = checkGrammar(text)
        outputLines, linenums = markCorrections(
            outputLines, corrections, "crit")
        grammar_linenums += linenums

    # style check
    if args.style:
        corrections = checkStyle(text)
        outputLines, linenums = markCorrections(
            outputLines, corrections, "warn")
        style_linenums += linenums

    # plagiarism check
    if args.plagiarism:
        plag = checkPlagiarism(text)

    # report
    if args.style or args.grammar or args.spell or args.plagiarism:
        report_out = createHTMLreport(
            outputLines, [grammar_linenums, style_linenums,
                          spell_linenums], stats, plag
        )
        with open(fileBaseName + "_papercheck.html", "w+") as f:
            f.write(report_out)


def parse_arguments():
    argparser = argparse.ArgumentParser(
        description="Checks papers and other technical texts for grammar, plagiarism and style.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    argparser.add_argument(
        "-g", "--grammar", action="store_true", help="check grammar")
    argparser.add_argument(
        "-p", "--plagiarism", action="store_true", help="check plagiarism"
    )
    argparser.add_argument(
        "-s", "--spell", action="store_true", help="check spelling")
    argparser.add_argument(
        "-y", "--style", action="store_true", help="check language style"
    )
    argparser.add_argument(
        "-o",
        "--output",
        dest="filename",
        help="write report to FILE",
        metavar="FILE",
        default="papercheck_report.html",
    )
    argparser.add_argument(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        default=True,
        help="don't print messages to stdout",
    )
    argparser.add_argument("files", nargs="+")

    return argparser.parse_args()


args = parse_arguments()
for file in args.files:
    parseFile(file, args)
