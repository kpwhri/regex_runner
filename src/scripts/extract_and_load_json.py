"""
Usage:
    for database:
python this_file.py --file <input_jsonl> --version <pytakes|runrex> --connection-string <sqlalchemy-style-connection-string>
    for output file
python this_file.py --file <input_jsonl> --version <pytakes|runrex> --output-directory <directory-to-place-output>
This program automates the process of:
    * summarizing the jsonl data (from pytakes/runrex)
    * extracting/combining/formatting
    * uploading it to a new sql server table

Connection String
===================
* For SQL Alchemy-style connection string, see: https://docs.sqlalchemy.org/en/13/core/engines.html
    - NB: will need to install `pyodbc`
* Example:
    - SQL Server: mssql+pyodbc://SERVER/DATABASE
"""
import csv
import os
import json
import pathlib
from collections import Counter
from typing import Tuple

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

try:
    from loguru import logger
except ModuleNotFoundError:
    import logging as logger

    logger.basicConfig(level=logger.DEBUG)


def create_table(tablename, eng):
    Base = declarative_base()

    class Table(Base):
        __tablename__ = tablename
        id = sa.Column(sa.Integer, primary_key=True)
        doc_id = sa.Column(sa.String(50))
        source = sa.Column(sa.String(100))
        dict_id = sa.Column(sa.Integer)
        algorithm = sa.Column(sa.String(100))
        category = sa.Column(sa.String(100))
        concept = sa.Column(sa.String(100))
        captured = sa.Column(sa.String(100))
        context = sa.Column(sa.String(300))
        certainty = sa.Column(sa.Integer)
        hypothetical = sa.Column(sa.Boolean)
        historical = sa.Column(sa.Boolean)
        other_subject = sa.Column(sa.Boolean)
        start_idx = sa.Column(sa.Integer)
        end_idx = sa.Column(sa.Integer)
        version = sa.Column(sa.String(10))

        def to_list(self) -> Tuple:
            """
            For use in CSV file, etc.
            :return:
            """
            return tuple(getattr(self, x) for x in dir(self) if not x.startswith('_') and x != 'metadata')

    Base.metadata.create_all(eng)
    return Table


def update_counter(counter, qualifiers):
    counter[f'certainty={qualifiers["certainty"]}'] += 1
    counter[f'hypothetical={qualifiers["hypothetical"]}'] += 1
    counter[f'historical={qualifiers["historical"]}'] += 1
    counter[f'other_subject={qualifiers["other_subject"]}'] += 1


def get_pytakes_data(data, name, counter):
    update_counter(counter, data['qualifiers'])
    return {
        'doc_id': data['meta'][0],
        'source': name,
        'dict_id': int(data['concept_id']),
        'concept': data['concept'],
        'captured': data['captured'],
        'context': data['context'],
        'certainty': data['qualifiers']['certainty'],
        'hypothetical': data['qualifiers']['hypothetical'],
        'historical': data['qualifiers']['historical'],
        'other_subject': data['qualifiers']['other_subject'],
        'start_idx': data['start_index'],
        'end_idx': data['end_index'],
    }


def get_runrex_data(data, name, counter):
    doc_id = data['name']
    algo = data['algorithm']
    cat = data['category']
    counter[f'{cat}_{algo}'] += 1
    counter[cat] += 1
    return {
        'doc_id': doc_id,
        'source': name,
        'algorithm': algo,
        'category': cat,
        'start_idx': data['start'],
        'end_idx': data['end'],
    }


def get_data(version, data, name, counter):
    if version == 'runrex':
        return get_runrex_data(data, name, counter)
    elif version == 'pytakes':
        return get_pytakes_data(data, name, counter)
    else:
        raise ValueError(f'Expected version: pytakes or runrex, got {version}')


def get_pytakes_entry(Entry, data, name, counter):
    """Get database entry for pytakes file"""
    return Entry(**get_pytakes_data(data, name, counter))


def get_runrex_entry(Entry, data, name, counter):
    """Get database entry for runrex file"""
    return Entry(**get_runrex_data(data, name, counter))


