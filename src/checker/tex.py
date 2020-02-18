# imports
import re
from lib.nlp import *


# global state variables
# ==========================================================
outputLines = []


def bold(string):
    return "\033[1m" + string + "\033[0m"


def red(string):
    return "\033[91m" + string + "\033[0m"


def green(string):
    return "\033[32m" + string + "\033[0m"


def printRule(ln, msg, match, replace):
    global outputLines
    print(bold("Line " + str(ln)) + ": " + msg)
    num_n = match.count("\n")
    outcopy = outputLines[ln - 1 : ln + num_n]
    replacestr = green('⇒"' + replace + '"') if (replace != "") else ""
    print("".join(outcopy).replace(match, red('"' + match + '"') + replacestr))


def findRegEx(regex, text):
    matches = []
    regex = regex + r"|(\n)"
    line_num = 1
    line_start = 0
    for mo in re.finditer(regex, text):
        if mo.group(mo.lastindex) == "\n":
            line_start = mo.end()
            line_num += 1
        else:
            column = mo.start() - line_start
            matches.append((line_num, column, mo))
            if "\n" in mo.group(0):
                line_num += mo.group(0).count("\n")
    return matches


class ReRule:
    def __init__(self, description, suggestion="", regex=r""):
        self.desc = description
        self.sugg = suggestion
        self.regex = regex

    def check(self, sentence):
        # print(self.regex)
        matches = findRegEx(self.regex, sentence)
        for match in matches:
            replace = match[2].group(0).replace(match[2].group(1), self.sugg, 1)
            # replace = " "+re.sub(self.regex, self.sugg, match[2].group(0))+" "
            printRule(match[0], self.desc, match[2].group(0), replace)


def checkTeX(text):
    global outputLines
    outputLines = text.splitlines(True)
    print("\n\nTeX Analysis:")
    print("----------------------------------------------------")
    text = re.sub(r"(?<!\\)\%.*?\n", r"\n", text)  # remove comments
    # checkTeXheadings( text )
    for rule in G_TeXRules:
        rule.check(text)

    checkTeXreferences(text)
    checkTeXmath(text)
    print("----------------------------------------------------\n\n")


# LaTeX Rules
# --------------------------------------------


# LaTeX Rules
# --------------------------------------------
R_Caption_Period = ReRule(
    " * INFO: Captions should be ended by a period '.'.",
    ".}",
    r"\\caption\{[^}]+[^. ]\s*(\}\s*)(?=\n)",
)


G_TeXRules = [R_Caption_Period]


## Analyze TeX
# - check itemize starts with capital/lowercase consistent, headings consistent
# - check that each section has at least 2 subsections etc.
# - check that itemize has dots, comma
# - check caption has period, analyze abstract,
# - check number of references and how often cited
# - check label/ref, centering in figure, tables with @{} consistence, check SI units
# - check figures referenced in text  DONE
##########################


def checkTeXheadings(text):
    lstTeXHeading = [
        "title",
        "chapter",
        "section",
        "subsection",
        "subsubsection",
        "paragraph",
    ]
    for heading in lstTeXHeading:
        matches = findRegEx(r"\\" + heading + r"\{([^}]*?)\}", text)
        for match in matches:
            words = split2words(match[2].group(1))
            for word in words:
                if (
                    len(word) > 3
                    and word[0].islower()
                    and word not in lstAdpos + lstDet + lstConjunction
                ):
                    # askAction( match[0], "Lowercase letter in heading:" , word, word.capitalize())
                    print("Lowercase letter in heading: ", match[2].group(1))
                    break


def checkTeXreferences(text):
    refs = {}
    matches = re.findall(r"\\cite\{([^}]+)\}", text)
    for match in matches:
        refs[match] = refs[match] + 1 if match in refs.keys() else 1
    print(
        " * INFO: found {} references and {} citations.".format(
            len(refs.keys()), len(matches)
        )
    )

    matches = re.findall(r"\\label\{([^}]+)\}", text)
    for match in matches:
        if re.search(r"ref\{\s*" + re.escape(match) + r"\s*\}", text) == None:
            print(" * WARN: unused label: {}".format(match))

    matches = findRegEx(r"\\caption\{[^}]+[^.](\s*\})\s*\n", text)
    for match in matches:
        print(" * WARN: caption missing period (line {})".format(match[0]))


def checkTeXmath(text):
    reFunction = r"(sin|cos|tan|log|min|max|exp)"
    matches = findRegEx(
        r"\\begin\{equation\}\s*\n\s*([^$]+?)\s*\n\s*\\end\{equation\}", text
    )
    # matched = findRegEx(r'\s\$(\S[^$]+\S)\$\s', text)
    for match in matches:
        # print(match[2].group(1))
        fun = re.search(r"(?:\s|[\(\)\*])" + reFunction, match[2].group(1))
        if fun != None:
            print(
                ' * WARN: use "\\{}" instead of "{}". (Equation ln. {})'.format(
                    fun.group(1), fun.group(1), match[0]
                )
            )
