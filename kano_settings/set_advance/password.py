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
from kano.gtk3.kano_dialog import KanoDialog

from kano_settings.components import fixed_size_box
from .parental import set_parental_enabled

win = None
entry = None
entry1 = None
entry2 = None
parental_disabled = None


def activate(_win, _box, _button, _parental_disabled):
    global win, entry1, entry2, entry, parental_disabled

    win = _win
    settings = fixed_size_box.Fixed()
    parental_disabled = _parental_disabled

    # Entry container
    entry_container = Gtk.Grid(column_homogeneous=False,
                               column_spacing=22,
                               row_spacing=10)
    align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
    align.add(entry_container)

    # if disabled, turning on
    if _parental_disabled:
        entry1 = Gtk.Entry()
        entry1.set_size_request(300, 44)
        entry1.props.placeholder_text = "Select password"
        entry1.set_visibility(False)

        entry2 = Gtk.Entry()
        entry2.props.placeholder_text = "Confirm password"
        entry2.set_visibility(False)

        entry1.connect("key_release_event", enable_button, _button)
        entry2.connect("key_release_event", enable_button, _button)

        entry_container.attach(entry1, 0, 0, 1, 1)
        entry_container.attach(entry2, 0, 1, 1, 1)

        # Move email entries down by 25px
        align.set_padding(25, 0, 0, 0)

    # if enabled, turning off
    else:
        entry = Gtk.Entry()
        entry.set_size_request(300, 44)
        entry.props.placeholder_text = "Confirm your password"
        entry.set_visibility(False)
        entry.connect("key_release_event", enable_button, _button)
        entry_container.attach(entry, 0, 0, 1, 1)

        # Move email entries down by 50px
        align.set_padding(50, 0, 0, 0)

    settings.box.pack_start(align, False, False, 0)
    _button.set_sensitive(False)
    title = Heading("Parental lock", "Enter password")

    _box.pack_start(title.container, False, False, 0)
    _box.pack_start(settings.box, False, False, 0)
    _box.pack_start(_button.align, False, False, 10)

    win.show_all()


def apply_changes(button=None):
    password = None

    # if disabled, turning on
    if parental_disabled:
        password = entry1.get_text()
        password2 = entry2.get_text()
        passed_test = (password == password2)
        error_heading = "Careful"
        error_description = "The passwords don't match! Try again"

    # if enabled, turning off
    else:
        password = entry.get_text()
        passed_test = True

    # if test passed, update parental configuration
    if passed_test:
        update_config(password)

    # else, display try again dialog
    else:
        response = create_dialog(error_heading, error_description)
        if response == -1:
            if parental_disabled:
                entry1.set_text("")
                entry2.set_text("")
            else:
                entry.set_text("")
        return response

    return 0


def create_dialog(message1, message2):
    kdialog = KanoDialog(
        message1,
        message2,
        {
            "TRY AGAIN": {
                "return_value": -1
            },
            "GO BACK": {
                "return_value": 0
            }
        },
        parent_window=win
    )

    response = kdialog.run()
    return response


def enable_button(widget=None, event=None, apply_changes=None):
    # if disabled, turning on
    if parental_disabled:
        text1 = entry1.get_text()
        text2 = entry2.get_text()
        apply_changes.set_sensitive(text1 != "" and text2 != "")

    # if enabled, turning off
    else:
        text = entry.get_text()
        apply_changes.set_sensitive(text != "")


def update_config(password=None):
    # if disabled, turning on
    if parental_disabled:
        success, msg = set_parental_enabled(True, password)

    # if enabled, turning off
    else:
        success, msg = set_parental_enabled(False, password)

    if success:
        heading = "Succes"
    else:
        heading = "Error"

    kdialog = KanoDialog(heading, msg, parent_window=win)
    kdialog.run()

