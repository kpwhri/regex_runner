import abc
import csv
import datetime
import json
import os

from runrex.io import sqlai, formatter

DATETIME_STR = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')


class NullFileWrapper:

    def __init__(self):
        self._header = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def writeline(self, data_func):
        pass


class FileWrapper:

    def __init__(self, file, path=None, header=None, encoding='utf8', **kwargs):
        if path:
            self.fp = os.path.join(path, file)
            os.makedirs(path, exist_ok=True)
        else:
            self.fp = file
        self.fh = None
        self._header = header or []
        self.encoding = encoding

    def __enter__(self):
        if self.fp:
            self.fh = open(self.fp, 'w', encoding=self.encoding)
            self.writeline(self._header)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fh:
            self.fh.close()

    def writeline(self, data_func, sep=None):
        line = data_func(self._header).values()
        if sep:
            self.fh.write(sep.join(self.clean_list(line)) + '\n')
        else:
            self.fh.write(self.clean(line) + '\n')

    def clean(self, val):
        return str(val).replace('\n', ' ~~')

    def clean_list(self, lst):
        for el in lst:
            yield self.clean(el)


class CsvFileWrapper(FileWrapper):

    def __init__(self, file, path=None, header=None, delimiter=',', **kwargs):
        super().__init__(file, path=path, header=header, **kwargs)
        self.writer = None
        self.delimiter = delimiter

    def __enter__(self):
        if self.fp:
            self.fh = open(self.fp, 'w', newline='')
            self.writer = csv.writer(self.fh, delimiter=self.delimiter)
            self.writer.writerow(self._header)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fh:
            self.fh.close()

    def writeline(self, data_func, **kwargs):
        if self.writer:
            line = data_func(self._header).values()
            self.writer.writerow(self.clean_list(line))


class TsvFileWrapper(CsvFileWrapper):

    def __init__(self, file, path=None, header=None, delimiter='\t', **kwargs):
        super().__init__(file, path=path, header=header, delimiter=delimiter, **kwargs)


class JsonlWrapper(FileWrapper):

    def __init__(self, file, path=None, header=None, **kwargs):
        super().__init__(file, path, header, **kwargs)

    def __enter__(self):
        if self.fp:
            self.fh = open(self.fp, 'w', encoding=self.encoding)
        return self

    def writeline(self, data_func, sep=None):
        d = data_func(self._header)
        self.fh.write(json.dumps(d) + '\n')


class TableWrapper:

    def __init__(self, tablename, driver, server, database, header=None, **kwargs):
        self._header = header or []
        self.eng = sqlai.get_engine(driver=driver, server=server, database=database)
        self.tablename = f'{tablename}'

    def __enter__(self):
        formatter.create_table(self.tablename, self._header, self.eng)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.eng.dispose()

    def _quote(self, val):
        if isinstance(val, (int, float)):
            return val
        elif val is None:
            return 'NULL'
        else:
            return str(val)

    def writeline(self, data_func):
        d = data_func(self._header)
        self.eng.execute(f"insert into {self.tablename} ({','.join(d.keys())}) "
                         f"VALUES ({', '.join(self._quote(v) for v in d.values())})")


def get_file_wrapper(name=None, kind=None, path=None,
                     driver=None, server=None, database=None, **kwargs):
    if not name:
        return NullFileWrapper()
    name = name.replace('{datetime}', DATETIME_STR)
    header = ('id', 'name', 'algorithm', 'value', 'category', 'date', 'start', 'end', 'extras')
    if kind == 'csv' or name.endswith('.csv'):
        return CsvFileWrapper(name, path, header=header, **kwargs)
    elif kind == 'tsv' or name.endswith('.tsv'):
        return TsvFileWrapper(name, path, header=header, **kwargs)
    elif kind == 'sql':
        return TableWrapper(name, driver, server, database, **kwargs)
    elif kind == 'jsonl' or name.endswith('.jsonl'):
        return JsonlWrapper(name, path, header=header, **kwargs)
    else:
        raise ValueError('Unrecognized output file type.')


def get_logging(directory='.', kind='jsonl', ignore=False,
                driver=None, server=None, database=None, **kwargs):
    header = ('name', 'algorithm', 'value', 'category', 'matches', 'text', 'start', 'end')
    if ignore:
        return NullFileWrapper()
    elif kind == 'tsv':
        return TsvFileWrapper(path=directory,
                              file=f'text_{DATETIME_STR}.out.tsv',
                              header=header, **kwargs)
    elif kind == 'csv':
        return CsvFileWrapper(path=directory,
                              file=f'text_{DATETIME_STR}.out.csv',
                              header=header, **kwargs)
    elif kind == 'sql':
        return TableWrapper(f'text_{DATETIME_STR}_out', driver, server, database, **kwargs)
    elif kind == 'jsonl':
        return JsonlWrapper(path=directory, file=f'text_{DATETIME_STR}.out.jsonl',
                            header=header, **kwargs)
    else:
        raise ValueError('Unrecognized output file type.')
