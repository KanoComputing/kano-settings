#!/usr/bin/env python3

# config_file.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import re


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


def write_to_file(setting_name, setting):

    # Update .kano-settings with new current_country and current_variant   
    try:
        f = open(settings_path, 'r+')
        file_content = str(f.read())
        f.close()

        file_index = file_content.index(setting_name + ':')
        file_index3 = file_content[file_index:].index('\n') # Get selected variant of that country
        old_string = file_content[file_index: file_index3]

        #selected_country_index = country_combo.get_active()
        #selected_variants_index = variants_combo.get_active()
        new_string = setting_name + ':' + setting + '\n'

        config_file.file_replace(settings_path, old_string, new_string)

    except:
        # Fail silently
        return 

def read_from_file(setting_name):
    # Set up in file in .kano-settings  
    try:
        f = open(settings_path, 'r+')
        # Format, "keyboard:country,second_choice"
        file_content = str(f.read())
        file_index = file_content.index(setting_name + ':') + len(setting_name + ":")
        file_index2 = file_content[file_index:].index('\n') # Get selected variant of that country
        setting = file_content[file_index : file_index2]
        print("setting =  " + setting)
        f.close()
        return setting
        #country_substring = file_content[file_index: file_index + file_index2]
        #variant_substring = file_content[file_index + file_index2 + 1: file_index + file_index3]
        #country_combo.set_active(int(country_substring))
        #variants_combo.set_active(int(variant_substring))

    except:
        print("Failed")
        write_to_file(setting_name, '0')
        #f = open(settings_path, "w+")
        #usa_index = countries.index('USA')
        #country_combo.set_active(usa_index)
        #variants_combo.set_active(0)
        #f.write("Keyboard:" + str(usa_index) + "," + str(0) + "\n")
        
    