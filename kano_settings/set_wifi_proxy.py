#!/usr/bin/env python

# wifi_proxy_commenuicaton.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Pango
import kano_settings.set_proxy as set_proxy
import kano_settings.set_wifi as set_wifi

win = None
box = None
update = None
#to_wifi_button = None
#to_proxy_button = None


def activate(_win, _box, _update):
    global win, box, update, to_proxy_button, to_wifi_button

    win = _win
    box = _box
    update = _update

    to_proxy_button = generate_proxy_button()
    to_wifi_button = generate_wifi_button()

    set_wifi.activate(win, box, update, to_proxy_button)


def to_proxy(event=None, arg=None):
    global win, box, update

    to_wifi_button = generate_wifi_button

    for i in box.get_children():
        box.remove(i)

    set_proxy.activate(win, box, update, to_wifi_button)

    win.show_all()


def generate_wifi_button():
    to_wifi_button = Gtk.EventBox()
    to_wifi_button.get_style_context().add_class("apply_changes_button")
    to_wifi_button.get_style_context().add_class("green")
    to_wifi_label = Gtk.Label("BACK TO WIFI")
    to_wifi_label.get_style_context().add_class("apply_changes_text")
    to_wifi_button.add(to_wifi_label)
    to_wifi_button.modify_font(Pango.FontDescription("Bariol 13"))
    to_wifi_button.set_size_request(150, 44)
    to_wifi_button.connect("button_press_event", to_wifi)
    return to_wifi_button


def generate_proxy_button():
    to_proxy_button = Gtk.EventBox()
    to_proxy_label = Gtk.Label("Proxy")
    to_proxy_label.get_style_context().add_class("orange")
    to_proxy_button.add(to_proxy_label)
    to_proxy_button.connect("button_press_event", to_proxy)
    return to_proxy_button


def to_wifi(event=None, arg=None):
    global win, box, update, to_proxy_button

    to_proxy_button = generate_proxy_button()
    for i in box.get_children():
        box.remove(i)

    set_wifi.activate(win, box, update, to_proxy_button)
    win.show_all()


def apply_changes(event=None, button=None):
    set_wifi.apply_changes()
    return
