#!/usr/bin/env python

# mouse.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Backend mouse functions
#


import os
from kano.logging import logger


SPEEDS = ['1', 'default', '10']


def change_mouse_speed(configuration):
    try:
        speed = SPEEDS[configuration]
    except IndexError:
        return

    command = "xset m {}".format(speed)

    # Apply changes
    os.system(command)
    logger.debug('set_mouse / change_mouse_speed: selected_button:{}'.format(configuration))
