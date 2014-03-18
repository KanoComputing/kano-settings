#!/usr/bin/env python

# set_wifi.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Pango
import kano_settings.proxy as proxy

libpreload = proxy.LibPreload()
pxysettings = proxy.ProxySettings()

def is_enabled():
    return libpreload.is_enabled()

def enable(dict_settings):
    libpreload.proxify(True)
    pxysettings.set_settings(dict_settings)

def disable():
    libpreload.proxify(True)

def get_settings():
    pxysettings.get_settings()
