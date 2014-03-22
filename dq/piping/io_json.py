import json

from .base import FileSource


class InJSON(FileSource):
    def __call__(self):
        return json.load(self.fp)


class OutJSON(FileSource):
    def __call__(self, obj):
        return json.load(self.fp)
