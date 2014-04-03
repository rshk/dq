"""
Lexer for dq queries.


Queries are built like this:

{ F1(<args>) ; F2(<args>) } | F3(<args>)

Where each ``<args>`` part is to be handled separately,
and is a comma-separated list of Python expressions
and assignments (but we can just split on commas).

"""

from __future__ import absolute_import

import os
import re

import ply.lex as lex


class LexerError(Exception):
    pass


def t_error(t):
    # todo: provide better information about the error..
    raise LexerError("Unknown text {0!r}".format(t.value,))


states = (
    ('pyargs', 'exclusive'),
)


tokens = [
    'COMMENT',
    'SYMBOL',
    'PYARGS',
    'PYEXPR',
]


token_symbols = [
    ('LBRACE', '{'),
    ('RBRACE', '}'),
    # ('LPAREN', '('),
    # ('RPAREN', ')'),
    ('COMMA', ','),
    ('PIPE', '|'),
    # ('EQUAL', '='),
]


globs = globals()
for tk, tkval in token_symbols:
    tokens.append(tk)
    globs['t_' + tk] = re.escape(tkval)


t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    # We don't return a token: newlines will be skipped.


@lex.TOKEN(r'\#.*')
def t_COMMENT(t):
    return None  # Just skip this token


t_SYMBOL = r'[a-zA-Z_][a-zA-Z_0-9]*'


# ---------------------------------------------------------------------
# "Python arguments" state
# ---------------------------------------------------------------------

def t_pyargs(t):
    r'\('
    t.lexer.code_start = t.lexer.lexpos  # starting position
    t.lexer.level = 1  # parentheses level
    t.lexer.begin('pyargs')  # enter state


def t_pyargs_LPAREN(t):
    r'\('
    t.lexer.level += 1


def t_pyargs_RPAREN(t):
    r'\)'
    t.lexer.level -= 1

    # If closing parentheses, return the code fragment
    if t.lexer.level == 0:
        t.value = t.lexer.lexdata[t.lexer.code_start - 1:t.lexer.lexpos]
        t.type = "PYARGS"
        t.lexer.lineno += t.value.count('\n')
        t.lexer.begin('INITIAL')
        return t


def t_pyargs_STRING(t):
    # Single or double-quoted string -> ignore contained parentheses
    r'\"([^\\\n]|(\\.))*?\"|\'([^\\\n]|(\\.))*?\''


def t_pyargs_PYEXPR(t):
    r'[^\(\)\'\"]+'


t_pyargs_ignore = ""


# For bad characters, we just skip over it
# todo: which kind of bad characters?
def t_pyargs_error(t):
    t.lexer.skip(1)


# ----------------------------------------------------------------------
# todo: use some better way to enable partial debug modes
debug = True if os.environ.get('DQ_DEBUG') else False
lexer = lex.lex(debug=debug)
