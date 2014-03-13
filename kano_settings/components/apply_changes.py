#!/usr/bin/env python

# apply_changes.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the style of the main button in the projects that applies the changes

from gi.repository import Gtk, Pango


class Apply(Gtk.Button):

    def __init__(self, icon_first=True):

        # Create button
        self.button = Gtk.Button()

        self.text = Gtk.Label()
        self.text.modify_font(Pango.FontDescription("Bariol bold 13"))
        # This doesn't seem to work?
        self.button.set_size_request(70, 30)
        # Contains writing and icon of button
        self.label = Gtk.Box()
        self.label.set_size_request(50, 20)
        #self.label.get_style_context().add_class("")

        self.image = Gtk.Image()
        self.button.add(self.label)
        # Get rid of annoying dotted borders around click buttons
        self.button.set_can_focus(False)
        # Allow button to be styled in css
        self.style = self.button.get_style_context()
        self.style.add_class("apply_changes")

        if icon_first:
            self.label.pack_start(self.image, False, False, 5)
            self.label.pack_start(self.text, False, False, 5)
        else:
            self.label.pack_start(self.text, False, False, 5)
            self.label.pack_start(self.image, False, False, 5)


