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

USER = None
USER_ID = None


def init():
    USER = os.environ['SUDO_USER']
    #USER_ID = getpwnam(USER).pw_uid
    path = "/home/%s/.kano-settings" % (USER)
    # Update .kano-settings with new current_country and current_variant
    try:
        f = open(path, 'r+')
        f.write('finished:0\n')
        f.close()

    except:
        # Fail silently
        return


def replace(fname, pat, s_after):

    # See if the pattern is even in the file.
    with open(fname) as f:
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


def replace_setting(setting_name, setting):

    USER = os.environ['SUDO_USER']
    #USER_ID = getpwnam(USER).pw_uid
    path = "/home/%s/.kano-settings" % (USER)

    setting = str(setting)
    # Update .kano-settings with new current_country and current_variant
    try:
        f = open(path, 'r')
        file_content = str(f.read())
        f.close()
        file_index = file_content.index(setting_name + ':')
        # Get selected variant of that country
        file_index3 = file_content[file_index:].index('\n')
        old_string = file_content[file_index: file_index3 + file_index]
        new_string = setting_name + ':' + setting
        replace(path, old_string, new_string)
        print("SUCCESS: completed replace_setting")
        return 0

    except Exception as e:
        # Failure is probably down to the setting not existing
        print("FAIL: replace_setting")
        print(e)
        #f.close()
        write_to_file(setting_name, setting)
        return


def write_to_file(setting_name, setting):

    USER = os.environ.get('SUDO_USER')
    path = "/home/%s/.kano-settings" % (USER)

    setting = str(setting)

    # Update .kano-settings with new current_country and current_variant
    try:
        f = open(path, "a+")
        new_string = setting_name + ":" + setting + "\n"
        f.write(new_string)
        f.close()
        print("SUCCESS: write_to_file completed")
        return

    except Exception as e:
        print("FAIL: write_to_file")
        print(e)
        return


def read_from_file(setting_name):

    USER = os.environ.get('SUDO_USER')
    path = "/home/%s/.kano-settings" % (USER)

    try:
        f = open(path, 'r')
        file_content = str(f.read())
        f.close()
        index1 = file_content.index(setting_name + ':')

        index2 = file_content[index1:].index('\n')
        # file_index2 is the distance from file_index
        # You have to add them to find total distance
        # file_index does not take into account the length of the setting name
        setting = file_content[index1 + len(setting_name) + 1: index2 + index1]
        f.close()
        print("SUCCESS: completed read_from_file")
        return setting

    except Exception as e:
        print("FAIL: read_from_file")
        print(e)
        # change to custom defaults
        setting_prop = set_defaults(setting_name)
        return setting_prop


def set_defaults(setting_name):

    setting_prop = ""

    if setting_name == "Email":
        setting_prop = "?"
    elif setting_name == "Keyboard-continent-index":
        setting_prop = str(1)
    elif setting_name == "Keyboard-country-index":
        setting_prop = str(21)
    elif setting_name == "Keyboard-variant-index":
        setting_prop = str(0)
    elif setting_name == "Keyboard-continent-human":
        setting_prop = "America"
    elif setting_name == "Keyboard-country-human":
        setting_prop = "USA"
    elif setting_name == "Keyboard-variant-human":
        setting_prop = "Generic"
    elif setting_name == "Audio":
        setting_prop = "Analogue"
    elif setting_name == "Wifi":
        setting_prop = "?"
    elif setting_name == "Display":
        setting_prop = "Auto"
    elif setting_name == "Completed":
        setting_prop = "0"

    write_to_file(setting_name, setting_prop)

    return setting_prop
