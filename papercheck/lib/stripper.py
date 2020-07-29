# strip TeX, Markdown, PDF output


import re
import os
from pathlib import Path


def readTextFromFile(fileName):

    ext = fileName.lower().split(".")[-1]
    fileName = os.path.expanduser(fileName)
    inFileHandler = open(fileName, "rb")

    if ext == "pdf":
        import subprocess

        SCRIPT_DIR = os.getcwd()

        if Path(fileName).is_absolute():
            fileName = Path(os.path.relpath(Path(fileName), SCRIPT_DIR))

        args = ["pdftotext", "-enc", "UTF-8", "{}/{}".format(SCRIPT_DIR, fileName), "-"]
        res = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        text = res.stdout.decode("utf-8")
        text = stripPDFtoText(text)

    elif ext in ["txt", "tex", "md"]:
        text = inFileHandler.read().decode("utf-8")
        inFileHandler.close()

    elif ext == "html":
        text = inFileHandler.read().decode("utf-8")
        text = stripHTML(text)

    else:
        raise ValueError("unknown extension: " + ext)

    text = resolveHyphen(text)

    return text


def resolveHyphen(text):
    # note: pdftotext already removes hyphens
    #       undo this: 1. figure out average line length, check if a line almost double the length, check if word is misspelled.
    matches = re.findall(r"(\s(\w{2,7})-\n(\w{2,7})\s)", text)
    for match in matches:
        if match[1] != "self" and match[2] not in [
            "based",
            "constrained",
            "defined",
            "case",
            "related",
            "critical",
            "level",
        ]:
            text = text.replace(match[0], match[1] + match[2] + "\n")
    return text


