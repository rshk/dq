from .base import BaseDevice


class Filter(BaseDevice):
    def __init__(self, condition):
        self.condition = condition

    def __call__(self, stream):
        for item in stream:
            if self.condition.evaluate(loc={'item': item}):
                yield item


class Transform(BaseDevice):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, stream):
        for item in stream:
            for name, expr in self.kwargs.iteritems():
                item[name] = expr.evaluate(loc={'item': item})
                yield item
