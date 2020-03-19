import logging
from collections import defaultdict

from runrex.io.corpus import get_next_from_corpus, Skipper
from runrex.io.formatter import format_data_as_dict
from runrex.io.out import get_file_wrapper, get_logging
from runrex.io.report import Reporter
from runrex.schema import validate_config
from runrex.util import kw


def parse_annotation_file(file=None, data=None):
    if not data:
        data = defaultdict(lambda: None)
    if file:
        with open(file) as fh:
            for line in fh:
                name, res, *comments = line.strip().split()
                data[name] = int(res)
    return data


def parse_annotation_files(*configs, data=None):
    for config in configs:
        data = parse_annotation_file(data=data, **kw(config))
    return data


def process(corpus=None, annotation=None, annotations=None, output=None, select=None,
            algorithms=None, loginfo=None, skipinfo=None, logger=None, ssplit=None):
    """

    :param corpus:
    :param annotation:
    :param annotations:
    :param output:
    :param select:
    :param algorithms: dict of name -> algorithm function
    :param loginfo:
    :param skipinfo:
    :param logger:
    :return:
    """
    if logger and not logger['verbose']:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    truth = parse_annotation_file(**kw(annotation))
    truth = parse_annotation_files(*annotations or list(), data=truth)
    if not algorithms:
        raise ValueError('No algorithms specified!')
    results = {name: Reporter() for name in algorithms}
    number_id = 0
    with get_file_wrapper(**output) as out, \
            get_logging(**kw(loginfo)) as log, \
            Skipper(**kw(skipinfo)) as skipper:
        for i, doc in enumerate(get_next_from_corpus(**kw(corpus), **kw(select),
                                                     skipper=skipper, ssplit=ssplit)):
            for alg_name, alg_func in algorithms.items():
                max_res = None
                for res in alg_func(doc, truth[doc.name]):
                    if res:
                        logging.debug(f'{i}: {doc.name}: {res}')
                        out.writeline(format_data_as_dict(number_id, doc, alg_name, res))
                        number_id += 1
                    elif res.is_skip():  # always skip
                        skipper.add(doc.name)
                        break
                    log.writeline(format_data_as_dict(None, doc, alg_name, res))
                    # only take max
                    if not max_res or res.result > max_res.result:
                        max_res = res
                else:  # avoid if skipped
                    if max_res is not None:
                        results[alg_name].update(max_res)
                        if max_res.expected is not None:
                            logging.info(f'Validation for {doc.name}: {results}')
    logging.warning(f'Final results: {results}')


def main(config_file):
    conf = validate_config(config_file)
    process(**conf)


if __name__ == '__main__':
    import sys

    try:
        main(sys.argv[1])
    except IndexError:
        raise AttributeError('Missing configuration file: Usage: main.py file.(json|yaml|py)')
