# strip TeX, Markdown, PDF output


import re


def readTextFromFile(fileName):
    import os

    ext = fileName.lower().split(".")[-1]
    fileName = os.path.expanduser(fileName)
    inFileHandler = open(fileName, "rb")

    if ext == "pdf":
        import subprocess

        SCRIPT_DIR = os.getcwd()

        if Path(fileName).is_absolute():
            fileName = Path(os.path.relpath(Path(fileName), SCRIPT_DIR))

        args = [
            "pdftotext",
            "-enc",
            "UTF-8",
            "{}/{}".format(SCRIPT_DIR, fileName),
            "-",
        ]
        res = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        text = res.stdout.decode("utf-8")
        text = re.sub(r"(?<=\n)\w\w?(?=\n)", "", text)  # remove lines with single word
        text = re.sub(r"\f", "", text)  # remove page breaks
        text = re.sub(r"ﬁ", "fi", text)  # fi Ligature ﬁ
        text = re.sub(r"ﬀ", "ff", text)  # ff Ligature ﬀ

    elif ext in ["txt", "tex", "md"]:
        text = inFileHandler.read().decode("utf-8")
        inFileHandler.close()

    else:
        raise ValueError("unknown extension: " + ext)

    text = re.sub(r"\s(\w{2:7})-\n(\w{2:7})\s", r" \1\2\n", text)  # resolve hyphen

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
