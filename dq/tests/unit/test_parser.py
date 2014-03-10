from dq.parser import Pipeline, PipelineBlock, Device
from .utils import parser  # noqa


def test_simple_parsing(parser):
    result = parser.parse("""
    DEV1() | DEV2()
    """)

    assert isinstance(result, Pipeline)
    assert len(result) == 2

    assert isinstance(result[0], Device)
    assert result[0].name == 'DEV1'

    assert isinstance(result[1], Device)
    assert result[1].name == 'DEV2'


def test_parsing_blocks(parser):
    result = parser.parse("""
    { DEV1() | DEV2() , DEV3() | DEV4() } | MERGE()
    """)

    assert isinstance(result, Pipeline)
    assert len(result) == 2

    assert isinstance(result[0], PipelineBlock)
    assert len(result[0]) == 2

    assert isinstance(result[0][0], Pipeline)
    assert len(result[0][0]) == 2
    assert isinstance(result[0][0][0], Device)
    assert result[0][0][0].name == 'DEV1'
    assert isinstance(result[0][0][1], Device)
    assert result[0][0][1].name == 'DEV2'

    assert isinstance(result[0][1], Pipeline)
    assert len(result[0][1]) == 2
    assert isinstance(result[0][1][0], Device)
    assert result[0][1][0].name == 'DEV3'
    assert isinstance(result[0][1][1], Device)
    assert result[0][1][1].name == 'DEV4'

    assert isinstance(result[1], Device)
    assert result[1].name == 'MERGE'
