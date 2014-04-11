#!/usr/bin/env python
#
# set_account.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
import os
import kano_settings.components.heading as heading
import kano_settings.components.fixed_size_box as fixed_size_box
from kano.utils import get_user_unsudoed

win = None
update = None


def activate(_win, changeable_content, _update):
    global win, update

    win = _win
    update = _update

    title = heading.Heading("System account settings", "Set your account")

    # Settings container
    settings = fixed_size_box.Fixed()

    # Text entry
    account_entry = Gtk.Grid(column_homogeneous=False,
                             column_spacing=22,
                             row_spacing=22)

    # Change password button
    pass_button = Gtk.EventBox()
    pass_button.get_style_context().add_class("apply_changes_button")
    pass_button.get_style_context().add_class("green")
    pass_label = Gtk.Label("CHANGE PASSWORD")
    pass_label.get_style_context().add_class("apply_changes_text")
    pass_button.add(pass_label)
    pass_button.set_size_request(200, 44)
    pass_button.connect("button_press_event", set_password)

    # Accounts label
    accounts_label = Gtk.Label("ACCOUNTS")

    # Add account button
    add_button = Gtk.EventBox()
    add_button.get_style_context().add_class("apply_changes_button")
    add_button.get_style_context().add_class("green")
    add_label = Gtk.Label("ADD ACCOUNT")
    add_label.get_style_context().add_class("apply_changes_text")
    add_button.add(add_label)
    add_button.set_size_request(200, 44)
    add_button.connect("button_press_event", add_account)

    # Remove account button
    remove_button = Gtk.EventBox()
    remove_button.get_style_context().add_class("apply_changes_button")
    remove_button.get_style_context().add_class("green")
    remove_label = Gtk.Label("REMOVE ACCOUNT")
    remove_label.get_style_context().add_class("apply_changes_text")
    remove_button.add(remove_label)
    remove_button.set_size_request(200, 44)
    remove_button.connect("button_press_event", remove_account)

    account_entry.attach(pass_button, 0, 0, 1, 1)
    account_entry.attach(accounts_label, 0, 1, 1, 1)
    account_entry.attach(add_button, 0, 2, 1, 1)
    account_entry.attach(remove_button, 0, 3, 1, 1)

    valign = Gtk.Alignment(xalign=0.5, yalign=0, xscale=0, yscale=0)
    padding_above = 0
    valign.set_padding(padding_above, 0, 47, 0)
    valign.add(account_entry)
    settings.box.pack_start(valign, False, False, 0)

    changeable_content.pack_start(title.container, False, False, 0)
    changeable_content.pack_start(settings.box, False, False, 0)
    changeable_content.pack_start(update.box, False, False, 0)

    update.disable()


def set_password(event=None, button=None):
    # TODO: launch password screen
    pass


def add_account(event=None, button=None):
    # Bring in message dialog box
    dialog = Gtk.MessageDialog(
        win, 0, Gtk.MessageType.INFO,
        Gtk.ButtonsType.OK, "")
    dialog.format_secondary_text("New account scheduled. Reboot the system.")
    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        os.system("sudo kano-init newuser")
    dialog.destroy()


def remove_account(event=None, button=None):
    # Bring in message dialog box
    dialog = Gtk.MessageDialog(
        win, 0, Gtk.MessageType.INFO,
        Gtk.ButtonsType.OK, "")
    dialog.format_secondary_text("Are you sure you want to delete current user?")
    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        cmd = 'sudo kano-init deleteuser %s' % (get_user_unsudoed())
        os.system(cmd)
    dialog.destroy()


def apply_changes(button):

    return 1
