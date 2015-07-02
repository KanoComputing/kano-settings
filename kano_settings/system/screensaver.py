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
from kano_settings.config_file import username

# These are where we write the user settings
kdesk_config = os.path.join("/home", username, ".kdeskrc")

# This is where the default kdesk settings are kept
usr_kdesk_config = "/usr/share/kano-desktop/kdesk/.kdeskrc"

error_msg = "Could not find in home kdesk"


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
    f = open(kdesk_config, 'a+')

    # Check if we find the parameter in the file. If not, we need to
    # add it manually
    found = False

    # This is the line we want to insert into the kdesk config
    config_line = '{}: {}'.format(param_name, param_value)

    for line in f:
        if param_name in line:
            line = line.strip()

            line = line.replace('/', '\/')
            config_line = config_line.replace('/', '\/')

            # Replace the line in the original config with the newline in the
            # copy
            sed_cmd = 'sed -i \'s/{}/{}/g\' {}'.format(
                line, config_line, kdesk_config
            )
            logger.info('Applied the sed cmd: {}'.format(sed_cmd))
            os.system(sed_cmd)

            found = True

    if not found:
        f.write(config_line + "\n")

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
    # Create /home/user/.kdeskrc if it doesn't exist
    if not os.path.exists(kdesk_config):
        open(kdesk_config, "w+").close()

    param = check_file_for_parameter(kdesk_config, param_name)

    # If the home config file does not contain the parameter, check the
    # default.
    if param == error_msg:
        param = check_file_for_parameter(usr_kdesk_config, param_name)

    return param


def check_file_for_parameter(filepath, param_name):
    '''Check the specific file for the parameter.
    This is because we may have to check two files for
    the value of a parameter
    '''

    f = open(filepath, 'r')
    for line in f:
        if param_name in line:
            param_value = line.split(':')[1].strip()
            f.close()
            return param_value

    f.close()

    # If we cannot find a parameter, return a message.
    # The parameter in the config could be None or 0, so we need a
    # clear return value to show it's not in /home/user/.kdeskrc
    return error_msg
