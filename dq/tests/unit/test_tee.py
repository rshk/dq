"""
Test for pipe "tees".

todo: use the one provided by itertools instead..
"""

from dq.piping.tee import dispatch_stream


def test_tee():
    output = []
    producer = xrange(5)

    def consumer1(stream):
        for item in stream:
            output.append((1, item))

    def consumer2(stream):
        for item in stream:
            output.append((2, item))

    def consumer3(stream):
        for item in stream:
            output.append((3, item))

    dispatch_stream(producer, consumer1, consumer2, consumer3)

    assert output == [
        (1, 0), (2, 0), (3, 0),
        (1, 1), (2, 1), (3, 1),
        (1, 2), (2, 2), (3, 2),
        (1, 3), (2, 3), (3, 3),
        (1, 4), (2, 4), (3, 4),
    ]
