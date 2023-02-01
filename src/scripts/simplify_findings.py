"""
Take jsonl logging file and simplify/sort the output for easier use in debugging, etc.
"""

from runrex.cli.simplify_findings import simplify_findings_cli


def main():
    simplify_findings_cli()


if __name__ == '__main__':
    main()
