#!/usr/bin/env python

# cursor.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Functions that changes the cursor's appearence
#

from gi.repository import Gdk


# win is passed through as an argument
def hand_cursor(button, event, win):
    # Change the cursor to hour Glass
    cursor = Gdk.Cursor.new(Gdk.CursorType.HAND1)
    win.get_root_window().set_cursor(cursor)


def arrow_cursor(button, event, win):
    # Set the cursor to normal Arrow
    cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
    win.get_root_window().set_cursor(cursor)
