#!/usr/bin/env python
#
# password.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Controls the UI of the change password screen

from gi.repository import Gtk
from kano.gtk3.heading import Heading
import kano_settings.components.fixed_size_box as fixed_size_box
import kano.gtk3.kano_dialog as kano_dialog

win = None
entry1 = None
entry2 = None


def activate(_win, changeable_content, _update):
    global win, entry1, entry2

    win = _win
    settings = fixed_size_box.Fixed()

    entry1 = Gtk.Entry()
    entry1.set_size_request(300, 44)
    entry1.props.placeholder_text = "Select password"
    entry1.set_visibility(False)
    entry2 = Gtk.Entry()
    entry2.props.placeholder_text = "Confirm password"
    entry2.set_visibility(False)

    entry1.connect("key_release_event", enable_button, _update)
    entry2.connect("key_release_event", enable_button, _update)

    # Entry container
    entry_container = Gtk.Grid(column_homogeneous=False,
                               column_spacing=22,
                               row_spacing=10)

    entry_container.attach(entry1, 0, 0, 1, 1)
    entry_container.attach(entry2, 0, 1, 1, 1)

    align = Gtk.Alignment(xalign=0.5, yalign=0, xscale=0, yscale=0)
    align.add(entry_container)
    settings.box.pack_start(align, False, False, 0)
    _update.set_sensitive(False)
    title = Heading("Parental lock", "Enter password")

    changeable_content.pack_start(title.container, False, False, 0)
    changeable_content.pack_start(settings.box, False, False, 0)
    changeable_content.pack_start(_update.align, False, False, 10)

    win.show_all()


def apply_changes(button=None):

    password1 = entry1.get_text()
    password2 = entry2.get_text()

    # If the two new passwords match
    if password1 == password2:
        # TODO: create encrypted passwrod
        pass
    else:
        return create_dialog("Careful", "The passwords don't match! Try again")


def create_dialog(message1="Could not change password", message2=""):

    kdialog = kano_dialog.KanoDialog(message1, message2, {"TRY AGAIN": -1, "GO BACK": 0})
    response = kdialog.run()
    return response


def clear_text():
    global entry1, entry2
    entry1.set_text("")
    entry2.set_text("")


def enable_button(widget=None, event=None, apply_changes=None):
    text1 = entry1.get_text()
    text2 = entry2.get_text()
    apply_changes.set_sensitive(text1 != "" and text2 != "")
