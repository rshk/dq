from .base import BaseDevice

import copy


class Filter(BaseDevice):
    def __init__(self, condition):
        self.condition = condition

    def __call__(self, stream):
        for item in stream:
            if self.condition.evaluate({'item': item}):
                yield item


class Transform(BaseDevice):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, stream):
        for item in stream:
            _item = copy.deepcopy(item)
            for name, expr in self.kwargs.iteritems():
                _item[name] = expr.evaluate({'item': _item})
            yield _item


class Map(BaseDevice):
    def __init__(self, expr):
        self.expr = expr

    def __call__(self, stream):
        for item in stream:
            yield self.expr.evaluate({'item': item})


class List(BaseDevice):
    def __call__(self, stream):
        return list(stream)


class Dict(BaseDevice):
    def __call__(self, stream):
        return dict(stream)
