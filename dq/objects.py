import ast
import collections
import inspect
import itertools


class MultipleOutput(tuple):
    """
    Used to indicate this tuple contains multiple
    outputs, from a block, in order to distinguish
    from a device returning a normal tuple.
    """
    pass


class GeneratorWrapper(object):
    def __init__(self, value):
        self.value = value


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

    def get_instance(self):
        klass = DEVICES_REGISTER[self.name]
        return klass(*self.args, **self.keywords)


## todo: use entry points instead!
DEVICES_REGISTER = {}


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


def execute(obj, args=()):
    """
    Device -> <pyobj>
    PipelineBlock -> tuple
    Pipeline -> last return value
    """

    if isinstance(obj, Device):
        ## To execute a device, we just pass it all
        ## the arguments.
        ## In case we got streams, we just unwrap them.

        _callable = obj.get_instance()
        return _callable(*args)

    elif isinstance(obj, PipelineBlock):
        ## We need to call all the contained pipelines,
        ## passing arguments.

        _args_matrix = []
        _count = len(obj)
        _results = []

        for arg in args:
            if inspect.isgenerator(arg):
                ## We need a generator for each pipeline
                _args_matrix.append(itertools.tee(arg, _count))

            else:
                ## We just need to pass multiple copies
                _args_matrix.append((arg,) * _count)

        ## We zip the matrix to have each row contain
        ## all the argument calls.
        ## We zip that together with obj to get a list
        ## of (pipe, args) tuples..
        for pipe, args in zip(obj, zip(*_args_matrix)):
            assert isinstance(pipe, Pipeline)
            _results.append(execute(pipe, args))

        return tuple(_results)

    elif isinstance(obj, Pipeline):
        ## We need to keep executing items in the pipeline
        ## passing the return value of each one to the next.

        if args is None:
            args = ()
        wasblock = True  # we could have multiple inputs

        for item in obj:
            assert isinstance(item, (Device, PipelineBlock))

            result = execute(item, args)

            if isinstance(item, PipelineBlock):
                ## Args should be passed as-is to the next one
                assert isinstance(result, tuple)
                wasblock = True
                args = result

            else:
                ## We have only one object to pass to next node
                ## but is it a stream?
                assert isinstance(item, Device)
                wasblock = False
                args = (result,)

        if not wasblock:
            return args[0]
        return args

    else:
        raise TypeError("Not a duck")
