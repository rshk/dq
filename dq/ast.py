from __future__ import absolute_import

import ast
import collections


class WrappedList(collections.MutableSequence):
    def __init__(self, iterable=None):
        self.__wrapped = list()
        if iterable is not None:
            self.__wrapped.extend(iterable)

    def __getitem__(self, pos):
        return self.__wrapped[pos]

    def __setitem__(self, pos, item):
        self.__wrapped[pos] = item

    def __delitem__(self, pos):
        del self.__wrapped[pos]

    def __len__(self):
        return len(self.__wrapped)

    def insert(self, pos, item):
        self.__wrapped.insert(pos, item)


class Pipeline(WrappedList):
    def __repr__(self):
        contents = ' | '.join(repr(x) for x in self)
        return '{{ {0} }}'.format(contents)


class PipelineBlock(WrappedList):
    def __repr__(self):
        contents = ', '.join(repr(x) for x in self)
        return '{{ {0} }}'.format(contents)


class Device(object):
    """
    Parsed object for containers.

    Contains:

    - the device name
    - a list of expressions to be passed as constructor arguments
    """

    def __init__(self, name, args, keywords):
        """
        :param name: function name
        :param args: list of Expression instances
        :param keywords: dict of {string: Expression}
        """

        self.name = name
        self.args = tuple(args)
        self.keywords = keywords

    @classmethod
    def from_star(cls, name, *a, **kw):
        return cls(name, args=a, keywords=kw)

    def __repr__(self):
        arguments = [repr(self.name)]
        for a in self.args:
            arguments.append(repr(a))
        for k, v in self.keywords.iteritems():
            arguments.append('{0}={1!r}'.format(k, v))
        return "{fn}({args})".format(
            fn=self.__class__.__name__,
            args=', '.join(arguments))


class Expression(object):
    """
    Wrapper around Python expressions, parsed from device
    constructor arguments.
    """

    def __init__(self, node, name=None):
        self.node = node
        self.name = name or '<none>'

    @classmethod
    def from_string(cls, s, name=None):
        node = ast.parse(s).body[0].value
        return cls(node, name=name)

    def __repr__(self):
        return "{0}({1!r}, name={2!r})".format(
            self.__class__.__name__, self.node, self.name)

    def compile(self):
        """Compile the node using compile() builtin"""

        return compile(ast.Expression(self.node), self.name, 'eval')

    @property
    def compiled(self):
        comp = getattr(self, '_compiled', None)
        if comp is None:
            comp = self._compiled = self.compile()
        return comp

    def evaluate(self, glob=None, loc=None):
        """Evaluate this expression in a given scope"""

        if glob is None:
            glob = {}
        if loc is None:
            loc = {}
        return eval(self.compiled, glob, loc)
