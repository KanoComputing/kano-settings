#!/usr/bin/env python3

# config_file.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
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
        file_index3 = file_content[file_index:].index('\n') # Get selected variant of that country
        old_string = file_content[file_index: file_index3 + file_index]
        new_string = setting_name + ':' + setting
        replace(path, old_string, new_string)
        print("Successfully completed replace_setting")
        return 0

    except:
        # Failure is probably down to the setting not existing 
        print("FAIL: replace_settings")
        #f.close()
        write_to_file(setting_name, setting)
        return 



def write_to_file(setting_name, setting):

    USER = os.environ.get('SUDO_USER')
    #USER_ID = getpwnam(USER).pw_uid
    path = "/home/%s/.kano-settings" % (USER)

    setting = str(setting)

    # Update .kano-settings with new current_country and current_variant   
    try:
        f = open(path, "a+")
        new_string = setting_name + ":" + setting + "\n"
        f.write(new_string)
        f.close()
        return

    except:
        print("FAIL: write_to_file")
        #f.close()
        return 

def read_from_file(setting_name):

    USER = os.environ.get('SUDO_USER')
    #USER_ID = getpwnam(USER).pw_uid
    path = "/home/%s/.kano-settings" % (USER)

    try:
        f = open(path, 'r')
        file_content = str(f.read())
        f.close()
        file_index = file_content.index(setting_name + ':')

        file_index2 = file_content[file_index:].index('\n')
        # file_index2 is the distance from file_index, so you have to add them to find total distance
        # file_index does not take into account the length of the setting name
        setting = file_content[file_index + len(setting_name) + 1: file_index2 + file_index]
        f.close()
        return setting

    except:
        print("FAIL: read_from_file")
        #set_defaults(setting_name) #change to custom defaults
        return 

custom_info = ["Email", "Keyboard-country-human", "Audio", "Wifi", "Display"]

def set_defaults(setting_name):

    if setting_name == "Email":
        setting_prop = ""
    elif setting_name == "Keyboard-country":
        setting_prop = str(108)
    elif setting_name == "Keyboard-variant":
        setting_prop = str(0)
    elif setting_name == "Keyboard-country-human":
        setting_prop = "USA"
    elif setting_name == "Keyboard-variant-human":
        setting_prop = "Generic"
    elif setting_name == "Audio":
        setting_prop = "Analogue"
    elif setting_name == "Wifi":
        setting_prop = ""
    elif setting_name == "Display":
        setting_prop = "Auto"
    elif setting_name == "Completed":
        setting_prop = "0"

    write_to_file(setting_name, setting_prop)