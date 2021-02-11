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
from papercheck.ui.report import *


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


# insert the title content for spans
def finalizeCorrections(lines, spans):
    lines = "".join(lines)
    # print(lines)
    for idx, span in enumerate(spans):
        # print("replacing <span{}>".format(str(idx)), "with", span)
        lines = lines.replace("<span{}>".format(str(idx)), span)
    lines = lines.splitlines(True)
    return lines


def markCorrections(lines, corrections, cssclass, spans=[]):
    corrected_linenums = []

    lines = "".join(lines)

    for corr in corrections:
        corrected_linenums += [corr.line]

        # lines[corr.line-1] = lines[corr.line-1].replace(
        #         corr.match, span
        #     )

        # todo: should build a html list an only apply marks to HTML inner
        # todo place whitespace outside
        # todo: replace only specific lines to prevent spelling errors shown many times
        ms = ""
        me = ""
        if corr.match[0] in " (\n":  # FIXME: this might cause line shifts!
            ms = corr.match[0]
            corr.match = corr.match[1:]
        if corr.match[-1] in " ),.\n":
            me = corr.match[-1]
            corr.match = corr.match[:-1]
        spanmark = '<span class="corr {}" title="{} Suggestion: \'{}\'">'.format(
            cssclass, corr.desc, corr.sugg.replace("\n", " ").strip()
        )
        span = "<span" + str(len(spans)) + ">" + corr.match + "</span>"

        lines = lines.replace(ms + corr.match + me, ms + span + me)
        spans.append(spanmark)

    lines = lines.splitlines(True)
    return lines, corrected_linenums, spans


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
    texwarns = ""
    if fileName.endswith(".tex"):
        texcorrections, texwarns = checkTeX(text)
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

    spans = []
    # tex again
    if fileName.endswith(".tex"):
        outputLines, linenums, spans = markCorrections(
            outputLines, texcorrections, "crit", spans
        )
        outputLines = hlTeX(outputLines)
        grammar_linenums += linenums

    # spell check
    if args.spell:
        corrections = checkSpelling(text)
        outputLines, linenums, spans = markCorrections(
            outputLines, corrections, "err", spans
        )
        spell_linenums += linenums

    # grammar check
    if args.grammar:
        corrections = checkGrammar(text)
        outputLines, linenums, spans = markCorrections(
            outputLines, corrections, "crit", spans
        )
        grammar_linenums += linenums

    # style check
    if args.style:
        corrections = checkStyle(text)
        outputLines, linenums, spans = markCorrections(
            outputLines, corrections, "warn", spans
        )
        style_linenums += linenums

    # apply spans
    outputLines = finalizeCorrections(outputLines, spans)

    # plagiarism check
    if args.plagiarism:
        plag = checkPlagiarism(text)

    # report
    if args.style or args.grammar or args.spell or args.plagiarism:
        report = HTMLReport()
        report.setTitle("PaperCheck Report for " + fileBaseName)
        report.addSection("Statistics", stats)
        report.addSection("TeX Warnings", texwarns)
        report.addSection("Plagiarism", plag)
        report.addCorrectedLines(
            outputLines, [grammar_linenums, style_linenums, spell_linenums]
        )
        report.writeToFile(fileBaseName + "_papercheck.html")


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
