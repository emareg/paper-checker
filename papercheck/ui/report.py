import re


class LineMarks:
    crit = []
    err = []
    warn = []


def hlTeX(lines):
    for idx, line in enumerate(lines):
        # store tags
        tags = re.findall(r"(<span[^<]*?</span>)", line)
        for jdx, tag in enumerate(tags):
            line = line.replace(tag, "<span{}>".format(jdx))

        # highlight
        line = re.sub(r"(\\\w+)(?=\W)", r'<span style="color:blue;">\1</span>', line)
        line = re.sub(r"(\\\\)", r'<span style="color:blue;">\1</span>', line)
        line = re.sub(
            r"(?:[^\\]|^)(%.*?)(?=\n)", r'<span style="color:gray;">\1</span>', line
        )

        # restore tags
        for jdx, tag in enumerate(tags):
            line = line.replace("<span{}>".format(jdx), tag)
        lines[idx] = line
    return lines


class HTMLReport:

    CSS = """<style>
    body{ font-family: monospace; }
    td{ vertical-align: top; max-width: 90vw; }
    pre{ white-space: pre-wrap; }
    em{ font-weight: bold; }
    .ln{display: inline-block;width: 50px;user-select: none;}
    .corr{font-weight:bold;cursor:help;}
    .corr .corr{background-color: #eee; outline: 1px solid gray; padding: .2em;}
    .corr:hover {background-color: yellow;}
    .err{color:Magenta;}
    .crit{color:red;}
    .warn{color:orange;}
    .good{color:green;}
    </style>
    """

    HTML = """<html>
 <head>
  <title>{title}</title>
  <meta name="author" content="PaperCheck by E. Regnath">
  <link rel="icon" type="image/png" href="favicon.png" sizes="any">
  {css}
 </head>
 <body>
  <h1>{title}</h1>
  {body}
 </body>
</html>"""

    SEC = """
    <h2>{heading}</h2><pre>{content}</pre><hr>
    """

    def __init__(self, text=""):
        self.title = "PaperCheck Report"
        self.markLines = {"err": [], "warn": [], "crit": []}
        self.text = text
        self.main = ""
        self.spans = []  # resolve marked <span> elements

    def setTitle(self, title):
        self.title = title

    def addCorrections(self, corrections, cssclass):
        for corr in corrections:
            self.markLines[cssclass] += [corr.line]

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
            span = "<span" + str(len(self.spans)) + ">" + corr.match + "</span>"

            self.text = self.text.replace(ms + corr.match + me, ms + span + me)
            self.spans.append(spanmark)

    def hlTeX(self):
        self.text = "".join(hlTeX(self.text.splitlines(True)))

    def _finalizeCorrections(self):
        for idx, span in enumerate(self.spans):
            self.text = self.text.replace("<span{}>".format(str(idx)), span)

    def addCorrectedLines(self, lines, linenums):

        ROW = '<tr><td><span class="ln {csscls}">{num}</span></td><td><pre>{line}</pre></td>\n'
        rows = ""

        def lineClass(lNum):
            if lNum in linenums["crit"]:
                return "crit"
            if lNum in linenums["warn"]:
                return "warn"
            if lNum in linenums["err"]:
                return "err"
            return ""

        open_tag = None
        for idx, line in enumerate(lines):
            lNum = idx + 1

            # resolve open tags
            if open_tag != None:
                line = open_tag + line
            open_tag = re.search(r"(<span[^>]+>)[^<]*$", line)
            if open_tag:
                open_tag = open_tag.group(1)
                line += "</span>"

            rows += ROW.format(csscls=lineClass(lNum), num=lNum, line=line)

        self.main += """
    <h2>Text Analysis</h2>
    <p>Color Legend:</p>
    <ul>
    <li><span class="crit">Grammar Problems: {}</span></li>
    <li><span class="warn">Style Improvement: {}</span></li>
    <li><span class="err">Spelling Errors: {}</span></li>
    </ul>
    <table><tbody>{}</tbody></table>""".format(
            len(linenums["crit"]), len(linenums["warn"]), len(linenums["err"]), rows
        )

    def addSection(self, heading, content):
        if content != "":
            self.main += HTMLReport.SEC.format(heading=heading, content=content)

    def writeToFile(self, reportFileName):
        self._finalizeCorrections()
        self.addCorrectedLines(self.text.splitlines(True), self.markLines)

        with open(reportFileName, "w+") as f:
            f.write(str(self))

    def __str__(self):
        return HTMLReport.HTML.format(
            title=self.title, css=HTMLReport.CSS, body=self.main
        )
