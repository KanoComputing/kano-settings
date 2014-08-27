
#!/usr/bin/env python

# template.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Template container class
#

import os
from gi.repository import Gtk

from kano.gtk3.top_bar import TopBar
from kano.gtk3.buttons import KanoButton
from kano.gtk3.heading import Heading
from kano.gtk3.kano_dialog import KanoDialog
from kano.gtk3.scrolled_window import ScrolledWindow
import kano_settings.constants as constants


class TopBarTemplate(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.top_bar = TopBar("Settings")
        self.pack_start(self.top_bar, False, False, 0)
        self.top_bar.set_close_callback(self.close_window)

    # On closing window, will alert if any of the listed booleans are True
    def close_window(self, button, event):
        if constants.need_reboot:
            kdialog = KanoDialog(
                "Reboot?",
                "Your Kano needs to reboot for changes to apply",
                {
                    "REBOOT NOW": {
                        "return_value": 1,
                        "color": "orange"
                    },
                    "LATER": {
                        "return_value": 0,
                        "color": "grey"
                    }
                },
                parent_window=self.get_toplevel()
            )

            kdialog.set_action_background("grey")
            response = kdialog.run()
            if response == 1:
                os.system("sudo reboot")

        Gtk.main_quit()


class Template(TopBarTemplate):

    def __init__(self, title, description, button_text):
        TopBarTemplate.__init__(self)

        self.title = Heading(title, description)
        self.title.container.set_margin_bottom(0)
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.align = Gtk.Alignment(xscale=0, yscale=0, xalign=0.5, yalign=0.3)
        self.align.add(self.box)
        self.kano_button = KanoButton(button_text)
        self.kano_button.pack_and_align()
        self.kano_button.align.set_padding(0, 30, 0, 0)

        self.pack_start(self.title.container, False, False, 0)
        self.pack_start(self.align, True, True, 0)
        self.pack_end(self.kano_button.align, False, False, 0)


class ScrolledWindowTemplate(TopBarTemplate):

    def __init__(self, title, description, button_text):
        TopBarTemplate.__init__(self)

        self.sw = ScrolledWindow(wide_scrollbar=True)
        self.sw.set_size_request(630, 210)
        self.title = Heading(title, description)
        self.kano_button = KanoButton(button_text)
        self.kano_button.pack_and_align()

        self.pack_start(self.title.container, False, False, 0)
        self.pack_start(self.sw, False, False, 0)
        self.pack_start(self.kano_button.align, False, False, 0)


class LabelledListTemplate(Template):
    @staticmethod
    def label_button(button, text0, text1):
        button.set_label(text0)
        button.get_style_context().add_class("bold_toggle")

        info = Gtk.Label(text1)
        info.get_style_context().add_class("normal_label")

        box = Gtk.Box()
        box.pack_start(button, False, False, 0)
        box.pack_start(info, False, False, 0)

        return box

    def __init__(self, title, description, button_text, text_array):
        Template.__init__(self, title, description, button_text)
        self.button_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.buttons = []
        self.box.pack_start(self.button_container, False, False, 0)

    def label_button_and_pack(self, button, text0, text1):
        box = self.label_button(button, text0, text1)
        self.button_container.pack_start(box, False, False, 5)

    def get_button(self, index):
        return self.buttons[index]

    def set_button_spacing(self, number):
        self.button_container.set_spacing(number)


class RadioButtonTemplate(LabelledListTemplate):

    def __init__(self, title, description, button_text, text_array):
        LabelledListTemplate.__init__(self, title, description, button_text, text_array)

        button = Gtk.RadioButton.new_with_label_from_widget(None, text_array[0][0])
        self.buttons.append(button)
        self.label_button_and_pack(button, text_array[0][0], text_array[0][1])
        text_array.remove(text_array[0])
        button.connect("toggled", self.on_button_toggled)

        for text in text_array:
            button = Gtk.RadioButton.new_from_widget(self.buttons[0])
            self.buttons.append(button)
            self.label_button_and_pack(button, text[0], text[1])
            button.connect("toggled", self.on_button_toggled)


class CheckButtonTemplate(LabelledListTemplate):

    def __init__(self, title, description, button_text, text_array):
        LabelledListTemplate.__init__(self, title, description, button_text, text_array)

        for text in text_array:
            button = Gtk.CheckButton()
            self.buttons.append(button)
            self.label_button_and_pack(button, text[0], text[1])

