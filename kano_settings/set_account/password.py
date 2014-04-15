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

    # Potentially add icons next to Entries for instant verification.
    #success_icon1 = Gtk.Image()
    #tick = icons.Icons("tick").subpixbuf
    #cross = icons.Icons("cross").subpixbuf
    #email_entry.attach(success_icon, 1, 1, 1, 1)

    _update.disable()

    title = heading.Heading("Change your password", "Keep out the baddies!")

    changeable_content.pack_start(title.container, False, False, 0)
    changeable_content.pack_start(settings.box, False, False, 0)
    changeable_content.pack_start(_update.box, False, False, 10)

    win.show_all()


def apply_changes(button=None):
    global win

    #text1 = entry1.get_text()
    text2 = entry2.get_text()
    text3 = entry3.get_text()

    returnvalue = 0

    # Verify the current password in the first text box

    if text2 == text3:

        out, e, cmdvalue = utils.run_cmd("echo $SUDO_USER:%s | sudo chpasswd" % (text2))

        # if password is not changed
        if cmdvalue != 0:
            dialog = Gtk.MessageDialog(win, 0, Gtk.MessageType.ERROR,
                                       Gtk.ButtonsType.OK_CANCEL, "Could not change password")
            dialog.format_secondary_text("Either your old password is incorrect, or your new password is not long enough.  Try again.")
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                # do nothing
                # Returning -1 means we don't use the default_intro.py flow
                returnvalue = -1
            elif response == Gtk.ResponseType.CANCEL:
                returnvalue = 0

            dialog.destroy()
            clear_text(entry1, entry2, entry3)
            return returnvalue

    else:
        dialog = Gtk.MessageDialog(win, 0, Gtk.MessageType.ERROR,
                                   Gtk.ButtonsType.OK_CANCEL, "Could not change password")
        dialog.format_secondary_text("Your new passwords don't match!  Try again")
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            # do nothing
            returnvalue = -1
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()
            # Go back to the accounts screen
            returnvalue = 0

        dialog.destroy()
        clear_text(entry1, entry2, entry3)
        return returnvalue


def clear_text(entry1, entry2, entry3):
    entry1.set_text("")
    entry2.set_text("")
    entry3.set_text("")


def enable_button(widget=None, event=None, apply_changes=None):
    text1 = entry1.get_text()
    text2 = entry2.get_text()
    text3 = entry3.get_text()
    apply_changes.button.set_sensitive(text1 != "" and text2 != "" and text3 != "")
