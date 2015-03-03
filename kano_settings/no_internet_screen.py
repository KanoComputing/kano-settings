#!/usr/bin/env python

# no_internet_screen.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
from kano.gtk3.buttons import OrangeButton, KanoButton
from kano_settings.set_wifi import SetWifi
from kano_settings.common import media


class NoInternet(Gtk.Box):
    selected_button = 0
    initial_button = 0

    def __init__(self, win):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.win = win
        self.win.set_main_widget(self)
        # Main image
        image = Gtk.Image.new_from_file(media + "/Graphics/no-internet-screen.png")
        # Orange button
        later_button = OrangeButton("Later")
        later_button.connect("button_release_event", self.win.close_window)
        # Green button
        self.kano_button = KanoButton("CONNECT NOW")
        self.kano_button.pack_and_align()
        self.kano_button.connect("button-release-event", self.go_to_wifi)
        self.kano_button.connect("key-release-event", self.go_to_wifi)
        # Text label
        text_align = self.create_text_align()
        # Place elements
        image.set_margin_top(50)
        image.set_margin_bottom(30)
        self.pack_start(image, False, False, 0)
        self.pack_start(text_align, False, False, 2)
        self.pack_start(self.kano_button.align, False, False, 10)
        self.pack_start(later_button, False, False, 3)
        # Refresh window
        self.win.show_all()

    def go_to_wifi(self, widget=None, event=None):
        self.win.clear_win()
        SetWifi(self.win)

    def create_text_align(self):
        label = Gtk.Label("You need internet to continue")
        label.get_style_context().add_class("about_version")

        align = Gtk.Alignment(xalign=0.5, xscale=0, yalign=0, yscale=0)
        align.add(label)

        return align
