# simple script to remove certain words
# is this a good idea? spell check should check spelling, not style!

uncommon_words = [
    "aardvark",
    "abject",
    "ably",
    "abler",
    "alright",
    "ugh",
    "extant",
    "veal",
    "veer",
    "righteous",
    "LSD",
    "Americanism",
]


fix_affixes = [
    "unlock/DSG",
    "actuate/ADSG",
    "desire/UBDGS",
    "order/UAESDG",
    "assemble/AEDSG",
    "configuration/ASM",
]

import sys, re


def remove_archaic(text):
    pass


def remove_colloquial(text):
    pass


def remove_uncommon(text):
    for word in uncommon_words:
        text = re.sub(r"(?<=\n)" + word + "(?:/[A-Z]+)?\n", "", text)
    return text


def add_affixes(text):
    reftext = read_dictionary("en_US-scowl-70.dic")
    print(len(reftext))
    lines = text.splitlines(True)
    for idx, line in enumerate(lines):
        if line not in reftext:
            word, _, affixes = line.partition("/")
            # print("'{}'".format(word))
            matches = re.search(
                r"(?<=\n)(" + word + "(?:/[A-Z]+)?\n)", reftext, re.MULTILINE
            )
            if matches != None:
                refline = matches[0]
                # TODO: merge affixes!!
                if len(refline) > len(lines[idx]):
                    lines[idx] = refline
                # print(word, refline)

    return "".join(lines)


def read_dictionary(dictfile):
    text = ""
    try:
        fh = open(dictfile, "r")
        text = fh.read()
        fh.close()
    except FileNotFoundError:
        print(
            "ERROR: Dictionary File '{}' not found. Install hunspell.".format(dictfile)
        )
    return text


def write_dict(text):
    fh = open("own_dictionary.dic", "w")
    fh.write(text)
    fh.close()


def main():

    text = read_dictionary(sys.argv[1])
    text = add_affixes(text)
    text = remove_uncommon(text)

    if "extant" in text:
        print("nooo!")

    write_dict(text)


main()
