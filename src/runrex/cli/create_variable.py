import argparse
import pathlib
import datetime
import json

from runrex.post.variable_builder import build_variables


def create_variable(file, metafile, output_directory=None, extra_condition=None, variable_file=None,
                    max_col_length=None, transformer_file=None):
    """

    :param extra_condition:
    :param variable_file:
    :param file:
    :param metafile:
    :param output_directory:
    :return:
    """
    with open(variable_file) as fh:
        var_data = json.load(fh)
    with open(transformer_file) as fh:
        transformer_data = json.load(fh)
    res = build_variables(file, metafile, extra_condition=extra_condition, column_name_transformers=transformer_data,
                          max_col_length=max_col_length, **var_data)
    if not output_directory:
        output_directory = file.parent
    res.to_csv(
        output_directory / f'final_variables_{datetime.datetime.now().strftime("%Y%m%d")}_from_{file.name}.csv',
        index=False
    )


def create_variable_cli():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@!')
    parser.add_argument('-i', '--file', required=True, type=pathlib.Path,
                        help='Fullpath to file output CSV from `extract_and_load_json`.')
    parser.add_argument('-m', '--metafile', required=True, type=pathlib.Path,
                        help='Fullpath to CSV file containing metadata. Must at least contain:'
                             ' doc_id, patient_id, total_text_length, date. May also contain'
                             ' other variables as well.')
    parser.add_argument('--extra-condition', dest='extra_condition', default=None,
                        help='Name of a new column in the metafile that should be used in building'
                             ' variables.')
    parser.add_argument('--output-directory', dest='output_directory', required=False, type=pathlib.Path,
                        help='Output directory to place extracted files.')
    parser.add_argument('--variable-file', dest='variable_file', required=False, default=None, type=pathlib.Path,
                        help='json file containing dict of variables to build using variable builder syntax'
                             ' (see runrex.post.variable_builder.py for details).')
    parser.add_argument('--transformer-file', dest='transformer_file', required=False, default=None, type=pathlib.Path,
                        help='json file containing dict of variable length-reduction {long[str]: short[str]}'
                             ' (see runrex.post.variable_builder.py for details).')
    parser.add_argument('--max-col-length', dest='max_col_length', type=int, default=None,
                        help='Limit column names to this many characters (e.g., for SAS limit to 32.')
    args = parser.parse_args()
    create_variable(args.file, args.metafile,
                    output_directory=args.output_directory,
                    variable_file=args.variable_file,
                    transformer_file=args.transformer_file,
                    max_col_length=args.max_col_length,
                    extra_condition=args.extra_condition)
