# Settings
#===========================================

ANALYZE_SENTENCE = False   # analyze sentence structure, experimental

MAX_WORDS_PER_SENT = 50

# consistency settings
OXFORD_COMMA=True                 # is oxford comma used?
CAPITAL_HEADINGS=True             # are headings written in capital?
AMERICAN_ENGLISH=True             # If False: British English




# import
#===========================================


# own functions
from lib.nlp import *         # language functions
from lib.cli import *         # command line interface
from lib.stripper import *
from pos.POS_en import *    # part of speech lists
from lib.word_lists import *    # part of speech lists

from checker import spelling


if ANALYZE_SENTENCE:
    from pos.tagger import *



# global state variables
# ==========================================================
outputLines = []






# checking regex
# ==========================================================


reIntroductoryPhrase = r'\s(?:Actually|As a result|Additionally|Afterwards|Consequently|However|Finally|First|Furthermore|Therefore|Third(?:ly)?|For example|For (?:this|that) reason|Generally|In general|In fact|In (?:18|19|20)\d\d|In the past|Instead(?! of)|On the other hand|Nevertheless|Nowadays|On the contrary|Recently|Second(?:ly)?|What is more)'


# Typography
wrongCharacters = [
    (r'\s(-)\s', '–'),
    (r'\s->\s', '→'),
    (r'(„)', '“'),
    (r'(")\w+', '“'),
    (r'\w+(?:\.|!|?)?(")', '”'),
]





# helper functions
######################################################################################





def findRegEx( regex, text ):
    matches = []
    regex = regex + r'|(\n)'
    line_num = 1
    line_start = 0
    for mo in re.finditer(regex, text):
        try:
            if mo.group(mo.lastindex) == '\n':
                line_start = mo.end()
                line_num += 1
            else:
                column = mo.start() - line_start
                if (mo.group(0)[0] == '\n'): line_num += 1
                matches.append( (line_num, column, mo) )    
                if ('\n' in mo.group(0)[1:]): line_num += mo.group(0).count('\n')
        except Exception as e:
            print(mo)
            print(e) 
    return matches





# features
######################################################################################


class Correction:
     def __init__(self, line, column, match, suggestion, description):
        self.line = line
        self.col = column
        self.match = match
        self.sugg = suggestion
        self.desc = description




class ReRule:
    def __init__(self, description, suggestion="", regex=r""):
        self.desc = description
        self.sugg = suggestion
        self.regex = regex

    def check(self, sentence):
        # print(self.regex)
        corrections = []
        matches = findRegEx(self.regex, sentence)
        for match in matches:
            matched_words = match[2].group(0) if match[2].group(0)[0] != '\n' else match[2].group(0)[1:]
            sugg = self.sugg(match[2].group(1)) if callable(self.sugg) else self.sugg
            sugg = sugg.replace(r'\1', match[2].group(1))
            desc = self.desc.replace(r'\1', match[2].group(1))
            replace = matched_words.replace(match[2].group(1), sugg, 1)
            #replace = " "+re.sub(self.regex, self.sugg, match[2].group(0))+" "
            askAction( match[0], desc, matched_words, replace)   
            corrections.append(Correction(match[0], match[1], matched_words, replace, desc))
        return corrections


class ReSub:
    def __init__(self, description, table, verbs=False):
        self.desc = description
        self.table = table

    def check(self, sentence):
        corrections = []
        for line in self.table:
            # print(line)
            matches = findRegEx(r'\s('+line[0]+r')\W', sentence)
            for match in matches:
                matched_words = match[2].group(0) if match[2].group(0)[0] != '\n' else match[2].group(0)[1:]
                # print(match[2].lastindex)
                # if match[2].lastindex > 1:
                #     replace = match[2].group(0).replace(match[2].group(2), line[1], 1)
                #     print(match[2].group(2))
                # else:
                replace = " "+line[1]+" "
                askAction( match[0], self.desc, match[2].group(0), replace)   
                corrections.append(Correction(match[0], match[1], matched_words, replace, self.desc))
        return corrections




