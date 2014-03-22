from __future__ import absolute_import

## todo: refactor this thing, as we want tee implementations
##       to match the one in itertools.tee
## todo: create a true parallel tee using multiprocessing
##       -> although it might be hard to do make compatible
##          with itertools.tee...
## todo: then figure out how to test it..

from greenlet import greenlet


##------------------------------------------------------------
## Purpose of a tee is dispatching output from a generator
## to a pool of consumers accepting a stream as input.
##------------------------------------------------------------


class GreenGenerator(object):
    """
    Iterable object, that keep asking parent greenlet
    for the next item.
    """

    def __iter__(self):
        return self

    def __next__(self):
        g_self = greenlet.getcurrent()
        next_item = g_self.parent.switch()
        return next_item

    next = __next__  # For python 2


def dispatch_stream(stream, *consumers):
    greenlets = [greenlet(c) for c in consumers]
    for g in greenlets:
        g.switch(GreenGenerator())
    for item in stream:
        for g in greenlets:
            g.switch(item)
