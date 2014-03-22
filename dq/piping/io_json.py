import json

from .base import FileSource, FileSink


class InJSON(FileSource):
    def __call__(self):
        return json.load(self.fp)


class OutJSON(FileSink):
    def __call__(self, obj):
        return json.dump(obj, self.fp)
