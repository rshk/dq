import os
import collections

import ply.yacc as yacc

from dq.lexer import lexer, tokens  # noqa (needed in scope)


class PipeLine(object):
    """
    Container for pipelines.

    Basically, this is a list of devices or other pipelines,
    along with some functionality for executing / chaining them.
    """
    pass


class Device(object):
    """
    Parsed object for containers.

    Contains:

    - the device name
    - a list of expressions to be passed as constructor arguments
    """
    pass


class Expression(object):
    """
    Wrapper around Python expressions, parsed from device
    constructor arguments.
    """
    pass


def p_error(p):
    raise Exception("Parser error!", p)


precedence = (
    ('left', 'COMMA'),
    ('left', 'PIPE'),
)


def p_program(p):
    """
    program : pipeline
    """
    p[0] = p[1]


def p_pipeline_component(p):
    """
    pipeline_component : pipeline
                       | device
    """
    p[0] = p[1]


def p_device(p):
    """
    device : SYMBOL PYARGS
    """
    pass


def p_device_args_list(p):
    pass


def p_device_kwargs_list_one(p):
    """
    device_kwargs_list : device_kwargs
    """
    p[0] = [p[1]]


def p_device_kwargs_list(p):
    """
    device_kwargs_list : device_kwargs_list COMMA device_kwargs
    """
    p[0] = p[1]
    p[0].append(p[3])


def p_device_kwargs(p):
    """
    device_kwargs : SYMBOL EQUAL expression
    """
    p[0] = (p[1], p[3])


##----------------------------------------------------------------------------
## Expressions
##----------------------------------------------------------------------------

def p_expression(p):
    """
    expression : PYEXPR
    """
    p[0] = p[1]


debug = True if os.environ.get('DQ_DEBUG') else False
parser = yacc.yacc(debug=debug)
