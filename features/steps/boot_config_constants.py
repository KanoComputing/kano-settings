RESOLUTIONS = {
    '1280x800': {
        'group': 'dmt',
        'mode': '28'
    },
    '1600x1200': {
        'group': 'dmt',
        'mode': 51
    },
    '1920x1080': {
        'group': 'cea',
        'mode': 16
    },
}

SCREENS = {
    'screen-kit': RESOLUTIONS['1280x800'],
    '1080p': RESOLUTIONS['1920x1080'],
    '4-3': RESOLUTIONS['1600x1200'],
}


BASE_CONFIG_FILE_PATH = 'base_config.txt'
import os
print os.path.exists(BASE_CONFIG_FILE_PATH)
print __dirname__
with open(BASE_CONFIG_FILE_PATH, 'r') as f:
    BASE_CONFIG_FILE = f.read()

print BASE_CONFIG_FILE
