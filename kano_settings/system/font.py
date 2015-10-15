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


SIZES = [10, 14, 18]


username = get_user_unsudoed()
config_file = os.path.join('/home', username, '.config/lxsession/LXDE/desktop.conf')


# int configuration: 0 = small, 1 = normal, 2 = big
def change_font_size(configuration):
    try:
        size = SIZES[configuration]
    except IndexError:
        return

    font = "sGtk/FontName=Bariol {}"
    pattern = font.format("[0-9]+")
    replace = font.format(size)

    # Apply changes: For jessie, this is automatically reloaded by lxsession 
    file_replace(config_file, pattern, replace)

    logger.debug('set_font / change_font_size: selected_button:{}'.format(configuration))