R_AvsAn = ReRule("Use 'an' because the next word starts with a vowel SOUND.", 'an', r'\s(a)\s(?:[AEFHILMNORSX][A-Z\d]{2,3}|(?:[AaOoIi]|[Ee][^u]|[Uu][^sn]|[Uu]n[^i]|[Uu]nin|8[- ]|hour)\w+)\W')
R_AnvsA = ReRule("Use 'a' because the next word does not start with a vowel SOUND.", 'a', r'\s(an)\s[„“”]?(?:[^AaOoEeIiUu\\„“”][a-z]|[^AEFHILMNORSX8„“”][^a-z]|[Uu]s|[Uu]ni)\w*\W')
R_RepeatedWord = ReRule("You repeated a word, which is probably not intended.", r"", r'\s(\w+) +\1\W')
R_RepeatedTwoWords = ReRule("You repeated two words, which is probably not intended.", r"", r'\s(\w+\s\w+) +\1\W')
R_To_vs_Too = ReRule("Possibly 'too' instead of 'to'.", 'too', r'\s(to)\s(:?much|big|cold|early|easy|fast|few|far|low|hard|high|hot|late|large|long|narrow|short|small|soft|soon|strong|weak|wide)\W')
R_Then_vs_Than = ReRule("Use 'than' for comparisons instead of 'then'.", 'than', 
    r'\s+(?:more|less|lower|higher|better|worse|larger|bigger|longer|earlier|shorter|smaller|weaker|stronger)(?: \w{4,15}){0,2}\s(then)\W')  # (:?rather|further)
R_Modal_Base = ReRule("Modal verbs require the base form of the following verb.", 'be', r'\s'+reModal+r'\s(?:not\s)?(?:'+reAdv+r'\s)?(to|are|been|am|is|was|were|has|had|\w{3,9}ed|\w{2,9}[^yus]s)\W') # only base forms
R_Double_Base_Verbs = ReRule("Probably wrong structure of base verbs.", '', r'\s(are|be|been|am|is|was|were|have|has|had)(:?\s\w\w\w+)?\s+(?:be|am|is|was|were|have|has|could|will)\W') # only base forms
R_Did_Base = ReRule("The word 'did' requires the base form of a verb.", 'BASEFORM', r'\sdid\s(?:not\s)?(?:'+reAdv+r'\s)?(\w{3,9}ed|\w{3,9}s)\W') # only base forms
R_Double_Det = ReRule("You have repeated a determiner, which is probably not intended.", '', r'\s'+reTheDet+r'\s+('+reTheDet+r')\W')
R_Double_Adp = ReRule("You have repeated an adposition, which is probably not intended.", '', r'\s'+reAdpos+r'\s+('+reAdpos+r')\W')
R_Double_Modal = ReRule("You have repeated a modal verb, which is probably not intended.", '', r'\s'+reModal+r'\s+('+reModal+r')\W')
R_Wrong3rdPerson = ReRule("Wrong verb form after 3rd person pronoun.", '', r'\s(?:[Hh]e|[Ss]he|[Ii]t|[Oo]ne|[Tt]his)\s(?:'+reAdv+r'\s)?(be|am|have|do|were)\W')
R_Wrong2ndPerson = ReRule("Wrong verb form after 2nd person pronoun.", '', r'\s(?:[Yy]ou|[We]e|[Tt]hey|[Tt]hese|[Tt]hose)\s(?:'+reAdv+r'\s)?(is|has|does|was)\W')


R_Comma_Intro = ReRule("Probably missing comma after introductory phrase.", r',\1', reIntroductoryPhrase + r'(\s\w{1,15})\s')
R_Comma_SubCon = ReRule("Probably no comma before a subordinate conjunction. Only use a comma if it connects two *independent* clauses.", '', r'(?<=\w\s)\w{1,15}\s\w{1,15}(,)\s(as \w\w+ as|after|before|that|whether|since|until|unless|if|even if)\s')
# Quick Trick: if you can replace so,but,and with "therefore" or "such that" it needs a comma (independent clauses)


