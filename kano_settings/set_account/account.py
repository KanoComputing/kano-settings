#!/usr/bin/env python
#
# account.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Controls the UI of the account setting

from gi.repository import Gtk
import os
from kano.gtk3.heading import Heading
import kano_settings.components.fixed_size_box as fixed_size_box
from kano.utils import get_user_unsudoed
import kano.gtk3.kano_dialog as kano_dialog
from kano.gtk3.buttons import KanoButton

win = None
button = None
box = None


def activate(_win, changeable_content, _button, pass_button):
    global win, button, box

    win = _win
    button = _button
    box = changeable_content
    title = Heading("System account settings", "Set your account")

    # Settings container
    settings = fixed_size_box.Fixed()

    pass_box = Gtk.Box()
    pass_box.add(pass_button)

    pass_align = Gtk.Alignment(xalign=0.5, yalign=0)
    pass_align.set_padding(0, 0, 125, 0)
    pass_align.add(pass_box)

    # Accounts label
    accounts_header = Heading("Accounts", "Add or remove accounts")

    # Add account button
    add_button = KanoButton("ADD ACCOUNT")
    add_button.set_size_request(200, 44)
    add_button.connect("button_press_event", add_account)

    # Remove account button
    remove_button = KanoButton("REMOVE ACCOUNT")
    remove_button.set_color("red")
    remove_button.set_size_request(200, 44)
    remove_button.connect("button_press_event", remove_account_dialog)

    button_container = Gtk.Box()
    button_container.pack_start(add_button, False, False, 10)
    button_container.pack_start(remove_button, False, False, 10)

    button_align = Gtk.Alignment(xalign=0.5, yalign=0.5)
    button_align.set_padding(0, 0, 10, 0)
    button_align.add(button_container)

    settings.box.pack_start(pass_align, False, False, 0)
    settings.box.pack_start(accounts_header.container, False, False, 10)
    settings.box.pack_start(button_align, False, False, 0)

    changeable_content.pack_start(title.container, False, False, 0)
    changeable_content.pack_start(settings.box, False, False, 0)

    win.show_all()


def add_account(event=None, button=None):
    # Bring in message dialog box
    kdialog = kano_dialog.KanoDialog("New account scheduled.", "Reboot the system.")
    kdialog.run()
    os.system("sudo kano-init newuser")


def remove_account_dialog(event=None, button=None):
    # Bring in message dialog box
    kdialog = kano_dialog.KanoDialog("Are you sure you want to delete the current user?", "", {"OK": -1, "CANCEL": 0})
    response = kdialog.run()
    if response == -1:
        remove_user()


def remove_user():
    cmd = 'sudo kano-init deleteuser %s' % (get_user_unsudoed())
    os.system(cmd)


def apply_changes(button):
    return
