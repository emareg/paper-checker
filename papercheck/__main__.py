# Quick & dirty python script to check a paper for common English mistakes


# Statistics: http://textalyser.net/index.php?lang=en#analysis


# Settings
# ===========================================
CFG_INTERACTIVE = False  # ask for action after each error
CFG_PRINT_INPUT = False  # print the intput after pre-processing


# import
# ===========================================
from pathlib import Path
import argparse
import os
import sys


# own functions
from papercheck.checker.grammar import checkGrammar, checkStyle
from papercheck.checker.tex import checkTeX
from papercheck.checker.spelling import checkSpelling
from papercheck.checker.plagiarism import checkPlagiarism

from papercheck.lib.stripper import *
from papercheck.pos.tagger import analyzeSentences
from papercheck.textstats import createStats


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
        reply = input("Should the output file " + fileName + " be written? [y/n]")
    if reply == "y":
        with open(fileName, "w+") as f:
            f.write(text)


def markCorrections(lines, corrections, cssclass):
    corrected_linenums = []
    lines = "".join(lines)

    for corr in corrections:
        corrected_linenums += [corr.line]
        # todo place whitespace outside
        ms = ""
        me = ""
        if corr.match[0] in " (\n":
            ms = corr.match[0]
            corr.match = corr.match[1:]
        if corr.match[-1] in " ),.\n":
            me = corr.match[-1]
            corr.match = corr.match[:-1]
        lines = lines.replace(
            ms + corr.match + me,
            ms
            + '<span class="corr '
            + cssclass
            + '" title="{}">{}</span>'.format(
                corr.desc
                + " Suggestion: '"
                + corr.sugg.replace("\n", " ").strip()
                + "'",
                corr.match,
            )
            + me,
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
        html_stats += "<h2>Plagiarism Report</h2><pre>{}</pre><hr>".format(plag)

    out_lines = """
<h2>Text Analysis</h2>
<p>Color Legend:</p>
<ul>
<li><span class="crit">Grammar Problems: {}</span></li>
<li><span class="warn">Style Improvement: {}</span></li>
<li><span class="err">Spelling Errors: {}</span></li>
</ul>
<table><tbody>""".format(
        len(linenums[0]), len(linenums[1]), len(linenums[2])
    )

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
                + "</span></td><td><pre>"
                + line
                + "</pre></td>\n"
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
    out_lines = re.sub(r"(\\\\)", r'<span style="color:blue;">\1</span>', out_lines)
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
    grammar_linenums = []
    style_linenums = []
    spell_linenums = []
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
    if args.analyze:
        analyzeSentences(text)

    # spell check
    if args.spell:
        corrections = checkSpelling(text)
        outputLines, linenums = markCorrections(outputLines, corrections, "err")
        spell_linenums += linenums

    # grammar check
    if args.grammar:
        corrections = checkGrammar(text)
        outputLines, linenums = markCorrections(outputLines, corrections, "crit")
        grammar_linenums += linenums

    # style check
    if args.style:
        corrections = checkStyle(text)
        outputLines, linenums = markCorrections(outputLines, corrections, "warn")
        style_linenums += linenums

    # plagiarism check
    if args.plagiarism:
        plag = checkPlagiarism(text)

    # report
    if args.style or args.grammar or args.spell or args.plagiarism:
        report_out = createHTMLreport(
            outputLines, [grammar_linenums, style_linenums, spell_linenums], stats, plag
        )
        with open(fileBaseName + "_papercheck.html", "w+") as f:
            f.write(report_out)


def parse_arguments():
    argparser = argparse.ArgumentParser(
        description="Checks papers and other technical texts for grammar, plagiarism and style.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    argparser.add_argument("-g", "--grammar", action="store_true", help="check grammar")
    argparser.add_argument(
        "-p", "--plagiarism", action="store_true", help="check plagiarism"
    )
    argparser.add_argument("-s", "--spell", action="store_true", help="check spelling")
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
    argparser.add_argument("-x", "--analyze", action="store_true", help="experimental")
    argparser.add_argument("files", nargs="+")

    return argparser.parse_args()


args = parse_arguments()
for file in args.files:
    parseFile(file, args)
