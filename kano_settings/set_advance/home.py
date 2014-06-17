#!/usr/bin/env python
#
# home.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Controls the communication between the advanced mode and parental screen


from gi.repository import Gtk

from . import advance
from . import password
from .parental import get_parental_enabled


in_password = False
win = None
box = None
button = None
parental = None


def activate(_win, _box, _button):
    global box, win, button

    win = _win
    box = _box
    button = _button
    if in_password:
        to_password()
    else:
        to_advance()


def apply_changes(widget):
    if in_password:
        return password.apply_changes(widget)
    else:
        return advance.apply_changes(widget)


def set_in_password(boolean):
    global in_password
    in_password = boolean


def get_in_password():
    return in_password


def create_parental_button():
    global parental

    button = Gtk.CheckButton("Parental lock")
    parental = get_parental_enabled()
    button.set_active(parental)
    button.connect("clicked", to_password)
    return button


def to_advance(arg1=None, arg2=None):
    global win, box, button

    remove_children(box)
    checkbutton = create_parental_button()
    advance.activate(win, box, button, checkbutton)
    set_in_password(False)


def to_password(arg1=None, arg2=None):
    global win, box, button, parental

    remove_children(box)
    password.activate(win, box, button, not get_parental_enabled())
    set_in_password(True)


def remove_children(box):
    for i in box.get_children():
        box.remove(i)

