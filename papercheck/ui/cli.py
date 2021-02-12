import argparse


# CLI Formatting
# =====================================
def bold(string):
    return "\033[1m" + string + "\033[0m"


def red(string):
    return "\033[91m" + string + "\033[0m"


def green(string):
    return "\033[32m" + string + "\033[0m"


def setTitle(title):
    return ""


# ArgParse
# =======================================


def buildArgParser():
    argparser = argparse.ArgumentParser(
        description="Checks papers and other technical texts for grammar, plagiarism and style.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    argparser.add_argument(
        "-g", "--grammar", action="store_true", default=True, help="Check grammar"
    )
    argparser.add_argument(
        "-p", "--plagiarism", action="store_true", help="Check for plagiarism"
    )
    argparser.add_argument(
        "-s", "--spell", action="store_true", default=True, help="check spelling"
    )
    argparser.add_argument(
        "-y", "--style", action="store_true", default=True, help="Check language style"
    )
    # argparser.add_argument(
    #     "-o",
    #     "--output",
    #     dest="filename",
    #     help="write report to FILENAME",
    #     metavar="FILE",
    #     default="./papercheck_report.html",
    # )
    argparser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        dest="quiet",
        default=False,
        help="don't print messages to stdout",
    )
    argparser.add_argument("-x", "--analyze", action="store_true", help="experimental")
    argparser.add_argument("files", nargs="+")

    return argparser


# Deprecated
# =======================================

CFG_INTERACTIVE = False  # ask for action after each error
verbose = True
wasCorrectionMade = False


G_issues = ""


def logIssue(ln, msg, match):
    global G_issues
    G_issues += "Line " + str(ln) + ": " + msg + "(" + match + ")\n"


def askAction(ln, msg, match, replace):
    if not verbose:
        return
    replacestr = green("⇒" + replace) if (replace != "") else ""
    if match[0] != " ":
        match = " " + match

    print(bold("Line " + str(ln)) + ": " + msg + red(match) + replacestr)
    num_n = match.count("\n")
    # outcopy = outputLines[ln-1:ln+num_n]
    # replacestr = green("⇒\""+replace+"\"") if (replace != '') else ''
    # print (''.join(outcopy).replace(match, red('"'+match+'"') + replacestr) )

    ignoreall = False
    if not CFG_INTERACTIVE:
        return False
    global wasCorrectionMade
    reply = input(
        "What should we do? (Enter: nothing, r: repair, i:ignore all, q:quit) : "
    )
    if reply == "r":
        if replace != "":
            outputLines[ln - 1] = outputLines[ln - 1].replace(match, replace, 1)
            wasCorrectionMade = True
    elif reply == "i":
        ignoreall = True
    return ignoreall
