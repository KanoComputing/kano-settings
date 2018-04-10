#
# misc.py
#
# Copyright (C) 2014 - 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Miscellaneous functions
#

import os

from gi import require_version
require_version('Gtk', '3.0')

from gi.repository import Gtk, GdkPixbuf

from kano.paths import common_images_dir


def tick_icon():
    '''This should return a tick image.  We use this to show which
    WiFi network is already selected
    '''

    width = 24
    height = 24

    icons_path = os.path.join(common_images_dir, 'icons.png')

    tick_pixbuf = GdkPixbuf.Pixbuf.new_from_file(icons_path)

    tick_pixbuf = tick_pixbuf.new_subpixbuf(5 * 24, 0, width, height)
    tick_image = Gtk.Image()
    tick_image.set_from_pixbuf(tick_pixbuf)

    return tick_image
