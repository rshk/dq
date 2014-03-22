import lxml.html

from .base import FileSource


class InXML(FileSource):
    def __call__(self):
        return lxml.html.fromstring(self.fp.read())