#R_WrongPlural = ReRule("Possibly wrong plural", '', r"\s+(?:[Aa]n?|[Aa]nother|[Ee]ach)\s+(\w+[^uis'’]s)\W')
R_WrongPlural = ReRule("Possibly wrong plural", singular, r'\s'+reDetSgl+r'\s('+reNounPl+r')\W')
R_WrongSingular = ReRule("Possibly wrong singular", plural, r'\s'+reDetPl+r'\s('+reNounSgl+r')\W')


R_Neither_Or = ReRule("'Neither' needs 'nor' instead of 'or'.", 'nor', r'\s[Nn]either\s[^.]+\s(or)\W')
R_The_Are = ReRule("Probably 'there' or missing Noun?", 'there', r'\s([Tt]he)\s(?:is|are|was|were|have|has)\W')  

R_Quant_of = ReRule("Missing determiner after quantifier + 'of'.", ' of ', r'\s(?:all|any|some|most|none)\sof\s(?!the|these|those|them)\W')
R_Quant_Det = ReRule("Missing 'of' between quantifier and determiner.", ' of ', r'(?<=\s)(?:all|some|most)(\s)(?:the|these|those|them)\W')

R_Be_Do = ReRule("Probably you mean 'done' or 'doing'.", 'done', r'\s(?:be|been|is|are|was|were)\s(?:'+reAdv+r'\s)?(do)\W')



# special rules
R_If_There = ReRule("'if there' must be followed by a base verb.", '', r'\s[Ii]f\sthere\s(?!is|was|are|were|(?:have|has)\sbeen)')
R_Num_suff = ReRule("Wrong suffix of ordinal number", '', r'\s(1[^s][^t]|2[^n][^d]|3[^r][^d])')
R_Is_Cause = ReRule("Missing passive for 'cause'.", 'caused', r'\s(?:is|are|was|were)\s(cause)\W')
R_Kind_of_A = ReRule("'a/an' is not necessary.", '', r'\s(?:kind|sort|type)\sof\s(an?)\W')

R_Too_Either = ReRule("For negated sentences, use either instead of 'too'.", 'either', r'\s(?:not|no)(?:\s\w{1,15}){1,5}\s(too)\.\W')
R_Prefer_To_Gerund = ReRule("Use the base form over gerund after 'prefer to'.", 'BASEFORM', r'\sprefer\sto\s(\w{1,9}ing)\W')  
R_Use_To = ReRule("Probably 'used' instead of 'use'.", 'used', r'\s(?:be|been|is|are|was|were)\s(use)\sto\W')  
R_Especially = ReRule("Consider using 'especially'.", 'especially', r',\s(specially)\W') 
R_The_Question = ReRule("Use 'the question of ...'.", 'of', r'\sthe\squestion(\s)(?:how|why|whether)\W') 


# Wrong word combo?
R_Must_To = ReRule("Do not use 'to' after 'must'.", '', r',\smust\s(to)\W') 
R_Equally_As = ReRule("Do not use 'as' after 'equally'.", '', r',\sequally\s(as)\W') 
R_Width_With = ReRule("Probably 'width' instead of 'with'.", 'width', r',\s(?:a|line|pulse|the) (with)\W') 
R_wait_till = ReRule("Probably 'untill' instead of 'till'.", 'until', r',\s(?:wait|block|stay)(?:s|ed|ing)? (till)\W') 




# todo: check missing 'to' between verbs  (?:use|try|attemp)( )baseverb  => try TO do





# POS Rules
# Adverb repetition:  Adverb, Verb, Adverb
# Adverb before noun:  Adverb, Noun 
# 'The' or 'a' before a punctuation
# 'to' + non-base form verb
# (allow|begin|permit|attempt|admit|appreciate|avoid') + Gerund OR to + infinitive  https://www.ef.com/wwen/english-resources/english-grammar/gerund-equals-infinitive/
# advise|remind and not to


