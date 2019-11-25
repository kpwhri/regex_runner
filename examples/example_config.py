config = {
    'corpus': {
        'directories': [
            'input',
        ],
    },
    'output': {
        'name': 'results_{datetime}',
        'kind': 'csv',
        'path': 'out'
    },
    'select': {
        'start': 0,
        'end': 22,
    },
    'loginfo': {
        'directory': 'log'
    },
}
print(config)
