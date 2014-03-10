#!/usr/bin/env python3

# config_file.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import re


USER = os.environ['LOGNAME']
settings_path = "/home/%s/.kano-settings" % (USER)

def init():
    # Update .kano-settings with new current_country and current_variant   
    try:
        f = open(path, 'r+')
        f.write('finished:0\n')
        f.close()

    except:
        # Fail silently
        return 


def file_replace(fname, pat, s_after):

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


def write_to_file(setting_name, setting, path=settings_path):

    # Update .kano-settings with new current_country and current_variant   
    try:
        f = open(path, 'r+')
        file_content = str(f.read())
        f.close()

        file_index = file_content.index(setting_name + ':')
        file_index3 = file_content[file_index:].index('\n') # Get selected variant of that country
        old_string = file_content[file_index: file_index3]

        new_string = setting_name + ':' + setting

        config_file.file_replace(path, old_string, new_string)

    except:
        # Fail silently
        return 

def read_from_file(setting_name, path=settings_path):

    # Update .kano-settings with new current_country and current_variant   
    try:
        f = open(path, 'r')
        file_content = str(f.read())
        f.close()

        file_index = file_content.index(setting_name + ':')
        file_index3 = file_content[file_index:].index('\n') # Get selected variant of that country
        setting = file_content[file_index + len(setting_name + ':'): file_index3]
        return setting

    except:
        # Fail silently
        write_to_file(setting_name, '0')
        return 

"""def read_from_file(setting_name):
    # Set up in file in .kano-settings  
    try:
        f = open(settings_path, 'r+')
        # Format, "keyboard:country,second_choice"
        file_content = str(f.read())
        file_index = file_content.index(setting_name + ':') + len(setting_name + ":")
        file_index2 = file_content[file_index:].index(',') # Return first comma after Keyboard
        file_index3 = file_content[file_index:].index('\n') # Get selected variant of that country
        country_substring = file_content[file_index: file_index + file_index2]
        variant_substring = file_content[file_index + file_index2 + 1: file_index + file_index3]
        country_combo.set_active(int(country_substring))
        variants_combo.set_active(int(variant_substring))

    except:
        f = open(settings_path, "w+")
        usa_index = countries.index('USA')
        country_combo.set_active(usa_index)
        variants_combo.set_active(0)
        f.write("Keyboard:" + str(usa_index) + "," + str(0) + "\n")
        
    f.close()"""