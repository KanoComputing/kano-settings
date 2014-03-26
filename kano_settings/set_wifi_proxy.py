#!/usr/bin/env python

# wifi_proxy_commenuicaton.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Pango
import kano_settings.set_proxy as set_proxy
import kano_settings.set_wifi as set_wifi


def activate(win, box, update):

    to_proxy_button = Gtk.EventBox()
    to_proxy_label = Gtk.Label("Proxy")
    to_proxy_label.get_style_context().add_class("orange")
    to_proxy_button.add(to_proxy_label)

    to_wifi_button = Gtk.EventBox()
    to_wifi_button.get_style_context().add_class("apply_changes_button")
    to_wifi_label = Gtk.Label("BACK TO WIFI")
    to_wifi_label.get_style_context().add_class("apply_changes_text")
    to_wifi_button.add(to_wifi_label)
    to_wifi_button.modify_font(Pango.FontDescription("Bariol 13"))
    to_wifi_button.set_size_request(150, 44)

    to_proxy_button.connect("button_press_event", to_proxy, [win, box, update, to_wifi_button])
    to_wifi_button.connect("button_press_event", to_wifi, [win, box, update, to_proxy_button])

    set_wifi.activate(win, box, update, to_proxy_button)


def to_proxy(event=None, arg=None, data=[]):

    win = data[0]
    box = data[1]
    update = data[2]
    to_wifi_button = data[3]

    for i in box.get_children():
        box.remove(i)

    set_proxy.activate(win, box, update, to_wifi_button)

    win.show_all()


def to_wifi(event=None, arg=None, data=[]):
    win = data[0]
    box = data[1]
    update = data[2]
    to_proxy_button = data[3]

    for i in box.get_children():
        box.remove(i)

    set_wifi.activate(win, box, update, to_proxy_button)

    win.show_all()
