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
from kano.utils import ensure_dir

USER = None
USER_ID = None

username = os.environ['SUDO_USER']
settings_dir = os.path.join('/home', username, '.kano-settings')
if os.path.exists(settings_dir) and os.path.isfile(settings_dir):
    os.rename(settings_dir, settings_dir + '.bak')
ensure_dir(settings_dir)
settings_file = os.path.join(settings_dir, 'config')


def init():
    # Update .kano-settings with new current_country and current_variant
    try:
        f = open(settings_file, 'r+')
        f.write('finished:0\n')
        f.close()

    except:
        # Fail silently
        return


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


# Returns true if the old setting is the same as the new one
def compare(setting_name, setting):

    setting = str(setting)
    old_setting = read_from_file(setting_name)
    return setting == old_setting


def replace_setting(setting_name, setting):
    setting = str(setting)
    # Update .kano-settings with new current_country and current_variant
    try:
        f = open(settings_file, 'r')
        file_content = str(f.read())
        f.close()
        file_index = file_content.index(setting_name + ':')
        # Get selected variant of that country
        file_index3 = file_content[file_index:].index('\n')
        old_string = file_content[file_index: file_index3 + file_index]
        new_string = setting_name + ':' + setting
        replace(settings_file, old_string, new_string)
        return 0

    except Exception:
        # Failure is probably down to the setting not existing
        write_to_file(setting_name, setting)
        return


def write_to_file(setting_name, setting):
    setting = str(setting)

    # Update .kano-settings with new current_country and current_variant
    try:
        f = open(settings_file, "a+")
        new_string = setting_name + ":" + setting + "\n"
        f.write(new_string)
        f.close()
        return

    except Exception:
        return


def read_from_file(setting_name):
    try:
        f = open(settings_file, 'r')
        file_content = str(f.read())
        f.close()
        index1 = file_content.index(setting_name + ':')

        index2 = file_content[index1:].index('\n')
        # file_index2 is the distance from file_index
        # You have to add them to find total distance
        # file_index does not take into account the length of the setting name
        setting = file_content[index1 + len(setting_name) + 1: index2 + index1]
        f.close()
        return setting

    except Exception:
        # change to custom defaults
        setting_prop = set_defaults(setting_name)
        return setting_prop


def set_defaults(setting_name):

    setting_prop = ""

    if setting_name == "Email":
        setting_prop = ""
    elif setting_name == "Keyboard-continent-index":
        setting_prop = str(1)
    elif setting_name == "Keyboard-country-index":
        setting_prop = str(21)
    elif setting_name == "Keyboard-variant-index":
        setting_prop = str(0)
    elif setting_name == "Keyboard-continent-human":
        setting_prop = "america"
    elif setting_name == "Keyboard-country-human":
        setting_prop = "United States"
    elif setting_name == "Keyboard-variant-human":
        setting_prop = "Generic"
    elif setting_name == "Audio":
        setting_prop = "Analogue"
    elif setting_name == "Wifi":
        setting_prop = ""
    elif setting_name == "Display-mode":
        setting_prop = "auto"
    elif setting_name == "Display-mode-index":
        setting_prop = "0"
    elif setting_name == "Display-overscan":
        setting_prop = "0"
    elif setting_name == "Overclocking":
        setting_prop = "High"
    elif setting_name == "Mouse":
        setting_prop = "Normal"
    elif setting_name == "Wallpaper":
        setting_prop = "kanux-background"
    else:
        setting_prop = ""

    write_to_file(setting_name, setting_prop)

    return setting_prop
