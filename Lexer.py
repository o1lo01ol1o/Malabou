from parsec import *

whitespace = regex(r'\s*', re.MULTILINE)

lexeme = lambda p: p << whitespace

lbrace = lexeme(string('{'))
rbrace = lexeme(string('}'))
lbrack = lexeme(string('['))
rbrack = lexeme(string(']'))
lparen = lexeme(string('('))
rparen = lexeme(string(')'))
lguillemet = lexeme(string(r"«"))
rguillemet = lexeme(string(r"»"))
colon = lexeme(string(':'))
comma = lexeme(string(','))

true = lexeme(string('true')).result(True)
false = lexeme(string('false')).result(False)
null = lexeme(string('null')).result(None)



def number():
    '''Parse number.'''
    return lexeme(
        regex(r'-?(0|[1-9][0-9]*)([.][0-9]+)?([eE][+-]?[0-9]+)?')
    )#.parsecmap(float)



def charseq():
    '''Parse string. (normal string and escaped string)'''
    def string_part():
        '''Parse normal string.'''
        return regex(r'[^"\\]+')

    def string_esc():
        '''Parse escaped string.'''
        return string('\\') >> (
            string('\\')
            | string('/')
            | string('"')
            | string('b').result('\b')
            | string('f').result('\f')
            | string('n').result('\n')
            | string('r').result('\r')
            | string('t').result('\t')
            | regex(r'u[0-9a-fA-F]{4}')#.parsecmap(lambda s: chr(int(s[1:], 16)))
        )
    return string_part() | string_esc()



@lexeme
@generate
def quotedDouble():
    '''Parse quoted string.'''
    yield string('"')
    body = yield many(regex(r'[^"]'))
    yield string('"')
    return ''.join(body)




@lexeme
@generate
def quotedWithStyle():
    yield string('“')
    body = yield many(regex(r'[^”]'))
    yield string('”')
    return ''.join(body)

@lexeme
@generate
def quoted():
    body = quotedDouble | quotedSingle | quotedWithStyle
    return '"' + body + '"'

@lexeme
@generate
def quotedSingle():
    '''Parse quoted string.'''
    yield string("'")
    body = yield many(regex(r'[^\']'))
    yield string("'")
    return ''.join(body)

@lexeme
@generate
def bracketed():
    '''Parse bracked string.'''
    yield lbrack
    body = yield many(regex(r'[^\[\]]'))
    yield rbrack
    return ''.join(body) + " "

def nonBracked():
    return regex(r'[^<>\[\]{}()]')

@lexeme
@generate
def parenthetical():
    '''Parse bracked string.'''
    yield lparen
    body = yield many(regex(r'[^()]'))
    yield rparen
    return ''.join(body) + " "

def anyWord():
    return lexeme(regex(r"[^\s]+"))

def anyNumber():
    return lexeme(regex(r"[0-9]+"))

@lexeme
@generate
def citationTitleAndPage():
    yield many(anyWord())
    yield lexeme(string(","))
    yield anyNumber()
    return ""

@lexeme
@generate
def citationIbidAndPage():
    yield lexeme(string("Ibid."))
    yield anyNumber()
    return ""

@lexeme
@generate
def maybeCitation():
    yield lparen
    yield citationTitleAndPage ^ citationIbidAndPage
    yield rparen
    return ""


def ellipsis():
    return lexeme(string("(…)"))

@lexeme
@generate
def ellipses():
    yield ellipsis() ^ lexeme(string("(. . .)")) ^ lexeme(string("(...)"))
    return""


