"""
Build lists of each variable (algorithm_CATEGORY) for reviewing/debugging.

Currently, the offsets are not quite right, so a few different output options are provided.
"""
from runrex.cli.build_review_lists import build_review_lists_cli


def main():
    build_review_lists_cli()


if __name__ == '__main__':
    main()
