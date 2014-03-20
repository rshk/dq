import collections

from dq.objects import Device, Pipeline, PipelineBlock, Expression


class SimpleInputDevice(Device):
    def execute(self):
        product = collections.namedtuple('product', 'id,name,price')
        rows = [
            (1, 'item-1', 10.0),
            (2, 'item-2', 20.0),
            (3, 'item-3', 30.0),
            (4, 'item-4', 40.0),
            (5, 'item-5', 50.0),
            (6, 'item-6', 60.0),
            (7, 'item-7', 70.0),
            (8, 'item-8', 80.0),
            (9, 'item-9', 90.0),
            (10, 'item-10', 100.0),
        ]
        for row in rows:
            yield product(*row)


class SimpleFilter(Device):
    def execute(self, stream):
        condition = self.args[0]
        for item in stream:
            if condition.evaluate(loc={'item': item}):
                yield item


class RecordingOutput(Device):
    def execute(self, stream):
        return list(stream)


def test_simple_pipeline():
    D1 = SimpleInputDevice()
    D2 = SimpleFilter(Expression.from_string('item.price >= 50'))
    D3 = RecordingOutput()

    pipe = Pipeline([D1, D2, D3])
    result = pipe.execute()

    assert len(result) == 6
