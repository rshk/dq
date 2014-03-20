import ast
import collections


class MultipleOutput(tuple):
    """
    Used to indicate this tuple contains multiple
    outputs, from a block, in order to distinguish
    from a device returning a normal tuple.
    """
    pass


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

    def execute(self, *args):
        """
        Execute the pipeline, with optional input argument(s).

        This will iterate all the devices/blocks in the pipe
        and call them passing the return value from the previous
        one.

        :param args:
            - 0 arguments: initial pipeline
            - 1 argument: pipeline with a single input
            - >1 arguments: pipeline with input from a block
        """

        ## The first one should be executed with args
        ## from the function call, if any.
        ## Subsequent ones should be called with return value.

        for item in self:
            args = item.execute(*args),  # comma is not a typo!

        return args[0]


class PipelineBlock(WrappedList):
    def __repr__(self):
        contents = ', '.join(repr(x) for x in self)
        return '{{ {0} }}'.format(contents)

    def execute(self, *args):
        """
        Execute a pipeline block, passing arguments
        to all the contained pipelines or blocks.

        .. note::
            If inputs are generators, we want to
            dispatch them to all functions.

            Problem is, what if some inputs are
            generators and some are not? We risk
            deadlocking while waiting for a function
            to iterate..

            A solution would be to disallow chaining
            two blocks, they must pass through a device
            that merges stuff in a smarter way..
        """
        pass


class Device(object):
    """
    Parsed object for containers.

    Contains:

    - the device name
    - a list of expressions to be passed as constructor arguments
    """

    def __init__(self, *args, **keywords):
        """
        :param name: function name
        :param args: list of Expression instances
        :param keywords: dict of {string: Expression}
        """

        self.args = args
        self.keywords = keywords

    def __repr__(self):
        arguments = []
        for a in self.args:
            arguments.append(repr(a))
        for k, v in self.keywords.iteritems():
            arguments.append('{0}={1!r}'.format(k, v))
        return "{fn}({args})".format(
            fn=self.__class__.__name__,
            args=', '.join(arguments))

    def execute(self, *args):
        raise NotImplementedError(
            "Must be implemented in subclasses")


class GenericDevice(Device):
    def __init__(self, *args, **kwargs):
        self.name = args[0]
        args = args[1:]
        return super(GenericDevice, self).__init__(*args, **kwargs)


## todo: use entry points instead!
DEVICES_REGISTER = {}


def get_device(name, args, kwargs):
    if name in DEVICES_REGISTER:
        klass = DEVICES_REGISTER.get(name)
        return klass(*args, **kwargs)
    return GenericDevice(name, *args, **kwargs)


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
