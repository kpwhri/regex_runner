from sqlalchemy import MetaData, Table, Column, Integer, String, Text

_COLUMNS = {
    'id': Column('id', Integer, primary_key=True),
    'name': Column('name', String(100)),
    'algorithm': Column('algorithm', String(100)),
    'value': Column('value', Integer),
    'category': Column('category', String(100)),
    'date': Column('date', String(200)),
    'extras': Column('extras', String(200)),
    'matches': Column('matches', Text),
    'text': Column('text', Text),
    'start': Column('start', Integer),
    'end': Column('end', Integer),
}


def create_table(tablename, columns, eng):
    employees = Table(tablename, MetaData(),
                      *(col for col in _COLUMNS if not columns or col in columns))
    employees.create(eng)


def format_data_as_dict(number, doc, algo_name, res):
    d = {
        'id': number,
        'name': doc.name,
        'algorithm': algo_name,
        'value': res.result,
        'category': res.value,
        'date': res.date,
        'extras': res.extras,
        'matches': tuple(m.matchobj.string for m in doc.matches),
        'text': res.text,
        'start': res.start,
        'end': res.end,
    }

    def data_from_columns(columns):
        return {k: v for k, v in d.items() if k in columns}

    return data_from_columns
