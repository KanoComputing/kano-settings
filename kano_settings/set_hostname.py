#!/usr/bin/env python

# set_hostname.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License:   http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Set the hostname in /etc/hosts and /etc/hostname
# 

import os
import sys
import re
from kano.logging import logger
import kano.utils
from kano_settings.get_username import get_first_username


def set_hostname_postinst():
    # when running as post install, get the existing first user and set as host name
    new_hostname = get_first_username()

    if new_hostname is None:
        logger.warning("No first user")
    else:
        set_hostname(new_hostname)


def set_hostname(new_hostname):
    if os.environ['LOGNAME'] != 'root':
        logger.error("Error: Settings must be executed with root privileges")


    # Check username chars

    new_hostname = re.sub('[^a-zA-Z0-9]', '', new_hostname).lower()

    if new_hostname == '':
        logger.error('no letters left in username after removing illegal ones')

    # check if already done
    curr_hosts = kano.utils.read_file_contents_as_lines('/etc/hosts')
    if '127.0.0.1\tkano' not in curr_hosts:
        logger.warn('/etc/hosts already modified, not changing')

    try:
        lines_changed = kano.utils.sed(
                                      '127.0.0.1\s+(kano)',
                                      '127.0.0.1\t{}'.format(new_hostname),
                                      '/etc/hosts',
                                      True)
        if lines_changed != 1:
            logger.error("failed to change /etc/hosts")
    except:
        logger.error("exception while changing change /etc/hosts")

    try:
        kano.utils.write_file_contents('/etc/hostname', new_hostname+'\n')
    except:
        logger.error("exception while changing change /etc/hostname")


