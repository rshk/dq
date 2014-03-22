from __future__ import absolute_import

from abc import ABCMeta, abstractmethod


class BaseDevice(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def __call__(self):
        pass


class FileSource(BaseDevice):
    """
    Base for devices reading from a file.

    Accepts a ``'name_or_fp'`` constructor argument and provides
    a ``fp`` property to access the open file object.
    """

    _open_binary = True
    _openfile = None
    _name_or_fp = None

    def __init__(self, name_or_fp):
        self._name_or_fp = name_or_fp.evaluate()

    @property
    def fp(self):
        if self._openfile is None:
            if isinstance(self._name_or_fp, basestring):
                mode = 'rb' if self._open_binary else 'r'
                self._openfile = open(self._name_or_fp, mode)
            else:
                self._openfile = self._name_or_fp
        return self._openfile


class FileSink(BaseDevice):
    """
    Base for devices writing to a file.

    Accepts a ``'name_or_fp'`` constructor argument and provides
    a ``fp`` property to access the open file object.
    """

    _open_binary = True
    _openfile = None
    _name_or_fp = None

    def __init__(self, name_or_fp):
        self._name_or_fp = name_or_fp.evaluate()

    @property
    def fp(self):
        if self._openfile is None:
            if isinstance(self._name_or_fp, basestring):
                mode = 'wb' if self._open_binary else 'w'
                self._openfile = open(self._name_or_fp, mode)
            else:
                self._openfile = self._name_or_fp
        return self._openfile
