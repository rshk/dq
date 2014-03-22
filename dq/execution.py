from __future__ import absolute_import

import inspect
import itertools

from .ast import Pipeline, PipelineBlock, Device


## todo: use entry points instead!
DEVICES_REGISTER = {}


def get_device_instance(name, args, keywords):
    klass = DEVICES_REGISTER[name]
    return klass(*args, **keywords)


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

        _callable = get_device_instance(
            name=obj.name, args=obj.args, keywords=obj.keywords)
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