G_Rules = [
    R_RepeatedWord,
    R_RepeatedTwoWords,
    R_Double_Det,
    R_Double_Adp,   # Some false positives
    R_Double_Modal,
    R_Modal_Base,
    R_Double_Base_Verbs,
    R_AvsAn,
    R_AnvsA,
    R_To_vs_Too,
    R_Then_vs_Than,
    R_Did_Base,
    R_Wrong2ndPerson,
    R_Wrong3rdPerson,
    #R_WrongPlural,    # Need POS tags to detect NN
    #R_WrongSingular,  # Need POS tags to detect NN
    R_Neither_Or,
    R_Be_Do,
    R_Comma_Intro,
    R_Comma_SubCon,
]

G_ExtRules = [
    R_If_There,
    R_Quant_of,
    R_Quant_Det,
    R_Is_Cause,
    R_Kind_of_A,
    R_Too_Either,
    R_Prefer_To_Gerund,
    R_Especially,
    R_The_Question,
    R_Must_To,
    R_Equally_As,
    R_Width_With,
    R_wait_till,
]






S_NonScientific = ReSub("Probably wrong word in scientific context.", tabNonScientificWords)
S_Informal = ReSub("Informal word, could be substituted.", tabInformalWords)
S_Redundant = ReSub("Redundant or wordy phrase. Be short.", tabRedundantPhrases)
S_ShortForms = ReSub("Short forms are informal.", tabShortForms)
S_Vague = ReRule("Found vague quantifier. Can you be more specific?", '?', r'\s('+'|'.join(lstVague)+r')\W')

S_Small_Number = ReRule("Cardinal numbers up to twelfe should be written in words within text paragraphs.", num2word, r'\w+\s(10|11|12|\d)\s\w+')
S_Large_Number = ReRule("Large number, you should use a thousand separator.", '', r'[ (](\d{5,})[ ),.]')
S_Preposition_End = ReRule("Do not use prepositions to end your sentences with.", '', r'\s('+rePrep+r')[.!?]')
S_Oxford_Comma = ReRule("Use Oxford comma to make lists less ambigous.", r'\1,', r'\w+,\s+(\w{4,})\s(?:and|or)\s')


# ToDo
# * check for  "foo bar, too"  => use also or additinally



G_StyleRules = [
    S_ShortForms,
    S_NonScientific,
    S_Informal,
    S_Redundant,
    S_Vague,
    # S_Small_Number,  # does not apply in science
    S_Large_Number,
    S_Preposition_End,
    S_Oxford_Comma,
]


G_StyleRulesExtra = [

]



# this needs tags!
def checkPlural( text ):
    matches = findRegEx(r"\s+(?:[Aa]n?|[Aa]nother|[Ee]ach|[Ee]very)\s+(\w+[^uis'’]s)\s+" , text )
    for match in matches:
        replace = match[2].group(0).replace(match[2].group(1), match[2].group(1)[:-1], 1)
        askAction( match[0], "Possibly wrong plural: ", match[2].group(0), replace)




def checkWrongPerson( text ):
    matches = findRegEx( r'\s(?:[Hh]e|[Ss]he|[Ii]t|[Oo]ne|[Tt]his)(:?\salso|\sonly|\s\w\w\w+ly)?\s(have|do|were)\s' , text )
    matches += findRegEx( r'\s(?:[Yy]ou|[We]e|[Tt]hey)(:?\salso|\sonly|\s\w\w\w+ly)?(?:is|has|does|was)\s' , text )
    for match in matches:
        askAction( match[0], "Probably wrong person", match[2].group(0), '')







def checkVerbPrepositions( text ):
    for verbprep in tabVerbPreposition:
        #matches = findRegEx( r'\W+('+verbprep[0]+')\s+((?!'+verbprep[1]+')\w{2,3})\W+' , text )    # invinitive is most likely a noun!
        verbpl = plural(verbprep[0])
        matches = findRegEx( r'\W+(\w+)\s+('+verbpl+')\s+((?!'+verbprep[1]+')\w{2,3})\W+' , text )
        verpt = past(verbprep[0])
        matches += findRegEx( r'\W+(\w+)\s+('+verpt+')\s+((?!'+verbprep[1]+')\w{2,3})\W+' , text )
        for match in matches:
            if match[2].group(1) not in lstDeterminer and match[2].group(3) in lstAdpos:
                print 
                replace = match[2].group(0).replace( match[2].group(3), verbprep[1], 1)
                askAction( match[0], "Possibly wrong preposition: ", match[2].group(0), replace)



