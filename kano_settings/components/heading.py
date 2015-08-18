#!/usr/bin/env python

# kano_dialog.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Heading used frequently around kano-settings and kano-login

from gi.repository import Gtk
# import kano_settings.common as common


class Heading():
    def __init__(self, title, description):

        self.title = Gtk.Label(title)
        self.title_style = self.title.get_style_context()
        self.title_style.add_class('title')

        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.container.pack_start(self.title, False, False, 0)

        if description != "":
            self.description = Gtk.Label(description)
            self.description.set_justify(Gtk.Justification.CENTER)
            self.description.set_line_wrap(True)
            self.description_style = self.description.get_style_context()
            self.description_style.add_class('description')

            self.container.pack_start(self.description, False, False, 0)

    def set_text(self, title, description):
        self.title.set_text(title)
        if getattr(self, 'description'):
            self.description.set_text(description)

    def get_text(self):
        if getattr(self, 'description'):
            return [self.title.get_text(), self.description.get_text()]
        else:
            return [self.title.get_text(), ""]

    def set_margin(self, top_margin, right_margin, bottom_margin, left_margin):
        self.container.set_margin_left(left_margin)
        self.container.set_margin_right(right_margin)
        self.container.set_margin_top(top_margin)
        self.container.set_margin_bottom(bottom_margin)

    def add_plug_styling(self):
        self.title.get_style_context().add_class("plug")
        self.description.get_style_context().add_class("plug")
