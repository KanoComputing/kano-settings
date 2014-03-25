#!/usr/bin/env python

# apply_changes.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the style of the main button in the projects that applies the changes

from gi.repository import Gtk, Pango


class Apply():

    def __init__(self, icon_first=True):

        # Create button
        self.button = Gtk.EventBox()

        self.text = Gtk.Label()
        self.text.modify_font(Pango.FontDescription("Bariol bold 13"))
        # Contains writing and icon of button
        self.label = Gtk.Box()
        self.label_style = self.button.get_style_context()
        self.label_style.add_class("apply_changes_label")
        self.label.add(self.text)
        self.button.add(self.label)
        self.label.props.halign = Gtk.Align.CENTER
        self.button.set_size_request(150, 44)

        # Get rid of annoying dotted borders around click buttons
        self.button.set_can_focus(False)
        # Allow button to be styled in css
        self.button_style = self.button.get_style_context()
        self.button_style.add_class("apply_changes_button")
        self.box = Gtk.Box()
        self.box.pack_start(self.button, False, False, 0)
        self.box.props.halign = Gtk.Align.CENTER

    def enable(self):

        self.button.set_sensitive(True)

    def disable(self):

        self.button.set_sensitive(False)
