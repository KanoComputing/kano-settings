#!/usr/bin/env python

# menu_button.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the button styling in the default introduction screen which shows all the settings

from gi.repository import Gtk, Pango
import kano_settings.common as common
import kano.gtk3.cursor as cursor


class Menu_button():
    def __init__(self, name, description=''):

        # Contains the info about the level and the image
        self.container = Gtk.Grid()
        self.container.set_hexpand(True)
        self.container.props.margin = 20

        # Info about the different settings
        self.title = Gtk.Label(name)
        self.title.get_style_context().add_class("menu_intro_label")
        self.title.set_alignment(xalign=0, yalign=0)
        self.title.props.margin_top = 10

        self.description = Gtk.Label(description)
        self.description.get_style_context().add_class("menu_custom_label")
        self.description.set_ellipsize(Pango.EllipsizeMode.END)
        self.description.set_size_request(130, 10)
        self.description.set_alignment(xalign=0, yalign=0)
        self.description.props.margin_bottom = 8

        self.button = Gtk.Button()
        self.button.set_can_focus(False)
        cursor.attach_cursor_events(self.button)
        self.img = Gtk.Image()
        self.img.set_from_file(common.media + "/Icons/Icon-" + name + ".png")

        self.container.attach(self.title, 2, 0, 1, 1)
        self.container.attach(self.description, 2, 1, 1, 1)
        self.container.attach(self.img, 0, 0, 2, 2)
        self.container.set_row_spacing(2)
        self.container.set_column_spacing(20)
        self.container.props.valign = Gtk.Align.CENTER

        self.button.add(self.container)
