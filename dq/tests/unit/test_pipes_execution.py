from __future__ import absolute_import

import json

from dq.execution import execute
from dq.parser import parser


SIMPLE_CSV = (
    "1,item-1,10.0\r\n"
    "2,item-2,20.0\r\n"
    "3,item-3,30.0\r\n"
    "4,item-4,40.0\r\n"
    "5,item-5,50.0\r\n"
    "6,item-6,60.0\r\n"
    "7,item-7,70.0\r\n"
    "8,item-8,80.0\r\n"
    "9,item-9,90.0\r\n"
    "10,item-10,100.0\r\n"
)
EXP_CSV_OUT1 = "9,item-9,90.0\r\n10,item-10,100.0\r\n"
EXP_CSV_OUT2 = "1,item-1,10.0\r\n"


def test_filter_csv(tmpdir):
    infile = str(tmpdir.join('input.csv'))
    outfile1 = str(tmpdir.join('output1.csv'))
    outfile2 = str(tmpdir.join('output2.csv'))

    with open(infile, 'w') as f:
        f.write(SIMPLE_CSV)

    code = """
    InCSV({0!r}, fieldnames=['id', 'name', 'price']) | {{
        filter(float(item.price) >= 90) | OutCSV({1!r}) ,
        filter(float(item.price) < 20) | OutCSV({2!r})
    }}
    """.format(infile, outfile1, outfile2)

    pipe = parser.parse(code)
    execute(pipe)

    assert open(outfile1).read() == EXP_CSV_OUT1
    assert open(outfile2).read() == EXP_CSV_OUT2


def test_filter_csv_autoheader(tmpdir):
    infile = str(tmpdir.join('input.csv'))
    outfile1 = str(tmpdir.join('output1.csv'))
    outfile2 = str(tmpdir.join('output2.csv'))

    with open(infile, 'w') as f:
        f.write("id,name,price\r\n")
        f.write(SIMPLE_CSV)

    code = """
    InCSV({0!r}, header=True) | {{
        filter(float(item.price) >= 90) | OutCSV({1!r}) ,
        filter(float(item.price) < 20) | OutCSV({2!r})
    }}
    """.format(infile, outfile1, outfile2)

    pipe = parser.parse(code)
    execute(pipe)

    assert open(outfile1).read() == EXP_CSV_OUT1
    assert open(outfile2).read() == EXP_CSV_OUT2


def test_csv_to_json(tmpdir):
    infile = str(tmpdir.join('input.csv'))
    outfile = str(tmpdir.join('output.json'))

    with open(infile, 'w') as f:
        f.write("id,name,price\r\n")
        f.write("1,item-1,10.0\r\n")
        f.write("2,item-2,20.0\r\n")
        f.write("3,item-3,30.0\r\n")

    code = """
    InCSV({0!r}, header=True)
    | Map(item._asdict())
    | List() | OutJSON({1!r})
    """.format(infile, outfile)

    pipe = parser.parse(code)
    execute(pipe)

    assert json.load(open(outfile)) == [
        {'id': '1', 'name': 'item-1', 'price': '10.0'},
        {'id': '2', 'name': 'item-2', 'price': '20.0'},
        {'id': '3', 'name': 'item-3', 'price': '30.0'},
    ]

    code = """
    InCSV({0!r}, header=True)
    | Map(item._asdict())
    | Transform(id=int(item['id']), price=float(item['price']))
    | List() | OutJSON({1!r})
    """.format(infile, outfile)

    pipe = parser.parse(code)
    execute(pipe)

    assert json.load(open(outfile)) == [
        {'id': 1, 'name': 'item-1', 'price': 10.0},
        {'id': 2, 'name': 'item-2', 'price': 20.0},
        {'id': 3, 'name': 'item-3', 'price': 30.0},
    ]
