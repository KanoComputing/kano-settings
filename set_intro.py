#!/usr/bin/env python3

# set_intro.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk


def activate(_win, table, box):

    label = Gtk.Label()
    label.set_text("Hi! This is some kind of introductory text!")
    label.set_justify(Gtk.Justification.LEFT)
    box.pack_start(label, True, True, 0)
