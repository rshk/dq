"""
Tests for the new lexer
"""

import pytest

from .utils import lexer  # noqa (fixture)
from .utils import _check_parsed


def test_lex_expression(lexer):
    lexer.input("""
    { F1() | F2() , F3() }
    | F4()
    | {
        { F5() | F6() , F7() } | F8() ,
        F9()
      }
    """)
    _check_parsed(list(lexer), [
        ('LBRACE', '{'),
        ('SYMBOL', 'F1'), ('PYARGS', '()'),
        ('PIPE', '|'),
        ('SYMBOL', 'F2'), ('PYARGS', '()'),
        ('COMMA', ','),
        ('SYMBOL', 'F3'), ('PYARGS', '()'),
        ('RBRACE', '}'),
        ('PIPE', '|'),
        ('SYMBOL', 'F4'), ('PYARGS', '()'),
        ('PIPE', '|'),
        ('LBRACE', '{'),
        ('LBRACE', '{'),
        ('SYMBOL', 'F5'), ('PYARGS', '()'),
        ('PIPE', '|'),
        ('SYMBOL', 'F6'), ('PYARGS', '()'),
        ('COMMA', ','),
        ('SYMBOL', 'F7'), ('PYARGS', '()'),
        ('RBRACE', '}'),
        ('PIPE', '|'),
        ('SYMBOL', 'F8'), ('PYARGS', '()'),
        ('COMMA', ','),
        ('SYMBOL', 'F9'), ('PYARGS', '()'),
        ('RBRACE', '}'),
    ])


_pycode = [
    ('int', '123'),
    ('string', '"this is a string"'),
    ('comparison', 'hello == "world"'),
    ('multi-args', '1, 2, 3, 4'),
    ('expression', '(one == 1) or (two == 2)'),
    ('expression2', '((one == 1) or (two == 2)) and condition + 3'),
    ('args-kwargs',
     '"alpha", "bravo", "charlie"'
     'alpha="a", bravo="b", charlie="c"'),
    ('string-with-parens',
     '"This (is) a ((string)!)"'),
    ('string-with-confusing-parens',
     '"This ((( is (( a string"'),
    ('string-with-confusing-parens2',
     '"This ) is )) a string"'),
    ('string-with-confusing-parens3',
     '"This \\") is )) a string"'),
    ('more-confusing-string', r"""
     'This is \' )', another == string
     """)
]
_pycode_keys = [p[0] for p in _pycode]
_pycode = dict(_pycode)


@pytest.fixture(params=_pycode_keys)
def pycode(request):
    return _pycode[request.param]


def test_lex_pyargs(lexer, pycode):
    lexer.input("Example({0}) | OUT".format(pycode))
    _check_parsed(list(lexer), [
        ('SYMBOL', 'Example'),
        ('PYARGS', "({0})".format(pycode)),
        ('PIPE', '|'),
        ('SYMBOL', 'OUT'),
    ])


def test_lex_pyargs_multi(lexer):
    lexer.input("Example(1, 2)")
    _check_parsed(list(lexer), [
        ('SYMBOL', 'Example'),
        ('PYARGS', "(1, 2)"),
    ])
