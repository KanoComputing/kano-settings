#!/usr/bin/env python

# Template.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Template class based on Gtk.Box
#

from gi.repository import Gtk
from kano_settings.components.heading import Heading
from kano.gtk3.buttons import KanoButton, OrangeButton


class Template(Gtk.Box):

    def __init__(self, title, description, buttons, is_plug=False, img_path=None):
        super(Template, self).__init__(orientation=Gtk.Orientation.VERTICAL)
        self._focus_widget = None

        heading = Heading(
            title,
            description,
            is_plug,
            back_btn=False
        )
        bbox = Gtk.ButtonBox()
        bbox.set_spacing(20)
        bbox.set_layout(Gtk.ButtonBoxStyle.CENTER)
        bbox.set_margin_right(10)
        bbox.set_margin_left(10)

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

            if "focus" in b:
                self._focus_widget = gtk_button

        self.pack_start(heading.container, False, False, 0)
        heading.container.set_margin_right(15)
        heading.container.set_margin_left(15)

        if img_path:
            image = Gtk.Image.new_from_file(img_path)

        if is_plug:
            self.pack_start(image, False, False, 10)
            self.pack_start(bbox, False, False, 30)
        else:
            self.pack_start(image, False, False, 20)
            self.pack_end(bbox, False, False, 30)

        self.show_all()

    def button_grab_focus(self):
        if self._focus_widget is not None:
            self._focus_widget.grab_focus()
