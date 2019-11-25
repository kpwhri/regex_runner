from patterns import burden  # input regular expression
from regex_runner.algo.pattern import Document
from regex_runner.algo.result import Status, Result
from regex_runner.main import process
from regex_runner.schema import validate_config


class CostStatus(Status):
    """
    Defines the 'answers'/results that can be obtained
    """
    NONE = -1
    BURDEN = 1
    SKIP = 99


def get_burden(document: Document, expected=None) -> Result:
    for sentence in document:  # there are various ways to iterate through a document
        if sentence.has_patterns(burden):  # define an algorithm by searching for patterns
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
