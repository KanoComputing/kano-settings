#!/usr/bin/env python

# home.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the interaction between wifi and proxy setting screens

from gi.repository import Gtk
import kano_settings.set_wifi.proxy as set_proxy
import kano_settings.set_wifi.wifi as set_wifi
import kano_settings.constants as constants
import kano_settings.components.cursor as cursor
from kano.gtk3.green_button import GreenButton


win = None
box = None
update = None
to_wifi_button = None
to_proxy_button = None
disable_proxy = None
in_proxy = False


def activate(_win, _box, _update):
    global win, box, update, to_proxy_button, to_wifi_button

    win = _win
    box = _box
    update = _update

    to_proxy_button = generate_proxy_button()
    to_wifi_button = generate_wifi_button()
    disable_proxy = generate_disable_proxy()
    constants.proxy_enabled = set_proxy.is_enabled()
    set_wifi.activate(win, box, update, to_proxy_button, disable_proxy)


# This button in the proxy setting screen that takes you to the wifi screen
def generate_wifi_button():
    to_wifi_button = GreenButton("APPLY CHANGES")
    to_wifi_button.pack_and_align()
    to_wifi_button.connect("button_press_event", to_wifi_apply_changes)
    return to_wifi_button


# This is the orange button we see in the wifi settings that takes you to the proxy settings
def generate_proxy_button():
    global win

    to_proxy_button = Gtk.Button()
    to_proxy_button.get_style_context().add_class("orange_button")
    # The bulk of this function has moved to wifi.py
    cursor.attach_cursor_events(to_proxy_button)
    to_proxy_button.connect("button_press_event", to_proxy)
    return to_proxy_button


# This is the orange button in the wifi setting screen that disables the proxy settings
def generate_disable_proxy():
    disable_proxy_button = Gtk.Button("Disable proxy")
    disable_proxy_button.get_style_context().add_class("orange_button")
    disable_proxy_button.connect("button_press_event", disable_proxy_function)
    return disable_proxy_button


# Reached when orange disable proxy button is clicked
def disable_proxy_function(arg1=None, arg2=None):

    set_proxy.set_sensitive(False)
    # Go to set_wifi without calling set_proxy.apply_changes()
    to_wifi()
    constants.proxy_enabled = set_proxy.is_enabled()


def to_wifi_apply_changes(event=None, arg=None):
    global win, box, update, to_proxy_button

    # Apply changes from set_proxy
    set_proxy.apply_changes()
    to_wifi()


def to_wifi(arg1=None, arg2=None):
    global in_proxy

    to_proxy_button = generate_proxy_button()
    disable_proxy = generate_disable_proxy()
    remove_children(box)
    set_wifi.activate(win, box, update, to_proxy_button, disable_proxy)
    in_proxy = False
    win.show_all()


def to_proxy(event=None, arg=None):
    global win, box, update, in_proxy

    to_wifi_button = generate_wifi_button()
    remove_children(box)
    set_proxy.activate(win, box, update, to_wifi_button)
    in_proxy = True
    win.show_all()


def remove_children(box):
    for i in box.get_children():
        box.remove(i)


def apply_changes(event=None, button=None):
    set_wifi.apply_changes()
