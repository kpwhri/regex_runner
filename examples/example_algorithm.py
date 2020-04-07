from example_patterns import BURDEN  # input regular expression
from runrex.text import Document
from runrex.algo.result import Status, Result
from runrex.main import process
from runrex.schema import validate_config


class CostStatus(Status):
    """
    Defines the 'answers'/results that can be obtained
    """
    NONE = -1
    BURDEN = 1
    SKIP = 99


def get_burden(document: Document, expected=None) -> Result:
    for sentence in document:  # there are various ways to iterate through a document
        if sentence.has_patterns(BURDEN):  # define an algorithm by searching for patterns
            yield Result(CostStatus.BURDEN, CostStatus.BURDEN.value, expected, text=sentence.text)


def main(config_file):
    conf = validate_config(config_file)
    algorithms = {
        'burden': get_burden,
    }
    process(**conf, algorithms=algorithms)


if __name__ == '__main__':
    import sys

    try:
        main(sys.argv[1])
    except IndexError:
        raise AttributeError('Missing configuration file: Usage: main.py file.(json|yaml|py)')
