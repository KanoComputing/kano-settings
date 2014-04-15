#!/usr/bin/env python
#
# home.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Controls the communication between the account and password screen


import kano_settings.set_account.account as account
import kano_settings.set_account.password as password

win = None
box = None
update = None
to_wifi_button = None
to_proxy_button = None
disable_proxy = None
in_proxy = False


def activate(_win, changeable_content, _update):
    global box

    box = changeable_content
    account.activate(_win, changeable_content, _update)


def apply_changes(widget):
    password.apply_changes(widget)