def get_entry(version, Entry, data, name, counter):
    if version == 'runrex':
        return get_runrex_entry(Entry, data, name, counter)
    elif version == 'pytakes':
        return get_pytakes_entry(Entry, data, name, counter)
    else:
        raise ValueError(f'Expected version: pytakes or runrex, got {version}')


def get_csv_header(version):
    if version == 'runrex':
        return ['doc_id', 'source', 'algorithm', 'category', 'start_idx', 'end_idx']
    elif version == 'pytakes':
        return ['doc_id', 'source', 'dict_id', 'concept', 'captured',
                'context', 'certainty', 'hypothetical', 'historical',
                'other_subject', 'start_idx', 'end_idx']
    else:
        raise ValueError(f'Expected version: pytakes or runrex, go {version}')


def write_to_file(file: pathlib.Path, version, output_directory=None):
    name = file.name.split('.')[0]
    if not output_directory:
        output_directory = file.parent
    outfile = output_directory / f'{version}_{name}.csv'

    # stats
    doc_ids = set()  # unique document ids
    counter = Counter()

    logger.info(f'Starting extraction of {file} to {outfile}')

    i = 0
    with open(outfile, 'w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=get_csv_header(version))
        writer.writeheader()
        with open(file) as fh:
            for i, line in enumerate(fh, start=1):
                data = json.loads(line)
                row = get_data(version, data, name, counter)
                writer.writerow(row)
                doc_ids.add(row['doc_id'])
                if i % 100 == 0:
                    logger.info(f'Completed upload of {i} lines')
    logger.info(f'Completed upload of {i} lines.')
    output_stats(file, len(doc_ids), counter)
    logger.info('Done')


def output_stats(file, n_docs, counter):
    logger.info(f'Outputting statistics.')
    with open(f'{file}.stat.txt', 'w') as out:
        out.write(f'Unique Documents with a hit:\t{n_docs}\n')
        out.write(f'Other Variables (count):\n')
        for key, value in sorted(counter.items(), reverse=True):
            out.write(f'\t{key}\t{value}\n')


def write_to_database(file: pathlib.Path, version, connection_string):
    """Extract data from jsonl file and upload to database

    :param file: fullpath to input jsonl file
    :param version: pytakes|runrex
    :param connection_string: sqlalchemy-style connection string (see, https://docs.sqlalchemy.org/en/13/core/engines.html)
    :return:
    """
    name = os.path.basename(file).split('.')[0]

    # database
    eng = sa.create_engine(connection_string)
    Entry = create_table(f'{version}_{name}', eng)
    session = sessionmaker(bind=eng)()

    # stats
    doc_ids = set()  # unique document ids
    counter = Counter()

    logger.info(f'Starting upload of {file}')

    i = 0
    with open(file) as fh:
        for i, line in enumerate(fh, start=1):
            data = json.loads(line)
            e = get_entry(version, Entry, data, name, counter)
            doc_ids.add(e.doc_id)
            session.add(e)
            session.commit()
            if i % 100 == 0:
                logger.info(f'Completed upload of {i} lines')
    logger.info(f'Completed upload of {i} lines.')
    output_stats(file, len(doc_ids), counter)
    logger.info('Done')


def main(file: pathlib.Path, version, *, connection_string=None, output_directory=None):
    if connection_string:
        write_to_database(file, version, connection_string)
        if output_directory:
            write_to_file(file, version, output_directory)
    else:
        write_to_file(file, version, output_directory)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(fromfile_prefix_chars='@!')
    parser.add_argument('-i', '--file', required=True, type=pathlib.Path,
                        help='Fullpath to input jsonl file (output of pytakes or runrex).')
    parser.add_argument('-v', '--version', choices=['pytakes', 'runrex'], required=True,
                        help='Specify type of data')
    parser.add_argument('--connection-string', required=False, dest='connection_string',
                        help='SQL Alchemy-style connection string.')
    parser.add_argument('--output-directory', dest='output_directory', required=False, type=pathlib.Path,
                        help='Output directory to place extracted files.')
    args = parser.parse_args()
    main(args.file, args.version,
         connection_string=args.connection_string,
         output_directory=args.output_directory)
