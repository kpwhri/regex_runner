"""
Output frequencies of the identified/captured text from the log file.
"""

import json
import sys
from collections import Counter, defaultdict

from runrex.io.utils import open_all


def read_log_file(inpath, results, *, encoding='utf8'):
    """Read runrex log output file, collecting frequencies by algorithm/category"""
    with open(inpath, encoding=encoding) as fh:
        for line in fh:
            data = json.loads(line)
            label = data['algorithm'] + '_' + data['category']
            if data['text']:
                results[label][data['text'].lower().strip()] += 1


def write_summary_md(outpath, results, *, frequency_cutoff=0, encoding='utf8'):
    """Write output into markdown format"""
    headers = set()
    with open_all(outpath or sys.stdout, 'w', encoding=encoding) as out:
        for label in sorted(results.keys()):
            alg, cat = label.split('_', maxsplit=1)
            if alg not in headers:
                out.write(f'\n# {alg}\n')
                headers.add(alg)
            out.write(f'\n## {cat}\n')
            for text, cnt in results[label].most_common():
                if cnt > frequency_cutoff:
                    out.write(f'* "{text}" ({cnt})\n')
            out.write('\n')


def main(inpath, outpath, *, frequency_cutoff=0, input_encoding='utf8', output_encoding='utf8'):
    results = defaultdict(Counter)
    read_log_file(inpath, results, encoding=input_encoding)
    write_summary_md(outpath, results, frequency_cutoff=frequency_cutoff, encoding=output_encoding)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('-i', '--inpath',
                        help='Input log file from runrex run')
    parser.add_argument('-o', '--outpath', default=None,
                        help='Output markdown file to write to; default to stdout')
    parser.add_argument('--frequency-cutoff', default=0, dest='frequency_cutoff',
                        help='Minimum frequency to include, default to include all')
    parser.add_argument('--input-encoding', default='utf8', dest='input_encoding',
                        help='Encoding of input log file')
    parser.add_argument('--output-encoding', default='utf8', dest='output_encoding',
                        help='Encoding of output markdown file')
    args = parser.parse_args()
    main(args.inpath, args.outpath, frequency_cutoff=args.frequency_cutoff,
         input_encoding=args.input_encoding, output_encoding=args.output_encoding)
