#!/usr/bin/env python

# boot_config.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Functions controlling reading and writing to config file
#

import re
from kano.utils import read_file_contents_as_lines

boot_config_path = "/boot/config.txt"


# if the value argument is None, the option will be commented out
def set_config_option(name, value=None):
    lines = read_file_contents_as_lines(boot_config_path)
    if not lines:
        return

    option_re = r'^\s*#?\s*' + str(name) + r'=(.*)'

    with open(boot_config_path, "w") as boot_config_file:
        was_found = False

        for line in lines:
            if re.match(option_re, line):
                was_found = True
                if value is not None:
                    replace_str = str(name) + "=" + str(value)
                else:
                    replace_str = r'#' + str(name) + r'=\1'
                new_line = replace_str
            else:
                new_line = line

            boot_config_file.write(new_line + "\n")

        if not was_found and value is not None:
            boot_config_file.write(str(name) + "=" + str(value) + "\n")
