#!/usr/bin/env python

# Template.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Template class based on Gtk.Box
#

from gi.repository import Gtk
from kano.gtk3.heading import Heading
from kano.gtk3.buttons import KanoButton, OrangeButton


class Template(Gtk.Box):

    def __init__(self, title, description, buttons):
        super(Template, self).__init__(orientation=Gtk.Orientation.VERTICAL)

        heading = Heading(title, description)
        bbox = Gtk.ButtonBox()
        bbox.set_spacing(20)
        bbox.set_layout(Gtk.ButtonBoxStyle.CENTER)

        for b in buttons:
            label = b["label"]

            if not label:
                gtk_button = Gtk.Label()

            else:
                button_type = b["type"]
                callback = b["callback"]

                if button_type == "KanoButton":
                    color = b["color"]
                    gtk_button = KanoButton(label, color=color)
                elif button_type == "OrangeButton":
                    gtk_button = OrangeButton(label)

                gtk_button.connect("clicked", callback)
            bbox.pack_start(gtk_button, False, False, 0)

        self.pack_start(heading.container, False, False, 0)
        self.pack_end(bbox, False, False, 30)
        self.show_all()
