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
from kano.utils import get_user_unsudoed, ensure_dir
import kano.gtk3.kano_dialog as kano_dialog
from kano.gtk3.buttons import KanoButton


win = None
button = None
box = None

add_button = None
remove_button = None
added_or_removed_account = False


ADD_REMOVE_USER_PATH = '/tmp/kano-init/add-remove'


def activate(_win, changeable_content, _button, pass_button):
    global win, button, box, add_button, remove_button

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

    # Check if we already scheduled an account add or remove by checking the file
    added_or_removed_account = os.path.exists(ADD_REMOVE_USER_PATH)

    # Add account button
    add_button = KanoButton("ADD ACCOUNT")
    add_button.set_size_request(200, 44)
    add_button.connect("button_press_event", add_account)
    add_button.connect("key_press_event", add_account)

    # Remove account button
    remove_button = KanoButton("REMOVE ACCOUNT")
    remove_button.set_color("red")
    remove_button.set_size_request(200, 44)
    remove_button.connect("button_press_event", remove_account_dialog)
    remove_button.connect("key_press_event", remove_account_dialog)

    # Disable buttons if we already scheduled
    if added_or_removed_account:
        disable_buttons()

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


# Gets executed when ADD button is clicked
def add_account(widget=None, event=None):
    if not hasattr(event, 'keyval') or event.keyval == 65293:
        # Bring in message dialog box
        kdialog = kano_dialog.KanoDialog("New account scheduled.", "Reboot the system.")
        kdialog.run()
        # add new user command
        os.system("kano-init newuser")
        disable_buttons()


# Gets executed when REMOVE button is clicked
def remove_account_dialog(widget=None, event=None):
    global add_button, remove_button

    if not hasattr(event, 'keyval') or event.keyval == 65293:
        # Bring in message dialog box
        kdialog = kano_dialog.KanoDialog("Are you sure you want to delete the current user?", "", {"OK": {"return_value": -1}, "CANCEL": {"return_value": 0}})
        response = kdialog.run()
        if response == -1:
            # remove current user command
            os.system('kano-init deleteuser %s' % (get_user_unsudoed()))
            disable_buttons()


# Disables both buttons and makes the temp 'flag' folder
def disable_buttons():
    global add_button, remove_button, added_or_removed_account

    add_button.set_sensitive(False)
    remove_button.set_sensitive(False)
    added_or_removed_account = True

    ensure_dir(ADD_REMOVE_USER_PATH)


def apply_changes(button):
    return