def checkHyphen( text ):
    matches = findRegEx( "\w+(-)\w\w\w+ing" , text )
    for match in matches:
        replace= str(match[2].group(0)).replace("-", " ")
        askAction( match[0], "Probably no hyphen of gerund combination: ", match[2].group(0), replace)      








def checkPairs( text ):
    matches = findRegEx( r'\w+\s+(\([^)]+(:?\.\s+[A-Z]))' , text ) # non closing
    matches += findRegEx( r'(\w+\s*\([^)]+\(\s*\w+|\w+\s*\)\s*\(\s*\w+)' , text ) # nested or subsequent parentheses
    #matches += findRegEx( r'(\w\w+\(\w)' , text ) # no space before 
    # @todo: check that the line is not code : no +-/= in the same line
    for match in matches:
        askAction( match[0], "Possibly problem with parentheses: ", match[2].group(0), '')

    matches = findRegEx( r'\s+(“[^”]+“|”\s*“)' , text ) # nested or subsequent “”
    matches += findRegEx( r'\s+(‘[^’]+‘|’\s*‘)' , text ) # nested or subsequent “”
    for match in matches:
        askAction( match[0], "Possibly problem with quotes: ", match[2].group(0), '')
    




def checkAbbreviations( text ):
    # todo: check if Acronym was only used once => suspicious!
    dictionary = {}
    spelling.read_acronyms(dictionary, 'src/dictionary/acronyms.md')
    foundAbbreviations=lstAcronyms + list(dictionary.keys())
    matches = findRegEx( r'\s([A-Z][A-Z])\s' , text )
    for match in matches:
        if( match[2].group(1) not in foundAbbreviations ):
            askAction( match[0], "Found two character acronym, could be written in full words.", match[2].group(0), '')
            foundAbbreviations.append(match[2].group(1))

    matches = findRegEx( r'\s([A-Z][A-Z][A-Z][A-Z]?[A-Z]?)\s(?!\(|“)' , text )
    for match in matches:
        if( '('+match[2].group(1)+')' not in text and match[2].group(1) not in foundAbbreviations ):
            askAction( match[0], "Found acronym that was probably never introduced." , match[2].group(0), '')
            foundAbbreviations.append(match[2].group(1))




def checkSplitInfinitve( text ):
    matches = findRegEx( r'\sto ('+reAdv+') (\w{4,})' , text )
    for match in matches:
        if match[2].group(2) not in lstDeterminer+lstAdpos+lstConjunction+lstAdv:
            replace = 'to '+match[2].group(2)+' '+match[2].group(1)
            askAction( match[0], "An adverb probably splits an infinitive expression.", match[2].group(0), replace)









## Analyze Sentences
##########################

# check length: > 50 words is too long


def checkSentences( text ):
    sentences = split2sentences( text )
    for sentence in sentences:  
        words = split2words( sentence )
        # check length
        if len(words) > MAX_WORDS_PER_SENT: print(bold('Sentence too long ')+'({} words): '.format(len(words))+sentence[:MAX_WORDS_PER_SENT]+'...')
        # print(sentence)
        analyzeSentence( sentence ) 



def checkGrammar( text ):
    global outputLines
    outputLines = text.splitlines(True)
    corrections = []
    # reliable, critical checks
    print('\n\nChecking Grammar:\n----------------------------------------------------')
    for rule in G_Rules + G_ExtRules:
        corrections += rule.check(text)
    return corrections


def checkStyle( text ):
    global outputLines
    outputLines = text.splitlines(True)
    corrections = []
    print('\n\nChecking Language Style:\n----------------------------------------------------')
    for rule in G_StyleRules:
        corrections += rule.check(text)



    print('\n\nChecking Language Extra:\n----------------------------------------------------')

    #checkHyphen( text )     # few false alarms
    checkSplitInfinitve( text )
    checkAbbreviations( text )
    #checkPairs( text )   # many false alarms
  
    return corrections



