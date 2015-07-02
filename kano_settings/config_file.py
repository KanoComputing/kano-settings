#!/usr/bin/env python

# config_file.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Functions controlling reading and writing to config file
#

import os
import re
import shutil
from kano.utils import ensure_dir, get_user_unsudoed, read_json, write_json, chown_path
from kano.logging import logger
from kano_settings.common import settings_dir
from kano.utils import is_model_2_b

USER = None
USER_ID = None

username = get_user_unsudoed()
if username != 'root':
    if os.path.exists(settings_dir) and os.path.isfile(settings_dir):
        os.rename(settings_dir, settings_dir + '.bak')
    ensure_dir(settings_dir)
    chown_path(settings_dir)
    settings_file = os.path.join(settings_dir, 'settings')

defaults = {
    'pi1': {
        'Keyboard-continent-index': 1,
        'Keyboard-country-index': 21,
        'Keyboard-variant-index': 0,
        'Keyboard-continent-human': 'america',
        'Keyboard-country-human': 'United States',
        'Keyboard-variant-human': 'Generic',
        'Audio': 'Analogue',
        'Wifi': '',
        'Wifi-connection-attempted': False,
        'Overclocking': 'High',
        'Mouse': 'Normal',
        'Font': 'Normal',
        'Wallpaper': 'kanux-background',
        'Parental-level': 0,
        'Locale': 'en_US'
    },
    'pi2': {
        'Keyboard-continent-index': 1,
        'Keyboard-country-index': 21,
        'Keyboard-variant-index': 0,
        'Keyboard-continent-human': 'america',
        'Keyboard-country-human': 'United States',
        'Keyboard-variant-human': 'Generic',
        'Audio': 'Analogue',
        'Wifi': '',
        'Wifi-connection-attempted': False,
        'Overclocking': 'Standard',
        'Mouse': 'Normal',
        'Font': 'Normal',
        'Wallpaper': 'kanux-background',
        'Parental-level': 0,
        'Locale': 'en_US'
    }
}


def file_replace(fname, pat, s_after):
    logger.debug('config_file / file_replace {} "{}" "{}"'.format(fname, pat, s_after))
    if not os.path.exists(fname):
        logger.debug('config_file / file_replace file doesn\'t exists')
        return -1

    # if escape:
        # pat = re.escape(pat)
        # logger.debug('config_file / file_replace replacing pattern, new pattern: "{}"'.format(pat))

    # See if the pattern is even in the file.
    with open(fname) as f:
        if not any(re.search(pat, line) for line in f):
            logger.debug('config_file / file_replace pattern does not occur in file')
            return -1  # pattern does not occur in file so we are done.

    # pattern is in the file, so perform replace operation.
    with open(fname) as f:
        out_fname = fname + ".tmp"
        out = open(out_fname, "w")
        for line in f:
            out.write(re.sub(pat, s_after, line))
        out.close()

        # preserving permissions from the old file
        shutil.copystat(fname, out_fname)

        # overwriting the old file with the new one
        os.rename(out_fname, fname)

    logger.debug('config_file / file_replace file replaced')


def get_pi_key():
    pi2 = is_model_2_b()

    key = "pi1"
    if pi2:
        key = "pi2"

    return key


def get_setting(variable):

    key = get_pi_key()

    try:
        value = read_json(settings_file)[key][variable]
    except Exception:
        if variable not in defaults:
            logger.info('Defaults not found for variable: {}'.format(variable))
        value = defaults[key][variable]
    return value


def set_setting(variable, value):

    key = get_pi_key()

    if username == 'root':
        return

    logger.debug('config_file / set_setting: {} {}'.format(variable, value))

    data = read_json(settings_file)
    if not data:
        data = dict()
        data["pi1"] = dict()
        data["pi2"] = dict()

    data[key][variable] = value
    write_json(settings_file, data)
    chown_path(settings_file)
