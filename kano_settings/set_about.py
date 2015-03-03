#!/usr/bin/env python

# set_about.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import webbrowser
from gi.repository import Gtk
from kano.gtk3.kano_dialog import KanoDialog
from kano.gtk3.buttons import OrangeButton, KanoButton
from kano_profile.paths import legal_dir
from kano_settings.common import media
from kano_settings.system.about import (
    get_current_version, get_space_available, get_temperature, get_model_name
)


class SetAbout(Gtk.Box):
    selected_button = 0
    initial_button = 0

    def __init__(self, win):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.win = win
        self.win.set_main_widget(self)
        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.win.go_to_home)

        image = Gtk.Image.new_from_file(media + "/Graphics/about-screen.png")

        version_align = self.create_version_align()
        space_available = get_space_available()
        temperature = get_temperature()
        model_name = get_model_name()

        space_align = self.create_other_align(space_available)
        temperature_align = self.create_other_align(temperature)
        model_align = self.create_other_align(model_name)

        terms_and_conditions = OrangeButton("Terms and conditions")
        terms_and_conditions.connect(
            "button_release_event", self.show_terms_and_conditions
        )

        credits_button = OrangeButton("Meet the team")
        credits_button.connect(
            "button_release_event", self.show_credits
        )

        changelog_button = OrangeButton("Changelog")
        changelog_button.connect(
            "button_release_event", self.show_changelog
        )

        self.kano_button = KanoButton("BACK")
        self.kano_button.pack_and_align()

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        hbox.pack_start(terms_and_conditions, False, False, 4)
        hbox.pack_start(credits_button, False, False, 4)
        hbox.pack_start(changelog_button, False, False, 4)
        hbutton_container = Gtk.Alignment(
            xalign=0.5, xscale=0, yalign=0, yscale=0
        )
        hbutton_container.add(hbox)

        image.set_margin_top(10)
        self.pack_start(image, False, False, 10)
        self.pack_start(version_align, False, False, 2)
        self.pack_start(space_align, False, False, 1)
        self.pack_start(temperature_align, False, False, 1)
        self.pack_start(model_align, False, False, 1)
        self.pack_start(hbutton_container, False, False, 3)
        self.pack_start(self.kano_button.align, False, False, 10)

        self.kano_button.connect("button-release-event", self.win.go_to_home)
        self.kano_button.connect("key-release-event", self.win.go_to_home)

        # Refresh window
        self.win.show_all()

    def create_version_align(self):
        '''This is the widget (Gtk.Alignment) containing the version
        information. This has different styling to the other information
        '''

        version_number = get_current_version()
        version_long = "Kano OS v." + version_number
        label = Gtk.Label(version_long)
        label.get_style_context().add_class("about_version")

        align = Gtk.Alignment(xalign=0.5, xscale=0, yalign=0, yscale=0)
        align.add(label)

        return align

    def create_other_align(self, text):
        '''This is the default template for any other information
        '''

        label = Gtk.Label(text)
        label.get_style_context().add_class("about_label")

        align = Gtk.Alignment(xalign=0.5, xscale=0, yalign=0, yscale=0)
        align.add(label)

        return align

    def show_terms_and_conditions(self, widget, event):
        '''This is the dialog containing the terms and conditions - same as
        shown before creating an account
        '''

        legal_text = ''
        for file in os.listdir(legal_dir):
            with open(legal_dir + file, 'r') as f:
                legal_text = legal_text + f.read() + '\n\n\n'

        kdialog = KanoDialog("Terms and conditions", "",
                             scrolled_text=legal_text,
                             parent_window=self.win)
        kdialog.run()

    def show_credits(self, widget, event):
        '''Launch the credits
        '''

        os.system(
            "/usr/bin/kano-launcher \"kdesk-blur 'urxvt -bg "
            "rgba:0000/0000/0000/FFFF -title 'Credits' -e "
            "/usr/bin/kano-credits'\""
        )

    def show_changelog(self, widget, event):
        '''Launch chromium with the link of the relevent changelog
        '''

        # Assuming current_version is of the form 1.3.4
        current_version = get_current_version()

        # Full link should be analogous to
        # http://world.kano.me/forum/topic/kanux-beta-v1.2.3
        link = "http://world.kano.me/forum/topic/kanux-beta-v{}".format(
            current_version
        )

        # Open in Chromium
        webbrowser.open(link)
