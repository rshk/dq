import os
import collections

import ply.yacc as yacc

from dq.lexer import lexer, tokens  # noqa (needed in scope)


class Pipeline(list):
    pass


class PipelineBlock(list):
    pass


class Device(object):
    """
    Parsed object for containers.

    Contains:

    - the device name
    - a list of expressions to be passed as constructor arguments
    """

    def __init__(self, name, args):
        self.name = name
        self.args = args


class Expression(object):
    """
    Wrapper around Python expressions, parsed from device
    constructor arguments.
    """

    pass


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

def p_pipeline_is_component(p):
    """
    pipeline : pipeline_component
    """
    p[0] = Pipeline([p[1]])


def p_pipeline_append(p):
    """
    pipeline : pipeline PIPE pipeline_component
    """
    assert isinstance(p[1], Pipeline)
    p[0] = p[1]
    p[0].append(p[3])


def p_pipeline_component(p):
    """
    pipeline_component : block
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
    block : LBRACE block_contents RBRACE
          | LBRACE block_contents COMMA RBRACE
    """
    p[0] = PipelineBlock(p[2])


def p_block_contents_is_pipe(p):
    """
    block_contents : pipeline
    """
    p[0] = [p[1]]


def p_block_contents_append_pipeline(p):
    """
    block_contents : block_contents COMMA pipeline
    """
    p[0] = p[1]
    p[0].append(p[3])


##----------------------------------------------------------------------------
## Devices
##----------------------------------------------------------------------------


def p_device(p):
    """device : SYMBOL PYARGS"""
    p[0] = Device(p[1], p[2])


##----------------------------------------------------------------------------
## Expressions
##----------------------------------------------------------------------------

# def p_expression(p):
#     """
#     expression : PYEXPR
#     """
#     p[0] = p[1]


debug = True if os.environ.get('DQ_DEBUG') else False
parser = yacc.yacc(debug=debug)
