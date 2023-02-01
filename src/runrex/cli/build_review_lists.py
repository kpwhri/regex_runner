import argparse
import pathlib

from runrex.post.build_review_lists import build_review_lists


def build_review_lists_cli():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='!@')
    parser.add_argument('--output-file', dest='output_file', required=True, type=pathlib.Path,
                        help='Output file for runrex. Either jsonl or csv.')
    parser.add_argument('--log-file', dest='log_file', required=True, type=pathlib.Path,
                        help='Loginfo file output by runrex. (jsonl format)')
    parser.add_argument('--metafile', required=True, type=pathlib.Path,
                        help='Fullpath to CSV file containing metadata. Must at least contain:'
                             ' doc_id, text. May also contain'
                             ' other variables as well.')
    build_review_lists(**vars(parser.parse_args()))
