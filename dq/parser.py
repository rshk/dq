from __future__ import absolute_import

import ast
import os

import ply.yacc as yacc

from dq.lexer import lexer, tokens  # noqa (needed in scope)
from dq.ast import Pipeline, PipelineBlock, Device, Expression


##------------------------------------------------------------
## Grammar
##------------------------------------------------------------
## program : pipeline
##
## pipeline : pipeline_item
##          | pipeline PIPE pipeline_item
##
## pipeline_item : device | block
##
## block : LBRACE RBRACE
##       | LBRACE block_content RBRACE
##       | LBRACE block_content COMMA RBRACE
##
## block_content : pipeline
##               | block_content COMMA pipeline
##
## device : symbol pyargs
##------------------------------------------------------------


def p_error(p):
    raise Exception("Parser error!", p)


precedence = (  # low to high
    ('left', 'COMMA'),
    ('left', 'PIPE'),
)


##----------------------------------------------------------------------
## Program
##----------------------------------------------------------------------

def p_program(p):
    """
    program : pipeline
    """

    p[0] = p[1]


##----------------------------------------------------------------------
## Pipeline
##
## pipeline = pipeline_component
## pipeline = pipeline PIPE pipeline_component
## pipeline_component = device | block
##----------------------------------------------------------------------

def p_pipeline_single(p):
    """
    pipeline : pipeline_item
    """

    p[0] = Pipeline([p[1]])


def p_pipeline_append(p):
    """
    pipeline : pipeline PIPE pipeline_item
    """

    assert isinstance(p[1], Pipeline)
    p[0] = p[1]
    p[0].append(p[3])


def p_pipeline_item(p):
    """
    pipeline_item : block
                  | device
    """

    p[0] = p[1]


##----------------------------------------------------------------------------
## Block
##
## block = LBRACE RBRACE
## block = LBRACE block_contents RBRACE
## block_contents = pipeline
## block_contents = block_contents COMMA pipeline
##----------------------------------------------------------------------------

def p_block_empty(p):
    """ block : LBRACE RBRACE """
    p[0] = PipelineBlock()


def p_block(p):
    """
    block : LBRACE block_content RBRACE
          | LBRACE block_content COMMA RBRACE
    """
    p[0] = PipelineBlock(p[2])


def p_block_content_single(p):
    """
    block_content : pipeline
    """
    p[0] = [p[1]]


def p_block_content_append(p):
    """
    block_content : block_content COMMA pipeline
    """
    p[0] = p[1]
    p[0].append(p[3])


##----------------------------------------------------------------------------
## Devices
##----------------------------------------------------------------------------


def p_device(p):
    """device : SYMBOL PYARGS"""

    ## We can parse the two tokens into a Python AST
    ## object, then extracting args, kwargs and expressions.

    text = ''.join((p[1], p[2]))
    parsed = ast.parse(text)

    assert isinstance(parsed, ast.Module)
    assert len(parsed.body) == 1
    assert isinstance(parsed.body[0], ast.Expr)
    assert isinstance(parsed.body[0].value, ast.Call)

    _call = parsed.body[0].value

    func_name = _call.func.id
    args = [Expression(a) for a in _call.args]
    keywords = dict((k.arg, Expression(k.value)) for k in _call.keywords)

    if _call.starargs is not None:
        raise ValueError("*varargs are not supported")
    if _call.kwargs is not None:
        raise ValueError("**kwargs are not supported")

    p[0] = Device(func_name, args, keywords)


##----------------------------------------------------------------------------
## Create the parser
##----------------------------------------------------------------------------

debug = True if os.environ.get('DQ_DEBUG') else False
parser = yacc.yacc(debug=debug)
