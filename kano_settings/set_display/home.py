#!/usr/bin/env python

# home.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the interaction between wifi and proxy setting screens

import kano_settings.set_display.set_display as set_display
import kano_settings.set_display.set_overscan as set_overscan
from kano.gtk3.buttons import KanoButton, OrangeButton


win = None
box = None
button = None
to_display_button = None
to_overscan_button = None


def activate(_win, _box, _button):
    global win, box, button, to_display_button, to_overscan_button

    win = _win
    box = _box
    button = _button

    to_display_button = generate_display_button()
    to_overscan_button = generate_overscan_button()
    set_display.activate(win, box, button, to_overscan_button)


# This button in the proxy setting screen that takes you to the wifi screen
def generate_display_button():
    to_display_button = KanoButton("APPLY CHANGES")
    to_display_button.pack_and_align()
    to_display_button.connect("button_press_event", to_display)
    return to_display_button


# This is the orange button we see in the wifi settings that takes you to the proxy settings
def generate_overscan_button():
    global win

    to_overscan_button = OrangeButton()
    to_overscan_button.connect("button_press_event", to_overscan)
    return to_overscan_button


def to_display(arg1=None, arg2=None):

    set_overscan.apply_changes(None)
    to_overscan_button = generate_overscan_button()
    remove_children(box)
    set_display.activate(win, box, button, to_overscan_button)
    win.show_all()


def to_overscan(event=None, arg=None):
    global win, box, button

    to_display_button = generate_display_button()
    remove_children(box)
    set_overscan.activate(win, box, to_display_button)
    win.show_all()


def remove_children(box):
    for i in box.get_children():
        box.remove(i)


def apply_changes(event=None, button=None):
    set_display.apply_changes(button)
    return
