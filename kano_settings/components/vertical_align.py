#!/usr/bin/env python

# set_audio.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk


class VerticalAlign():
    def __init__(self):

        # Create alignment container
        self.container = Gtk.Alignment(xalign=0.5, yalign=1, xscale=0, yscale=0)

        self.container.set_padding(50, 0, 0, 0)
