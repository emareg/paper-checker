import re


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

    def __init__(self):
        self.title = "PaperCheck Report"
        self.lns = None
        self.main = ""

    def setTitle(self, title):
        self.title = title

    def addCorrectedLines(self, lines, linenums):

        ROW = '<tr><td><span class="ln {csscls}">{num}</span></td><td><pre>{line}</pre></td>\n'
        rows = ""

        def lineClass(lNum):
            if lNum in linenums[0]:
                return "crit"
            if lNum in linenums[1]:
                return "warn"
            if lNum in linenums[2]:
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
            len(linenums[0]), len(linenums[1]), len(linenums[2]), rows
        )

    def addSection(self, heading, content):
        if content != "":
            self.main += HTMLReport.SEC.format(heading=heading, content=content)

    def writeToFile(self, reportFileName):
        with open(reportFileName, "w+") as f:
            f.write(str(self))

    def __str__(self):
        return HTMLReport.HTML.format(
            title=self.title, css=HTMLReport.CSS, body=self.main
        )
