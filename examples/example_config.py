config = {
    'corpus': {
        'directories': [
            'input',  # input directory
        ],
    },
    'output': {  # output file
        'name': 'results_{datetime}',  # 'datetime' will be auto-filled
        'kind': 'csv',  # output type
        'path': 'out'  # output directory
    },
    'select': {
        'start': 0,
        'end': 22,
    },
    'loginfo': {
        'directory': 'log'
    },
}
print(config)  # required to load config
