#!/usr/bin/env python3

# set_template.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk


def activate(_win, table, title_container, apply_changes):

    table.attach(title_container, 0, 0, 1, 1)
    table.attach(apply_changes, 0, 3, 1, 1)