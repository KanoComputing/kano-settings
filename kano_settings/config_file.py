#!/usr/bin/env python

# config_file.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Functions controlling reading and writing to config file
#

import os
import re
import shutil

from kano.logging import logger
from kano.utils.user import get_user_unsudoed
from kano.utils.file_operations import ensure_dir, read_json, write_json, \
    chown_path

from kano_settings.common import settings_dir
from kano_settings.system.boards import get_board_props

USER = None
USER_ID = None

username = get_user_unsudoed()
if username != 'root':
    if os.path.exists(settings_dir) and os.path.isfile(settings_dir):
        os.rename(settings_dir, settings_dir + '.bak')
    ensure_dir(settings_dir)
    chown_path(settings_dir)
    settings_file = os.path.join(settings_dir, 'settings')

def merge_dicts(base, override):
    for key, value in override.iteritems():
        base[key] = value

    return base

DEFAULT_CONFIG = {
    'Keyboard-continent-index': 1,
    'Keyboard-country-index': 21,
    'Keyboard-variant-index': 0,
    'Keyboard-continent-human': _("america"),
    'Keyboard-country-human': _("United States"),
    'Keyboard-variant-human': _("Generic"),
    'Audio': _("Analogue"),
    'Wifi': '',
    'Wifi-connection-attempted': False,
    'Mouse': _("Normal"),
    'Font': _("Normal"),
    'Wallpaper': 'kanux-background',
    'Parental-level': 0,
    'Locale': 'en_US',
    'LED-Speaker-anim': True,
    'Use_GLX': False
}

DEFAULTS = merge_dicts(DEFAULT_CONFIG, get_board_props().DEFAULT_CONFIG)


def file_replace(fname, pat, s_after):
    logger.debug("config_file / file_replace {} \"{}\" \"{}\"".format(fname, pat, s_after))
    if not os.path.exists(fname):
        logger.debug("config_file / file_replace file doesn't exists")
        return -1

    # if escape:
        # pat = re.escape(pat)
        # logger.debug('config_file / file_replace replacing pattern, new pattern: "{}"'.format(pat))

    # See if the pattern is even in the file.
    with open(fname) as f:
        if not any(re.search(pat, line) for line in f):
            logger.debug("config_file / file_replace pattern does not occur in file")
            return -1  # pattern does not occur in file so we are done.

    # pattern is in the file, so perform replace operation.
    with open(fname) as f:
        out_fname = fname + ".tmp"
        out = open(out_fname, 'w')
        for line in f:
            out.write(re.sub(pat, s_after, line))
        out.close()

        # preserving permissions from the old file
        shutil.copystat(fname, out_fname)

        # overwriting the old file with the new one
        os.rename(out_fname, fname)

    logger.debug("config_file / file_replace file replaced")


def get_setting(variable):

    try:
        value = read_json(settings_file)[variable]
    except Exception:
        if variable not in DEFAULTS:
            logger.info("Defaults not found for variable: {}".format(variable))
        value = DEFAULTS[variable]
    return value


def set_setting(variable, value):

    if username == 'root':
        return

    logger.debug("config_file / set_setting: {} {}".format(variable, value.encode('utf-8'))

    data = read_json(settings_file)
    if not data:
        data = dict()

    data[variable] = value
    write_json(settings_file, data)
    chown_path(settings_file)
