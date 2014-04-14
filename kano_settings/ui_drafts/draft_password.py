#!/usr/bin/env python
#
# set_password.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
import kano_settings.components.heading as heading
import kano_settings.components.fixed_size_box as fixed_size_box
#from kano.utils import get_user_unsudoed

win = None
update = None


def activate(_win, changeable_content, _update):
    global win, update

    entry1 = Gtk.Entry()
    entry1.props.placeholder_text = "Old password"
    entry1.set_visibility(False)
    entry2 = Gtk.Entry()
    entry2.props.placeholder_text = "New password"
    entry2.set_visibility(False)
    entry3 = Gtk.Entry()
    entry3.props.placeholder_text = "Repeat new password"
    entry3.set_visibility(False)

    title = heading.Heading("Change your password", "Keep out the baddies!")

    settings = fixed_size_box.Fixed()
    settings.box.pack_start(entry1, False, False, 0)
    settings.box.pack_start(entry2, False, False, 0)
    settings.box.pack_start(entry3, False, False, 0)

    changeable_content.pack_start(title.container, False, False, 0)
    changeable_content.pack_start(settings.box, False, False, 0)
    changeable_content.pack_start(_update.button, False, False, 0)

    _win.show_all()


def apply_changes():
    print "Clicked apply changes"

