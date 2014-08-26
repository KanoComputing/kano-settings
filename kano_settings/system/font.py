#!/usr/bin/env python

# font.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Backend font functions
#


import os
from kano_settings.config_file import file_replace
from kano.utils import get_user_unsudoed
from kano.logging import logger

SIZE_SMALL = 10
SIZE_NORMAL = 14
SIZE_BIG = 18

username = get_user_unsudoed()
config_file = os.path.join('/home', username, '.config/lxsession/LXDE/desktop.conf')


# int configuration: 0 = small, 1 = normal, 2 = big
def change_font_size(configuration):

    font = "sGtk/FontName=Bariol "
    font_pattern = font + "[0-9][0-9]"

    # Small configuration
    if configuration == 0:
        font += str(SIZE_SMALL)
    # Normal configuration
    elif configuration == 1:
        font += str(SIZE_NORMAL)
    # Big configurations
    elif configuration == 2:
        font += str(SIZE_BIG)

    # Apply changes
    file_replace(config_file, font_pattern, font)
    # Reload lxsession
    os.system("lxsession -r")
    logger.debug('set_font / change_font_size: selected_button:{}'.format(configuration))
