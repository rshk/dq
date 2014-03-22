import csv
import collections

from .base import FileSource, FileSink

## todo: figure out a nice way to load field names from file
##       while allowing user to pass them by hand too..


class InCSV(FileSource):
    def __init__(self, csvfile, fieldnames=None, header=None, **kw):
        super(InCSV, self).__init__(csvfile)

        ## If ``header=True``, the first line will be used as
        ## field headers.

        if header and (fieldnames is not None):
            raise ValueError("You can only specify one of fieldnames, header")

        self._csv_header = header.evaluate() if header is not None else False
        self._csv_fieldnames = (fieldnames.evaluate()
                                if fieldnames is not None else None)

        self._conf = dict((k, v.evaluate()) for k, v in kw.iteritems())

    def __call__(self):
        reader = csv.reader(self.fp, **self._conf)
        fieldnames = None

        if self._csv_header:
            ## This means: take first line as header
            fieldnames = tuple(next(reader))
        elif self._csv_fieldnames:
            fieldnames = tuple(self._csv_fieldnames)

        if fieldnames is not None:
            row_factory = collections.namedtuple('row', fieldnames)
        else:
            row_factory = tuple

        ## This method needs to be a generator..
        for line in reader:
            yield row_factory(line)


class OutCSV(FileSink):
    def __init__(self, csvfile, fieldnames=None, autoheader=False, **kw):
        super(InCSV, self).__init__(csvfile)

        self._csv_autoheader = autoheader
        self._fieldnames = fieldnames
        self._conf = kw

    def __call__(self, stream):
        ## todo: how to handle autoheader? (to handle properly
        ##       we lose asynchronousness..)
        ## todo: use correct order if a header is specified..

        writer = csv.writer(self.fp, **self._conf)
        for row in stream:
            writer.writerow(row)
