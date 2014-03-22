import csv

from .base import FileSource, FileSink

## todo: figure out a nice way to load field names from file
##       while allowing user to pass them by hand too..


class InCSV(FileSource):
    def __init__(self, csvfile, fieldnames=None, header=False, **kw):
        super(InCSV, self).__init__(csvfile)

        ## If ``header=True``, the first line will be used as
        ## field headers.

        if header and (fieldnames is not None):
            raise ValueError("You can only specify one of fieldnames, header")

        self._csv_header = header
        self._csv_fieldnames = fieldnames

        self._conf = kw

    def __call__(self):
        if self._csv_header or self._csv_fieldnames:
            reader = csv.DictReader()
            pass

        reader = csv.reader(self.fp, **self._conf)
        return iter(reader)  # Hide actual object


class OutCSV(FileSink):
    def __init__(self, csvfile, fieldnames=None, autoheader=False, **kw):
        super(InCSV, self).__init__(csvfile)

        self._csv_autoheader = autoheader
        self._fieldnames = fieldnames
        self._conf = kw

    def __call__(self, stream):
        ## todo: we need a decent way to write output rows
        ##       if items are dictionaries.

        fp = self._csvfile
        if isinstance(fp, basestring):
            fp = open(fp, 'wb')

        writer = csv.writer(fp, **self._conf)
        for row in stream:
            writer.writerow(row)
