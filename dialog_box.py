#!/usr/bin/env python3

# dialog_box.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#


from gi.repository import Gtk


class DialogWindow(Gtk.Dialog):

    def __init__(self, parent, labelText):
        Gtk.Dialog.__init__(self, "My Dialog", parent, 0,
            (Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)

        label = Gtk.Label(labelText)

        box = self.get_content_area()
        box.add(label)
        self.show_all()