def stripPDFtoText(text):
    # text = re.sub(r"(?<=\n)\s?\w\w*?\s?(?=\n)", "", text)  # remove lines with single word
    # text = re.sub(r"(?<=\n)((?!hede).)*(?=\n)", "", text)  # remove lines without words
    # text = re.sub(r"(?<=\n)(?!\d\.\s|\d.\d\d?\.|[A-Z]).{,12}(?=[^.:,]\n)", "", text)  # remove short lines that are not headings
    text = re.sub(
        r"(?<=\n)(?:(?:(?!\s\w{4}|\d.\d\d?\.|[A-Z]).){1,14}[^.:,]|[.:,])(?=\n)",
        "",
        text,
    )  # remove short lines without words
    text = re.sub(r"\n{4,}", "\n\n\n", text)  # remove empty parts
    text = re.sub(r"\f", "", text)  # remove page breaks
    text = re.sub(r"ﬁ", "fi", text)  # fi Ligature ﬁ
    text = re.sub(r"ﬀ", "ff", text)  # ff Ligature ﬀ
    text = text.replace("\f", "")  # pagebreaks

    lines = text.splitlines(True)
    n = len(lines)
    s = sorted([len(x) for x in lines])
    medlen = (
        int((sum(s[n // 2 - 1 : n // 2 + 1]) / 2.0, s[n // 2])[n % 2]) if n else None
    )
    minl = int(medlen * 0.78)

    ## find lines longer
    for idx, line in enumerate(lines):
        if len(line) > 1.6 * medlen:
            line = re.sub(
                rf"(.{{{minl},{medlen}}}\s\w{{4,10}})(based|constrained|defined|case|related|critical|level)",
                r"\1-\n\2",
                line,
            )
            line = re.sub(
                rf"([^\n]{{{minl},{medlen}}}\s(?:self))(\w{{3,10}})", r"\1-\n\2", line
            )
            line = re.sub(
                rf"([^\n]{{{minl+5},{medlen+5}}})\s([^\n]{{{minl-10},}})",
                r"\1\n\2",
                line,
            )
            # print(line)
            lines[idx] = line
    text = "".join(lines)
    return text


# is this necessary? Will produce nice output. Maybe only insert spaces before hX and <p>HERE Start of a Sentence</p>
# provide line-offset?


def stripHTML(text):
    text = re.sub(r"^(?:.|\n)*?<body.*?>", "", text)
    text = re.sub(r"</body>(?:.|\n)*", "", text)

    # headings, paragraphs, strong, em
    text = re.sub(
        r"<h\d[^>]*>((?:(?!</h\d>).)*?)</h\d>", r"\1", text
    )  # keep headings and lists?
    text = re.sub(r"<p[^>]*>((?:(?!</p>).)*?)</p>", r"\1", text)
    text = re.sub(r"<strong[^>]*>((?:(?!</strong>).)*?)</strong>", r"\1", text)
    text = re.sub(r"<code[^>]*>((?:(?!</code>).)*?)</code>", r"\1", text)
    text = re.sub(r"<em[^>]*>((?:(?!</em>).)*?)</em>", r"\1", text)

    text = text.replace("&nbsp;", "")

    return text


def stripTeX(text, preserveLines=False):
    linenum = 1
    if preserveLines and "\\begin{" + "document}" in text:
        preamble = re.search(r"^(?:.|\n)*?\\begin\{document\}", text).group(0)
        linenum = len(preamble.splitlines()) - 1

    text = re.sub(r"^(?:.|\n)*?\\begin\{document\}", "\n" * linenum, text)
    text = re.sub(r"\\end\{document\}(?:.|\n)*?", "", text)

    lstTexCmdOne = ["emph", "text\w\w", "math\w\w", "gls\w?", "num"]
    for cmd in lstTexCmdOne:
        text = re.sub(r"\\" + cmd + "\{([^}]*)\}", r"\1", text)

    lstTexCmdTwo = ["SI", "lettrine"]
    for cmd in lstTexCmdTwo:
        text = re.sub(r"\\" + cmd + "\{([^}]*)\}\{([^}]*)\}", r"\1\2", text)

    lstTexCmdRemove = ["cite", "label", "ref"]
    for cmd in lstTexCmdRemove:
        text = re.sub(r"\s?\\" + cmd + r"\{([^\}]*)\}", r"", text)

    text = re.sub(r"(?<!\\)\%.*?\n", r"\n", text)  # remove comments
    text = re.sub(r"(\$[^$]+\$)", "$x$", text)  # remove inline math
    text = re.sub(r"\\([%#$&])(?=[ \}])", r"\1", text)  # replace special chars

    # remove environments completely
    # todo: extract caption!
    lstTeXEnv = ["figure", "lstlisting", "table", "equation"]
    for env in lstTeXEnv:
        matches = re.findall(
            r"(\\begin\{" + env + r"\*?\}(?:.|(\n))*?\\end\{" + env + r"\*?\})", text
        )
        for match in matches:
            text = text.replace(match[0], "\n" * (len(str.splitlines(match[0])) - 1))

    # strip environments
    lstTeXEnv = [
        "abstract",
        "itemize",
        "enumerate",
        "description",
        "quotation",
        "verbatim",
    ]
    for env in lstTeXEnv:
        text = re.sub(r"\\begin\{" + env + r"\}", "", text)
        text = re.sub(r"\\end\{" + env + r"\}", "", text)
        text = re.sub(r"\\item(?:\[[^\]]*\])?", "", text)

    # headings
    lstTeXHeading = [
        "title",
        "chapter",
        "section",
        "subsection",
        "subsubsection",
        "paragraph",
    ]
    for heading in lstTeXHeading:
        text = re.sub(r"\\" + heading + r"\{([^}]*?)\}", r"\1", text)

    # remove remaining
    text = re.sub(
        r"\\\w+(?:\*|\[[^\]]*\])?(?:\{([^}\n]*)\})*", r"", text
    )  # replace special chars

    return text


def stripMarkdown(text):
    text = re.sub(r"\W\*\*?\S([^*]*)\*\*?\W", r"\1", text)  # bold/italic
    text = re.sub(r"`([^`]+)`", r"\1", text)  # inline code
    text = re.sub(r"```([^`]+)```", r"", text)  # remove code blocks
    return text
