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
from runrex.cli.extract_and_load_json import extract_and_load_json_from_cli


def main():
    extract_and_load_json_from_cli()


if __name__ == '__main__':
    main()
