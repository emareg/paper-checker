
CFG_INTERACTIVE = False   # ask for action after each error


verbose = True
wasCorrectionMade = False


def bold( string ):
    return '\033[1m'+string+'\033[0m'

def red( string ):
    return '\033[91m'+string+'\033[0m'

def green( string ):
    return '\033[32m'+string+'\033[0m'

def setTitle( title ):
    return ''


def set_silent():
    global verbose
    verbose = False




G_issues = ''
def logIssue( ln, msg, match ):
    global G_issues
    G_issues += "Line " + str(ln) + ": " + msg + "("+match+")\n"


def askAction( ln, msg, match, replace):
    if not verbose: return
    replacestr = green("⇒"+replace) if (replace != '') else ''
    if match[0] != ' ': match = ' '+match

    print ( bold("Line " + str(ln)) + ": " + msg + red(match) + replacestr )
    num_n = match.count('\n')
    # outcopy = outputLines[ln-1:ln+num_n]
    # replacestr = green("⇒\""+replace+"\"") if (replace != '') else ''
    # print (''.join(outcopy).replace(match, red('"'+match+'"') + replacestr) )


    ignoreall = False
    if not CFG_INTERACTIVE: return False
    global wasCorrectionMade
    reply = input("What should we do? (Enter: nothing, r: repair, i:ignore all, q:quit) : ")
    if(reply == "r"):
        if(replace != ''): 
            outputLines[ln-1] = outputLines[ln-1].replace(match, replace, 1)
            wasCorrectionMade = True
    elif(reply == "i"):
        ignoreall = True
    return ignoreall

