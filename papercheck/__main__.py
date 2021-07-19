# Quick & dirty python script to check a paper for common English mistakes


# Statistics: http://textalyser.net/index.php?lang=en#analysis


# Settings
# ===========================================
CFG_INTERACTIVE = False  # ask for action after each error
CFG_PRINT_INPUT = False  # print the intput after pre-processing


# import
# ===========================================
from pathlib import Path
import os
import sys


# own functions
from papercheck.checker.grammar import checkGrammar, checkStyle
from papercheck.checker.tex import checkTeX
from papercheck.checker.spelling import checkSpelling
from papercheck.checker.plagiarism import checkPlagiarism

from papercheck.lib.stripper import *
from papercheck.pos.tagger import analyzeSentences
from papercheck.textstats import TextStats

from papercheck.ui.cli import buildArgParser
from papercheck.ui.report import HTMLReport, LineMarks, hlTeX
from papercheck.ui.cligui import CliGui


# main parsing function
######################################################################################


def parseFile(args):

    for fileName in args.files:
        fileBaseName, ext = os.path.splitext(fileName)
        fileBaseName = os.path.basename(fileBaseName)

        text = readTextFromFile(fileName)

        plag = ""
        report = HTMLReport(text)

        # check if silent
        if args.quiet:
            sys.stdout = open(os.devnull, "w")

        # process TeX
        texwarns = ""
        if fileName.endswith(".tex"):
            texcorrections, texwarns = checkTeX(text)
            text = stripTeX(text, True)

        if CFG_PRINT_INPUT:
            for idx, line in enumerate(text.splitlines(True)):
                print("#{}: {}".format(idx, line), end="")

        # show stats
        stats = TextStats(text)
        print(stats)

        # regex finiter: https://docs.python.org/3/library/re.html#writing-a-tokenizer
        if args.analyze:
            analyzeSentences(text)

        spans = []
        # tex again
        if fileName.endswith(".tex"):
            report.addCorrections(texcorrections, "crit")
            report.hlTeX()

        # run checkers
        # =======================================
        checkers = [
            # (enabled: Bool, cmd: Callable, cssclass: str)
            (args.grammar, checkGrammar, "crit"),
            (args.spell, checkSpelling, "err"),
            (args.style, checkStyle, "warn"),
            # (args.plag,    checkPlagiarism,    'warn'),
        ]

        for idx, checker in enumerate(checkers):
            if checker[0]:
                corrections = checker[1](text)
                report.addCorrections(corrections, checker[2])

        # plagiarism check
        if args.plagiarism:
            plag = checkPlagiarism(text)

        # build report
        if args.style or args.grammar or args.spell or args.plagiarism:
            report.setTitle("PaperCheck Report for " + fileBaseName)
            report.addSection("Statistics", str(stats))
            report.addSection("TeX Warnings", texwarns)
            report.addSection("Plagiarism", plag)
            report.writeToFile(fileBaseName + "_papercheck.html")


# Ladies and Gentlemen, the entry point:

argParser = buildArgParser()

if len(sys.argv) == 1:
    print("No arguments, starting GUI.")
    CliGui(argParser, parseFile)
else:
    args = argParser.parse_args()
    parseFile(args)
