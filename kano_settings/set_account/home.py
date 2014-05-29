#!/usr/bin/env python
#
# home.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Controls the communication between the account and password screen


from gi.repository import Gtk
import kano_settings.set_account.account as account
import kano_settings.set_account.password as password
import kano.gtk3.cursor as cursor

win = None
box = None
update = None
in_password = False


def activate(_win, changeable_content, _update):
    global box, win, update, in_password

    win = _win
    box = changeable_content
    update = _update
    pass_button = password_button()
    account.activate(_win, changeable_content, _update, pass_button)
    set_in_password(False)


def to_account(arg1=None, arg2=None):
    global win, box, update, in_password

    remove_children(box)
    pass_button = password_button()
    account.activate(win, box, update, pass_button)
    set_in_password(False)


def to_password(arg1=None, arg2=None):
    global win, box, update, in_password

    remove_children(box)
    password.activate(win, box, update)
    set_in_password(True)


def password_button():
    pass_button = Gtk.Button("CHANGE PASSWORD")
    pass_button.get_style_context().add_class("green_button")
    pass_button.set_size_request(200, 44)
    cursor.attach_cursor_events(pass_button)
    pass_button.connect("button_press_event", to_password)
    return pass_button


def remove_children(box):
    for i in box.get_children():
        box.remove(i)


def apply_changes(widget):
    return password.apply_changes(widget)


def set_in_password(boolean):
    global in_password
    in_password = boolean


def get_in_password():
    return in_password
