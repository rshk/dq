from dq.objects import Pipeline, PipelineBlock, Device
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


def test_parsing_with_pyargs(parser):
    text = """
    Input('myfile.csv', sep=';', header=1)
    | Filter(item.first_name == 'hello')
    | Output('myfile2.csv', sep=',')
    """
    tree = parser.parse(text)
    assert isinstance(tree, Pipeline)
    assert len(tree) == 3

    ## Input('myfile.csv', sep=';', header=1)
    assert isinstance(tree[0], Device)
    assert tree[0].name == 'Input'
    assert tree[0].args[0].evaluate() == 'myfile.csv'
    assert tree[0].keywords['sep'].evaluate() == ';'
    assert tree[0].keywords['header'].evaluate() == 1

    ## Filter(item.first_name == 'hello')
    assert isinstance(tree[1], Device)

    ## Output('myfile2.csv', sep=',')
    assert isinstance(tree[1], Device)


def test_parsing_with_blocks_and_pyargs(parser):
    text = """
    { Dev1("foo", name='bar') | Dev2(hello == 'world'),
      Dev3() | Dev4(example=item + 100) }
    | Collector(bla="foobar") | Piped('here') | {
      Out1(), Out2(), Filter() | Out3(),
    }
    """

    tree = parser.parse(text)
    assert isinstance(tree, Pipeline)
    assert len(tree) == 4

    # { Dev1("foo", name='bar') | Dev2(hello == 'world'),
    #   Dev3() | Dev4(example=item + 100) }
    assert isinstance(tree[0], PipelineBlock)
    assert len(tree[0]) == 2

    # Dev1("foo", name='bar') | Dev2(hello == 'world')
    assert isinstance(tree[0][0], Pipeline)

    assert isinstance(tree[0][0][0], Device)
    assert tree[0][0][0].name == 'Dev1'
    assert len(tree[0][0][0].args) == 1
    assert len(tree[0][0][0].keywords) == 1
    assert tree[0][0][0].keywords['name'].evaluate() == 'bar'

    assert isinstance(tree[0][0][1], Device)
    assert tree[0][0][1].name == 'Dev2'
    assert tree[0][0][1].keywords == {}
    assert tree[0][0][1].args[0].evaluate({'hello': 'world'}) is True
    assert tree[0][0][1].args[0].evaluate({'hello': 'nothing'}) is False

    # Dev3() | Dev4(example=item + 100)
    assert isinstance(tree[0][1], Pipeline)

    assert isinstance(tree[0][1][0], Device)
    assert tree[0][1][0].name == 'Dev3'
    assert tree[0][1][0].args == ()
    assert tree[0][1][0].keywords == {}

    assert isinstance(tree[0][1][1], Device)
    assert tree[0][1][1].name == 'Dev4'
    assert tree[0][1][1].args == ()
    assert tree[0][1][1].keywords['example'].evaluate({'item': 10}) == 110

    # Collector(bla="foobar")
    assert isinstance(tree[1], Device)

    # Piped('here')
    assert isinstance(tree[2], Device)

    # { Out1(), Out2(), Filter() | Out3() }
    assert isinstance(tree[3], PipelineBlock)
