#!/usr/bin/env python

# boot_config.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Functions controlling reading and writing to /boot/confit.txt
#

import re
from kano.utils import read_file_contents_as_lines, is_number
from kano.logging import logger

boot_config_path = "/boot/config.txt"


# if the value argument is None, the option will be commented out
def set_config_value(name, value=None):
    lines = read_file_contents_as_lines(boot_config_path)
    if not lines:
        return

    logger.info('writing value to /boot/config.txt {} {}'.format(name, value))

    option_re = r'^\s*#?\s*' + str(name) + r'=(.*)'

    with open(boot_config_path, "w") as boot_config_file:
        was_found = False

        for line in lines:
            if re.match(option_re, line):
                was_found = True
                if value is not None:
                    replace_str = str(name) + "=" + str(value)
                else:
                    replace_str = r'#' + str(name) + r'=0'
                new_line = replace_str
            else:
                new_line = line

            boot_config_file.write(new_line + "\n")

        if not was_found and value is not None:
            boot_config_file.write(str(name) + "=" + str(value) + "\n")


def get_config_value(name):
    lines = read_file_contents_as_lines(boot_config_path)
    if not lines:
        return 0

    for l in lines:
        if l.startswith(name + '='):
            value = l.split('=')[1]
            if is_number(value):
                value = int(value)
            return value

    return 0


def set_config_comment(name, value):
    lines = read_file_contents_as_lines(boot_config_path)
    if not lines:
        return

    logger.info('writing comment to /boot/config.txt {} {}'.format(name, value))

    comment_str_full = '### {}: {}'.format(name, value)
    comment_str_name = '### {}'.format(name)

    with open(boot_config_path, "w") as boot_config_file:
        boot_config_file.write(comment_str_full + '\n')

        for line in lines:
            if comment_str_name in line:
                continue

            boot_config_file.write(line + '\n')


def get_config_comment(name, value):
    lines = read_file_contents_as_lines(boot_config_path)
    if not lines:
        return

    comment_str_full = '### {}: {}'.format(name, value)
    return comment_str_full in lines
