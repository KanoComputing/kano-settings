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
from kano.utils import ensure_dir, get_user_unsudoed, read_json, write_json, chown_path

USER = None
USER_ID = None

username = get_user_unsudoed()
settings_dir = os.path.join('/home', username, '.kano-settings')
if os.path.exists(settings_dir) and os.path.isfile(settings_dir):
    os.rename(settings_dir, settings_dir + '.bak')
ensure_dir(settings_dir)
chown_path(settings_dir)
settings_file = os.path.join(settings_dir, 'config')

defaults = {
    'Account': '',
    'Keyboard-continent-index': 1,
    'Keyboard-country-index': 21,
    'Keyboard-variant-index': 0,
    'Keyboard-continent-human': 'america',
    'Keyboard-country-human': 'United States',
    'Keyboard-variant-human': 'Generic',
    'Audio': 'Analogue',
    'Wifi': '',
    'Display-mode': 'auto',
    'Display-mode-index': 0,
    'Display-overscan': 0,
    'Overclocking': 'High',
    'Mouse': 'Normal',
    'Wallpaper': 'kanux-background',
    'Proxy-port': '',
    'Proxy-ip': '',
    'Proxy-username': '',
    'Proxy-type': '',
    'Parental-lock': False,
    'Debug-mode': False,
}


def replace(fname, pat, s_after):
    # See if the pattern is even in the file.
    with open(fname) as f:
        pat = re.escape(pat)
        if not any(re.search(pat, line) for line in f):
            return  # pattern does not occur in file so we are done.

    # pattern is in the file, so perform replace operation.
    with open(fname) as f:
        out_fname = fname + ".tmp"
        out = open(out_fname, "w")
        for line in f:
            out.write(re.sub(pat, s_after, line))
        out.close()
        os.rename(out_fname, fname)


def get_setting(variable):
    try:
        value = read_json(settings_file)[variable]
        # print 'getting {} from json'.format(variable)
    except Exception:
        if variable not in defaults:
            print 'Defaults not found for variable: {}'.format(variable)
        value = defaults[variable]
        # print 'getting {} from defaults'.format(variable)
    return value


def set_setting(variable, value):
    data = read_json(settings_file)
    if not data:
        data = dict()
    data[variable] = value
    write_json(settings_file, data)
    chown_path(settings_file)
    # print 'setting {} to {}'.format(variable, value)



