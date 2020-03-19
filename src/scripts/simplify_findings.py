"""
Take jsonl logging file and simplify/sort the output for easier use in debugging, etc.
"""
import json
import os
from collections import defaultdict
from datetime import datetime


def add_text(store, algo, text):
    if text in store[algo]:
        return False
    store[algo].add(text)
    return True


class Writer:

    def __init__(self, path, encoding='utf8'):
        self.path = path
        self.encoding = encoding
        self.dt = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.text = {}
        self.jsonl = {}

    def write(self, key, text, data):
        if key not in self.text:
            label = f'{key}_{self.dt}'
            self.text[key] = open(os.path.join(self.path, f'{label}.txt'), 'w', encoding=self.encoding)
            self.jsonl[key] = open(os.path.join(self.path, f'{label}.jsonl'), 'w', encoding=self.encoding)
        self.text[key].write(f'\n## {data["name"]}\n')
        self.text[key].write(f'{text}\n')
        self.jsonl[key].write(f'{json.dumps(data)}\n')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for fh in self.text.values():
            fh.close()
        for fh in self.jsonl.values():
            fh.close()


def main(logfile, outpath, *, encoding='utf8'):
    store = defaultdict(set)
    with open(logfile, encoding=encoding) as fh:
        os.makedirs(outpath, exist_ok=True)
        with Writer(outpath, encoding=encoding) as writer:
            for line in fh:
                data = json.loads(line)
                algo = data['algorithm']
                category = data['category']
                text = data['text']
                try:
                    del data['matches']
                except KeyError:
                    pass
                if add_text(store, algo, text):
                    writer.write(f'{algo}_{category}', text, data)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(fromfile_prefix_chars='@!')
    # required
    parser.add_argument('--logfile', required=True, help='Input logfile')
    parser.add_argument('--outpath', required=True, help='Path to place output files')
    # optional
    parser.add_argument('--encoding', default='utf8', help='File encoding')

    args = parser.parse_args()
    main(**vars(args))
