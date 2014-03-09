# dq - Data query tool

sed made smarter :)

This project goal is providing a tool to quickly inspect / manipulate
structured data from the command line, without having to write hackish
(and usually faulty) regular expressions, nor to write the same
boilerplate code over and over, just to extract some links from
a web page..


## Supported formats

Or, a bunch of formats we're planning to support in the core.
There are plans to make them extendible via plugins, so no worry if
your favourite one is not listed (yet).


**Tabular data:**

- CSV files (all csv dialects)
- OpenOffice calc datasheets
- MS Excel files

**Structured data:**

- Json files
- mspack, protobuf, bson, ..
- files based on C structs
- XML files
- HTML files


## Planned features

- Parsing, filtering and outputting of different formats
- Ability to make joins between sources
- (cached) indexes on files, to speed up multiple queries


## Query structure

See the ``SYNTAX.md`` file for more information about the supported
syntax.


All the "queries" are systems of pipelines.

Pipelines are composed of "devices" (better name, please!) accepting
one or more inputs and returning one or more outputs.

Devices are just callables accepting one or more streams and returning
a stream or a tuple of streams.


**Example device:**

```
mydevice('arg1', 'arg2', kwargs='like Python!')
```

will result in the instantiation of the device


**Example pipeline:**

```
device1() | device2()
```

will result in the following call:

```
device2(device1())
```

**Example tee:**

Complex pipelines can be built using "tees", devices accepting
more than an input / returning more than an output.

**Example 1: two inputs, one output**

```
(I1() | D1(), I2() | D2()) | T2() | D3() | O1()
```
Results in:

```python
pipe1 = D1()(I1()())
pipe2 = D1()(I1()())
pipe3 = T3()(pipe1, pipe2)
O1()(D3()(pipe3))
```

**Example 2: one input, two outputs**

```
I1() | D1() | T1() | (D3() | O1(), D4() | O2())
```

Results in:

```python
pipe1 = D1()(I1()())
pipe3, pipe4 = T3()(pipe1)
O1()(D3()(pipe3))
O2()(D4()(pipe4))
```

**Example 3: two inputs, two outputs**

```
(I1() | D1(), I2() | D2()) | T3() | (D3() | O1(), D4() | O2())
```

Results in:

```python
pipe1 = D1()(I1()())
pipe2 = D1()(I1()())
pipe3, pipe4 = T3()(pipe1, pipe2)
O1()(D3()(pipe3))
O2()(D4()(pipe4))
```

### Complex piping

```
       +----+ +----+ +----+
       | P1 | | P2 | | P3 |
       +----+ +----+ +----+
          |     |      |
           \    |     /
         +----+----+----+
         | I1 | I2 | I3 |
         +----+----+----+
         |    Device    |
         +----+----+----+
         | O1 | O2 | O3 |
         +----+----+----+
          | |   |    |||
  +-------+ |   |    ||+-------------+
  |      +--+   |    |+-------+      |
  |      |      |    |        |      |
+----+ +----+ +----+ +----+ +----+ +----+
| P4 | | P5 | | P6 | | P7 | | P8 | | P9 |
+----+ +----+ +----+ +----+ +----+ +----+
```

May be defined as:

```
(P1, P2, P3) | Device | ((P4, P5), P6, (P7, P8, P9))
```

And results in this code being executed:

```python
out1, out2, out3 = Device(P1, P2, P3)
P4(out1)
P5(out1)
P6(out2)
P7(out3)
P8(out3)
P9(out3)
```


## Example: filtering a CSV file

Input:

```
first_name,last_name,email
Hector;Baxter;"hector.baxter@example.net"
Dominic;Burns;"dominic.burns@example.com"
Spencer;Villarreal;"spencer.villarreal@example.org"
Molly;Delacruz;"molly.delacruz@example.net"
Cassidy;Finley;"cassidy.finley@example.com"
Valerie;Dorsey;"valerie.dorsey@example.org"
```

Query:

```
csv_input(stdin, header=1)
| filter(re.match('.*\@example.com\$', item['email']))
| sort(key=lambda x: item[x])
| csv_output(stdout)
```


Output:

```
Cassidy;Finley;"cassidy.finley@example.com"
Dominic;Burns;"dominic.burns@example.com"
```


## Example: extracting links from web page


Query:

```
http_input('http://en.wikipedia.org/wiki/XPath')
| xpath('//a/@href')
| text_output(stdout)
```


Output:

```
/wiki/Software_release_life_cycle
/wiki/Programming_language_implementation
/wiki/C_Sharp_(programming_language)
/wiki/Java_(programming_language)
/wiki/JavaScript
/wiki/XSLT
/wiki/XPointer
/wiki/XML_Schema_(W3C)
/wiki/XForms
/wiki/Query_language
/wiki/Node_(computer_science)
/wiki/XML
/wiki/String_(computer_science)
/wiki/Boolean_datatype
```
