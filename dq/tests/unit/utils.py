import pytest


@pytest.fixture
def lexer():
    from dq.lexer import lexer
    return lexer


@pytest.fixture
def parser():
    from dq.parser import parser
    return parser


def _check_parsed(data, expected):
    """Check that parser result matches the expected one"""
    assert len(data) == len(expected)
    for i, (typ, val) in enumerate(expected):
        assert data[i].type == typ
        assert data[i].value == val
