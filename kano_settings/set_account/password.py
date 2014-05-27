#!/usr/bin/env python
#
# password.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Controls the UI of the change password screen

from gi.repository import Gtk
import kano_settings.components.heading as heading
import kano_settings.components.fixed_size_box as fixed_size_box
import kano.utils as utils
import pam
import kano.gtk3.dialog.kano_dialog as kano_dialog
#from kano.utils import get_user_unsudoed

win = None
entry1 = None
entry2 = None
entry3 = None


def activate(_win, changeable_content, _update):
    global win, entry1, entry2, entry3

    win = _win
    settings = fixed_size_box.Fixed()

    entry1 = Gtk.Entry()
    entry1.set_size_request(300, 44)
    entry1.props.placeholder_text = "Old password"
    entry1.set_visibility(False)
    entry2 = Gtk.Entry()
    entry2.props.placeholder_text = "New password"
    entry2.set_visibility(False)
    entry3 = Gtk.Entry()
    entry3.props.placeholder_text = "Repeat new password"
    entry3.set_visibility(False)

    entry1.connect("key_release_event", enable_button, _update)
    entry2.connect("key_release_event", enable_button, _update)
    entry3.connect("key_release_event", enable_button, _update)

    # Entry container
    entry_container = Gtk.Grid(column_homogeneous=False,
                               column_spacing=22,
                               row_spacing=10)

    entry_container.attach(entry1, 0, 0, 1, 1)
    entry_container.attach(entry2, 0, 1, 1, 1)
    entry_container.attach(entry3, 0, 2, 1, 1)

    align = Gtk.Alignment(xalign=0.5, yalign=0, xscale=0, yscale=0)
    align.add(entry_container)
    settings.box.pack_start(align, False, False, 0)
    _update.disable()
    title = heading.Heading("Change your password", "Keep out the baddies!")

    changeable_content.pack_start(title.container, False, False, 0)
    changeable_content.pack_start(settings.box, False, False, 0)
    changeable_content.pack_start(_update.box, False, False, 10)

    win.show_all()


def apply_changes(button=None):
    global win

    old_password = entry1.get_text()
    new_password1 = entry2.get_text()
    new_password2 = entry3.get_text()

    # Verify the current password in the first text box
    # Get current username
    username, e, num = utils.run_cmd("echo $SUDO_USER")
    # Remove trailing newline character
    username = username.rstrip()

    if not pam.authenticate(username, old_password):
        return create_dialog(message1="Could not change password", message2="Your old password is incorrect!")

    # If the two new passwords match
    if new_password1 == new_password2:
        out, e, cmdvalue = utils.run_cmd("echo $SUDO_USER:%s | sudo chpasswd" % (new_password1))
        # if password is not changed
        if cmdvalue != 0:
            return create_dialog("Could not change password", "Your new password is not long enough or contains special characters.  Try again.")
    else:
        return create_dialog("Could not change password", "Your new passwords don't match!  Try again")


def create_dialog(message1="Could not change password", message2=""):
    global win

    kdialog = kano_dialog.KanoDialog(message1, message2, {"TRY AGAIN": -1, "GO BACK": 0})
    response = kdialog.run()
    return response


def clear_text():
    global entry1, entry2, entry3
    entry1.set_text("")
    entry2.set_text("")
    entry3.set_text("")


def enable_button(widget=None, event=None, apply_changes=None):
    text1 = entry1.get_text()
    text2 = entry2.get_text()
    text3 = entry3.get_text()
    apply_changes.button.set_sensitive(text1 != "" and text2 != "" and text3 != "")
