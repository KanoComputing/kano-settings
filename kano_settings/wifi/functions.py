#!/usr/bin/env python

# functions.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
import os
from kano.utils import get_user_unsudoed
import kano_settings.proxy as proxy
import kano.utils as utils

libpreload = proxy.LibPreload()
pxysettings = proxy.ProxySettings()


def is_enabled():
    return libpreload.is_enabled()


def enable():
    libpreload.proxify(True)


def disable():
    libpreload.proxify(False)


def set_settings(proxyip, proxyport, proxytype, username=None, password=None):
    settings = {
        'proxy-ip': proxyip,
        'proxy-port': proxyport,
        'proxy-type': proxytype,   # one of : "socks_v4 socks_v5" or "http_v1.0"
        'username': username,
        'password': password
    }
    pxysettings.set_settings(settings)


def get_settings():
    return pxysettings.get_settings()


def launch_chromium(widget=None, event=None):
    user_name = get_user_unsudoed()
    os.system('su ' + user_name + ' -c chromium')


def network_info():
    network = ''
    command_ip = ''
    command_network = '/sbin/iwconfig wlan0 | grep \'ESSID:\' | awk \'{print $4}\' | sed \'s/ESSID://g\' | sed \'s/\"//g\''
    out, e, _ = utils.run_cmd(command_network)
    if e:
        network = "Ethernet"
        command_ip = '/sbin/ifconfig eth0 | grep inet | awk \'{print $2}\' | cut -d\':\' -f2'
    else:
        network = out
        command_ip = '/sbin/ifconfig wlan0 | grep inet | awk \'{print $2}\' | cut -d\':\' -f2'
    ip, _, _ = utils.run_cmd(command_ip)

    return [network.rstrip(), ip.rstrip()]


