# Syntax specification

The syntax is very simple, and is composed of:

- Pipeline control
- Python expressions

## Pipeline control

- The pipe ``|`` operator is used to indicate pipelining
- Curly braces ``{`` and ``}`` are used to delimit sub-pipes
- Commas are used to separate sub-pipes inside braces.
- Pipeline "devices" instantiation syntax matches Python syntax
  for function call, everything inside parentheses is treated
  as a Python expression.


### Simple example

```
InputCSV(stdin, header=1) | Filter(this['foo'] == 'bar') | OutputCSV(stdout)
```

Will result in:

```python
d1 = InputCSV(stdin, header=1)
d2 = Filter(this['foo'] == 'bar')
d3 = OutputCSV(stdout)

d3(d2(d1))
```


### Multiple inputs

A function can accept multiple pipelines as input. They will simply
be passed as positional arguments to the function, in order.

```
{ InputCSV('file1.csv') , InputCSV('file2.csv') } | MergeCSV() | OutputCSV(stdout)
```

Will result in:

```python
d1 = InputCSV('file1.csv')
d2 = InputCSV('file2.csv') }
d3 = MergeCSV()
d4 = OutputCSV(stdout)

d4(d3(d1(), d2()))
```


### Multiple outputs

Multiple outputs can be specified for a device.
In that case:

- if the device returns a tuple of generators, they will be passed
  to output pipelines one-by-one. If the count mismatches, an exception
  is raised.

- if the device returns a single generator, its output will be
  sent in parallel to all the output pipes, using greenlets.

If the device returns a tuple of generators, and a single output pipe
is specified (omitting braces), they will be just passed as positional
arguments to the output pipe.


#### Examples

The ``TEE`` function below is specially-purposed and will dispatch
items from the stream to each of the functions passed as extra
arguments, using greenlet-based concurrency.

**Multiple outputs:**

```
DEV | { OUT1 , OUT2 }
```

will result in:

```python
result = DEV
if isinstance(result, tuple):
	assert len(result) == 2
	OUT1(result[0])
	OUT2(result[1])
else:
	TEE(result, OUT1, OUT2)
```

Multiple outputs (but just one pipe!)

```
DEV | { OUT1 }
```

will result in:

```python
result = DEV
if isinstance(result, tuple):
	assert len(result) == 1
	OUT1(result[0])
else:
	TEE(result, OUT1)  # equivalent to OUT1(result)
```

Multiple outputs, one output pipe (no braces!):

```
DEV | OUT1
```

will result in:

```python
result = DEV
if isinstance(result, tuple):
	OUT1(*result)
else:
	OUT1(result)
```


### Dispatching output to two output pipes

**Use case:** we have a csv file of people records, containing
first name, last name, gender. We want to split records between
male and female.

A query like this can be used:

```
csv_input('people.txt', header=1) | {
	filter(item['gender'] == 'male') | csv_output('males.csv'),
	filter(item['gender'] == 'female') | csv_output('females.csv')
}
```


Which will result in:

```python
i1 = csv_input(sys.stdin, header=1)
f1 = filter(item['gender'] == 'male')
o1 = csv_output('males.csv'),
f2 = filter(item['gender'] == 'female')
o2 csv_output('females.csv')

TEE(i1, lambda x: o1(f1(x)), lambda x: o2(f2(x)))
```


## Proposed syntax for variables

Variables can be defined as ``$name`` and just act as placeholders
for pieces of code.

```
$input = csv_input('people.txt', header=1);
$males = filter(item['gender'] == 'male') | csv_output('males.csv');
$females = filter(item['gender'] == 'female') | csv_output('females.csv');

$input | { $males , $females }
```

Things that we need to decide:

- Can they accept arguments, thus become actually "functions" or "macros"?

- Are they just "placeholders" for code, or should they hold actual state?

  Example:

  ```
  $foo = something();

  $foo | $foo
  ```

  Should result in:

  ```python
  foo = something();
  foo(foo())
  ```

  or in:

  ```python
  something(something());
  ```

  ?
