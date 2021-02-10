import re
from papercheck.lib.cli import *  # command line interface


class Correction:
    def __init__(self, line, column, match, suggestion, description):
        self.line = line
        self.col = column
        self.match = match
        self.sugg = suggestion
        self.desc = description

    def __str__(self):
        return bold("Line {}:".format(self.line)) + " {}: {} → {}".format(
            self.desc, red(self.match), green(self.sugg)
        )


def findRegEx(regex, text):
    matches = []
    regex = regex + r"|(\n)"
    line_num = 1
    line_start = 0
    for mo in re.finditer(regex, text):
        try:
            if mo.group(mo.lastindex) == "\n":
                line_start = mo.end()
                line_num += 1
            else:
                column = mo.start() - line_start
                if mo.group(0)[0] == "\n":
                    line_num += 1
                matches.append((line_num, column, mo))
                if "\n" in mo.group(0)[1:]:
                    line_num += mo.group(0).count("\n")
        except Exception as e:
            print("MatchObject:", mo)
            print(e)
    return matches


class ReRule:
    def __init__(self, description, suggestion="", regex=r""):
        self.desc = description
        self.sugg = suggestion
        self.regex = regex

    def _check_single(self, text, regex, sugg):
        pass

    def check(self, sentence):
        # print(self.regex)
        corrections = []
        matches = findRegEx(self.regex, sentence)
        for match in matches:
            matched_words = match[2].group(0)
            sugg = self.sugg(match[2].group(1)) if callable(self.sugg) else self.sugg
            sugg = sugg.replace(r"\1", match[2].group(1))
            if match[2].group(2):
                sugg = sugg.replace(r"\2", match[2].group(2))
            desc = self.desc.replace(r"\1", match[2].group(1))
            replace = matched_words.replace(match[2].group(1), sugg, 1)
            replace = replace.replace("\n", " ")
            replace = replace.replace("\\", "∖")
            # replace = " "+re.sub(self.regex, self.sugg, match[2].group(0))+" "
            # askAction(match[0], desc, matched_words, replace)
            newcorr = Correction(match[0], match[1], matched_words, replace, desc)
            corrections.append(newcorr)
            print(newcorr)
        return corrections


class ReSub(ReRule):
    def __init__(self, description, table):
        self.desc = description
        self.table = table

    def check(self, sentence):
        corrections = []
        for line in self.table:
            # print(line)
            matches = findRegEx(r"(\s" + line[0] + r"\W)", sentence)
            for match in matches:
                matched_words = match[2].group(0)
                replace = match[2].group(0)[0] + line[1] + match[2].group(0)[-1]
                askAction(match[0], self.desc, match[2].group(0), replace)
                corrections.append(
                    Correction(match[0], match[1], matched_words, replace, self.desc)
                )
        return corrections


class ComplexRule:
    def checkText(self, text: str) -> list:
        raise NotImplementedError


class Checker:
    def __init__(self, name):
        self.name = name
        self.reRules = []

    def addRules(self, rules: list):
        if not rules or len(rules) == 0:
            return
        self.reRules += rules

    def checkText(self, text: str):
        corrections = []
        for rule in self.reRules:
            corrections += rule.check(text)
        return corrections

    def checkSentences(self, sents: list):
        corrections = []
        for sent in sents:
            corrections += self.checkText(sent)
        return corrections
