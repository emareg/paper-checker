import re


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


class ReSub:
    def __init__(self, description, table, verbs=False):
        self.desc = description
        self.table = table

    def check(self, sentence):
        for line in self.table:
            # print(line)
            matches = findRegEx(r"\s(" + line[0] + r")\s", sentence)
            for match in matches:
                # print(match[2].lastindex)
                # if match[2].lastindex > 1:
                #     replace = match[2].group(0).replace(match[2].group(2), line[1], 1)
                #     print(match[2].group(2))
                # else:
                replace = " " + line[1] + " "
                printRule(match[0], self.desc, match[2].group(0), replace)
