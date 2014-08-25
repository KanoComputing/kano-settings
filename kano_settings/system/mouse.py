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


SPEED_SLOW = "1"
SPEED_NORMAL = "default"
SPEED_FAST = "10"


def change_mouse_speed(configuration):
    command = "xset m "
    # Slow configuration
    if configuration == 0:
        command += SPEED_SLOW
    # Modest configuration
    elif configuration == 1:
        command += SPEED_NORMAL
    # Medium configuration
    elif configuration == 2:
        command += SPEED_FAST

    # Apply changes
    os.system(command)
    logger.debug('set_mouse / change_mouse_speed: selected_button:{}'.format(configuration))
