from __future__ import absolute_import

import collections

from dq.ast import Device, Pipeline, Expression
from dq.execution import DEVICES_REGISTER, execute
from dq.parser import parser


class SimpleInputDevice(object):
    def __call__(self):
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


class SimpleFilter(object):
    def __init__(self, condition):
        self.condition = condition

    def __call__(self, stream):
        for item in stream:
            if self.condition.evaluate(loc={'item': item}):
                yield item


class RecordingOutput(object):
    def __call__(self, stream):
        return list(stream)


DEVICES_REGISTER.update({
    'IN': SimpleInputDevice,
    'filter': SimpleFilter,
    'OUT': RecordingOutput,
})


def test_simple_pipeline():
    D1 = Device.from_star('IN')
    cond = Expression.from_string('item.price >= 50')
    D2 = Device.from_star('filter', cond)
    D3 = Device.from_star('OUT')

    pipe = Pipeline([D1, D2, D3])
    result = execute(pipe)

    assert len(result) == 6
    assert result[0] == (5, 'item-5', 50.0)
    assert result[1] == (6, 'item-6', 60.0)
    assert result[2] == (7, 'item-7', 70.0)
    assert result[3] == (8, 'item-8', 80.0)
    assert result[4] == (9, 'item-9', 90.0)
    assert result[5] == (10, 'item-10', 100.0)


def test_simple_pipeline_parsed():
    pipe = parser.parse("""
    IN() | filter(item.price >= 50) | OUT()
    """)

    result = execute(pipe)

    assert len(result) == 6
    assert result[0] == (5, 'item-5', 50.0)
    assert result[1] == (6, 'item-6', 60.0)
    assert result[2] == (7, 'item-7', 70.0)
    assert result[3] == (8, 'item-8', 80.0)
    assert result[4] == (9, 'item-9', 90.0)
    assert result[5] == (10, 'item-10', 100.0)


def test_simple_block():
    pipe = parser.parse("""
    IN() | {
        filter(item.price >= 90) | OUT() ,
        filter(item.price < 20) | OUT()
    }
    """)
    result = execute(pipe)

    assert isinstance(result, tuple)
    assert len(result) == 2

    assert result[0] == [
        (9, 'item-9', 90.0),
        (10, 'item-10', 100.0),
    ]
    assert result[1] == [
        (1, 'item-1', 10.0),
    ]
