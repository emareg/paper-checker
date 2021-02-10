# imports
import re
from papercheck.lib.nlp import *
from papercheck.checker.rules import ReRule, findRegEx
from papercheck.lib.cli import *  # command line interface


# global state variables
# ==========================================================
outputLines = []


# suggest better packages
tabPackages = [("unitsdef", "siunitx")]


def checkTeX(text):
    corrections = []
    warnings = ""

    # warnings += "----------------------------------------------------\n"
    print("\n\nTeX Analysis:")
    print("----------------------------------------------------")
    text = re.sub(r"(?<!\\)\%.*?\n", r"\n", text)  # remove comments
    # checkTeXheadings( text )
    for rule in G_TeXRules:
        corrections += rule.check(text)

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

R_ItemPeriod = ReRule(
    "STYLE: Itemize/Enumerate items should be ended by punctuation (,.) if they are part of a sentence.",
    "\\1,",
    r"\\item\s([^\n]+?\s(?!(?:and|or|[,.!;:]))(?:\w*))(?=\n\s*\\item|\n\s*\\end)",
    # r"\\item\s[^\n]+?\s(?!(?:and|or|[,.!;:]))(\w*)\n\s*(?:\\item|\\end)",
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
    r"\s\$[^$]+?[^\\](sin|cos|tan|log|min|max|exp)[^$]*?[^\$]\$\W",
)

R_MultiCite = ReRule(
    "STYLE: Put consecutive citations in one together: \\cite{label1, label2}.",
    "\\cite{label1, label2}",
    r"((?:\\cite\{[\w :]+?\}[ ,]*){2,})",
)

R_CiteAfterPeriod = ReRule(
    "STYLE: Citations after the period to cite the entire paragraph is uncommon and non standard.",
    "\\cite{\\2}.",
    r"(\.\s*\\cite\{([\w :]+?)\})",
)

R_RefTarget = ReRule(
    "STYLE: Any refernece should state its type (Section|Table|Figure|Eq.|Listing).",
    " Figure \\ref{",
    r"\s(?:in|the|at|on|to|for)(\s*\\ref\{)",
    # r"\s(?!(?:Table|Figure|Section|Listing|Equation|Algorithm|Appendix))(\w*)\s*\\ref\{",
)


# sort by severety as lower rules cannot overwrite higher rules
G_TeXRules = [
    R_MultiCite,
    R_RefTarget,
    R_Caption_Period,
    R_ItemPeriod,
    R_Table_Hline,
    R_MathFun,
    R_SIUnits,
    R_CiteAfterPeriod,
]


## Analyze TeX
# - check itemize starts with capital/lowercase consistent, headings consistent
# - check that itemize item ends with period, comma, or column [.,:?]
# - check that each section has at least 2 subsections etc.
# - check Tables with numbers should be right aligned
# - check caption has period, analyze abstract,
# - check label/ref, centering in figure, tables with @{} consistence, check SI units
# - warn if cite is used after a period DONE
# - check that \ref is not used without a name such as Figure|Table|Section|Equation DONE
# - check number of references and how often cited DONE
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
