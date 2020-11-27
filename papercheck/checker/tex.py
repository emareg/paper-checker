# imports
import re
from papercheck.lib.nlp import *


# global state variables
# ==========================================================
outputLines = []


# suggest better packages
tabPackages = [("unitsdef", "siunitx")]


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


class Correction:
    def __init__(self, line, column, match, suggestion, description):
        self.line = line
        self.col = column
        self.match = match
        self.sugg = suggestion
        self.desc = description


class ReRule:
    def __init__(self, description, suggestion="", regex=r""):
        self.desc = description
        self.sugg = suggestion
        self.regex = regex

    def check(self, sentence):
        # print(self.regex)
        corrections = []
        text_out = ""
        matches = findRegEx(self.regex, sentence)
        for idx, match in enumerate(matches):
            matched_words = match[2].group(0)
            sugg = self.sugg(match[2].group(1)) if callable(self.sugg) else self.sugg
            sugg = sugg.replace(r"\1", match[2].group(1))
            desc = self.desc.replace(r"\1", match[2].group(1))
            replace = matched_words.replace(match[2].group(1), sugg, 1)
            replace = replace.replace(r"\n", " ")
            replace = replace.replace("\\", "∖")
            # replace = " "+re.sub(self.regex, self.sugg, match[2].group(0))+" "
            printRule(match[0], desc, matched_words, replace)
            if idx == 0:
                text_out += " * {}\n".format(desc)
            corrections.append(
                Correction(match[0], match[1], matched_words, replace, desc)
            )
        return corrections, text_out


# class ReRule:
#     def __init__(self, description, suggestion="", regex=r""):
#         self.desc = description
#         self.sugg = suggestion
#         self.regex = regex

#     def check(self, sentence):
#         # print(self.regex)
#         matches = findRegEx(self.regex, sentence)
#         for match in matches:
#             sugg = self.sugg.replace(r"\1", match[2].group(1))
#             desc = self.desc.replace(r"\1", match[2].group(1))
#             replace = match[2].group(0).replace(match[2].group(1), sugg, 1)
#             # replace = " "+re.sub(self.regex, self.sugg, match[2].group(0))+" "
#             printRule(match[0], desc, match[2].group(0), replace)


def checkTeX(text):
    global outputLines
    outputLines = text.splitlines(True)
    corrections = []
    warnings = ""

    # warnings += "----------------------------------------------------\n"
    print("\n\nTeX Analysis:")
    print("----------------------------------------------------")
    text = re.sub(r"(?<!\\)\%.*?\n", r"\n", text)  # remove comments
    # checkTeXheadings( text )
    for rule in G_TeXRules:
        c, w = rule.check(text)
        corrections += c
        warnings += w

    warnings += checkTeXreferences(text)
    warnings += checkTeXmath(text)
    return corrections, warnings


# LaTeX Rules
# --------------------------------------------
R_Caption_Period = ReRule(
    "STYLE: Captions should be ended by a period '.'.",
    ".}",
    r"\\caption\{[^}]+?[\w}](\s*\}\s*)(?=\n|%)",
    # r"\\caption\{[^}]+[^. ]\s*(\}\s*)(?=\n)",  # does not match multiline, see #24
)

R_Table_Hline = ReRule(
    "STYLE: In tables use \\toprule or \\midrule from package 'booktabs' instead of \\hline.",
    "\\\\ \\midrule",
    # r"\\begin\{table\}(?:.|\n)*?(\\\\\s*\\hline)(?:.|\n)*?\\end\{table\}",
    # r"\s&\s+.*?(\\\\\s*\\hline)\s*(?=\n)",
    r"(\\\\\s*\\hline)\s*(?=\n)",
)

R_SIUnits = ReRule(
    "STYLE: Use \\SI{ number }{ unit } from package 'siunitx'.",
    "\\SI{ NUM }{ UNIT }",
    r"(?<=\s)(\d+\s?[nmk]?(?:[mgsAKJWCVFTH]|rad|deg|Hz|Pa|Wb))(?=\W)",
)


R_MathFun = ReRule(
    "STYLE: In math mode, use \\\\1 instead of \\1 (upright font).",
    "\\\\1",
    r"\s\$[^$]+?[^\\](sin|cos|tan|log|min|max|exp)[^$]*?[^\$]\$\s",
)

G_TeXRules = [R_Caption_Period, R_Table_Hline, R_SIUnits, R_MathFun]


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
    result = ""
    matches = re.findall(r"\\cite\{([^}]+)\}", text)
    for match in matches:
        refs[match] = refs[match] + 1 if match in refs.keys() else 1
    result += " * INFO: found {} references and {} citations.\n".format(
        len(refs.keys()), len(matches)
    )

    matches = re.findall(r"\\label\{([^}]+)\}", text)
    for match in matches:
        if re.search(r"ref\{\s*" + re.escape(match) + r"\s*\}", text) == None:
            result += " * WARN: unused label: {}\n".format(match)
    return result


def checkTeXmath(text):
    result = ""
    reFunction = r"(sin|cos|tan|log|min|max|exp)"
    matches = findRegEx(
        r"\\begin\{equation\}\s*\n\s*([^$]+?)\s*\n\s*\\end\{equation\}", text
    )
    # matched = findRegEx(r'\s\$(\S[^$]+\S)\$\s', text)
    for match in matches:
        # print(match[2].group(1))
        fun = re.search(r"(?:\s|[\(\)\*])" + reFunction, match[2].group(1))
        if fun != None:
            result += ' * WARN: use "\\{}" instead of "{}". (Equation ln. {})'.format(
                fun.group(1), fun.group(1), match[0]
            )
    return result
