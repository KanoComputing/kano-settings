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

def enable():
    libpreload.proxify(True)

def disable():
    libpreload.proxify(False)

def get_settings():
    return pxysettings.get_settings()

def set_settings(proxyip, proxyport, proxytype, username='', password=''):
    settings = {
        'proxy-ip'    : proxyip,
        'proxy-port'  : proxyport,
        'proxy-type'  : proxytype,   # on of : "socks_v4 socks_v5" or "http_v1.0"
        'username'    : None,
        'password'    : None
        }
    pxysettings.set_settings(settings)
