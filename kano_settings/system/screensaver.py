#!/usr/bin/env python

# screensaver.py
#
# Copyright (C) 2014-2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Contains the screensaver backend functions

import os
from kano.logging import logger
from kano_settings import common

# These are the values we want to change the filepaths to
kdesk_config = '/usr/share/kano-desktop/kdesk/.kdeskrc'


def is_screensaver_on():
    '''Get whether the screensaver is currently switched on
    If the ScreenSaverTimeout parameter is set to 0, it is switched off
    '''
    timeout = int(get_kdesk_config('ScreenSaverTimeout').strip())
    return (timeout > 0)


def set_screensaver_timeout(timeout):
    '''Alternative to setting the screensaver timeout
    '''
    set_kdesk_config('ScreenSaverTimeout', timeout)


def get_screensaver_timeout():
    return get_kdesk_config('ScreenSaverTimeout')


def set_screensaver_program(program):
    '''Takes a string of the filepath to the program
    '''
    set_kdesk_config('ScreenSaverProgram', program)


def get_screensaver_program():
    return get_kdesk_config('ScreenSaverProgram')


def set_kdesk_config(param_name, param_value):
    '''Given a param name and a param value, will set the .kdeskrc file
    accordingly
    '''
    USER = os.environ['SUDO_USER']

    f = open(kdesk_config, 'r')

    for line in f:
        if param_name in line:
            line = line.strip()
            newline = '{}: {}'.format(param_name, param_value)
            line = line.replace('/', '\/')
            newline = newline.replace('/', '\/')

            # Replace the line in the original config with the newline in the
            # copy
            sed_cmd = 'sed -i \'s/{}/{}/g\' {}'.format(
                line, newline, kdesk_config
            )
            logger.info('Applied the sed cmd: {}'.format(sed_cmd))
            os.system(sed_cmd)

            logger.info('Refresh kdesk')
            cmd = 'sudo -u {user} kdesk -w'.format(user=USER)
            os.system(cmd)

            # For now, refreshing kdesk does not update the screensaver
            # settings, so prompt the user for a reboot
            common.need_reboot = True

    f.close()


def get_kdesk_config(param_name):
    '''For a particular parameter, get the config value
    This will always return a string.

    Parameter names of interest:

    ScreenSaverTimeout.  This is the length of time the screensaver is
    left on if it is set 0, it switches the screensaver off

    ScreenSaverProgram: the path to the program to be started as the
    screensaver
    '''

    f = open(kdesk_config, 'r')

    for line in f:
        if param_name in line:
            param_value = line.split(':')[1].strip()
            return param_value

    f.close()
