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
import kano_settings.components.heading as heading
import kano_settings.components.fixed_size_box as fixed_size_box
from kano.utils import get_user_unsudoed
import password

win = None
update = None
box = None


def activate(_win, changeable_content, _update):
    global win, update, box

    win = _win
    update = _update
    box = changeable_content
    title = heading.Heading("System account settings", "Set your account")

    # Settings container
    settings = fixed_size_box.Fixed()

    # Change password button
    pass_button = Gtk.Button()
    pass_button.get_style_context().add_class("apply_changes_button")
    pass_button.get_style_context().add_class("green")
    pass_label = Gtk.Label("CHANGE PASSWORD")
    pass_label.get_style_context().add_class("apply_changes_text")
    pass_button.add(pass_label)
    pass_button.set_size_request(200, 44)
    pass_button.connect("button_press_event", set_password)

    pass_box = Gtk.Box()
    pass_box.add(pass_button)

    pass_align = Gtk.Alignment(xalign=0.5, yalign=0)
    pass_align.set_padding(0, 0, 125, 0)
    pass_align.add(pass_box)

    # Accounts label
    accounts_header = heading.Heading("Accounts", "Add or remove accounts")

    # Add account button
    add_button = Gtk.Button()
    add_button.get_style_context().add_class("apply_changes_button")
    add_button.get_style_context().add_class("green")
    add_label = Gtk.Label("ADD ACCOUNT")
    add_label.get_style_context().add_class("apply_changes_text")
    add_button.add(add_label)
    add_button.set_size_request(200, 44)
    add_button.connect("button_press_event", add_account)

    # Remove account button
    remove_button = Gtk.Button()
    remove_button.get_style_context().add_class("apply_changes_button")
    remove_button.get_style_context().add_class("red")
    remove_label = Gtk.Label("REMOVE ACCOUNT")
    remove_label.get_style_context().add_class("apply_changes_text")
    remove_button.add(remove_label)
    remove_button.set_size_request(200, 44)
    remove_button.connect("button_press_event", remove_account)

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


def set_password(event=None, button=None):
    global update
    # TODO: launch password screen
    #pass
    # Remove element in the dynamic box
    for i in box.get_children():
        box.remove(i)

    password.activate(win, box, update)


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
