# Pipelines

This document explains how pipelines are built / executed.


## device | device

The simplest case: a single device is outputting a single object.

```
               +---------+
               |         |
               |   DEV0  |
               |         |
               +---------+
                    |
               +---------+
               |         |
               |   DEV1  |
               |         |
               +---------+
```

The execution will result in:

```python
DEV1(DEV0())
```

## device | block

Output from the device will be multiplexed.

```
               +---------+
               |         |
               |   DEV0  |
               |         |
               +---------+
                    |
     +--------------+--------------+
     |              |              |
+---------+    +---------+    +---------+
|         |    |         |    |         |
|   DEV1  |    |   DEV2  |    |   DEV3  |
|         |    |         |    |         |
+---------+    +---------+    +---------+
```

If the output is a "consumable" iterator, we need to send the items in parallel
to the sub-devices through a tee:


```python
TEE(DEV0(), DEV1, DEV2, DEV3)
```

Otherwise, we just send the object to other pipes:

```python
output = DEV0()
DEV1(output)
DEV2(output)
DEV3(output)
```


**todo:** deepcopy to prevent changes?

**todo:** how to check whether this is consumable?


## block | device

Blocks have multiple outputs, one for each contained pipeline.

Outputs will be passed as multiple arguments to device

```
+---------+    +---------+    +---------+
|         |    |         |    |         |
|   DEV1  |    |   DEV2  |    |   DEV3  |
|         |    |         |    |         |
+---------+    +---------+    +---------+
     |              |              |
     +--------------+--------------+
                    |
               +---------+
               |         |
               |   DEV0  |
               |         |
               +---------+
```

```python
DEV0(DEV1(), DEV2(), DEV3())
```


## block | block

This is similar to ``device | block``, but trickier: what if arguments
are mixed objects / streams? How to multiplex, especially avoiding deadlocks?

Maybe it would be worth to use true parallelism, distributing the pipes
in multiple concurrent processes (multiprocessing module).

