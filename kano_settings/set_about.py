#!/usr/bin/env python

# set_about.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

# -*- coding: utf-8 -*-

import os
import subprocess
from gi.repository import Gtk
from kano.gtk3.kano_dialog import KanoDialog
from kano.gtk3.buttons import OrangeButton, KanoButton
from kano_profile.paths import legal_dir
from kano_settings.common import media
from kano.network import launch_browser
from kano.utils import read_file_contents
from kano_settings.system.about import (
    get_current_version, get_space_available, get_temperature, get_model_name
)
from kano.utils import get_user_unsudoed, get_cpu_id


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

        version_number, os_name = get_current_version()
        os_variant = read_file_contents('/etc/kanux_version_variant')
        cpu_id = get_cpu_id()

        version_align = self.create_align(
            "Kano OS: {name} v{version}".format(name=os_name, version=version_number),
            'about_version'
        )
        if os_variant:
            variant_align = self.create_align(
                "{variant}".format(variant=os_variant),
                'about_version'
            )
        space_align = self.create_align(
            _("Disk space used: {used}B / {total}B").format(**get_space_available())
        )
        try:
            celsius = u"{:.1f}\N{DEGREE SIGN}C".format(get_temperature())
        except ValueError:
            celsius = "?"
        temperature_align = self.create_align(
            _(u"Temperature: {celsius}").format(celsius=celsius)
        )
        model_align = self.create_align(
            _("Model: {model}").format(model=get_model_name())
        )
        cpu_id_align = self.create_align(
            _("CPU ID: {id}").format(id=cpu_id)
        )

        terms_and_conditions = OrangeButton(_("Terms and conditions"))
        terms_and_conditions.connect(
            'button_release_event', self.show_terms_and_conditions
        )

        credits_button = OrangeButton(_("Meet the team"))
        credits_button.connect(
            'button_release_event', self.show_credits
        )

        self.kano_button = KanoButton(_("BACK"))
        self.kano_button.pack_and_align()

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        hbox.pack_start(terms_and_conditions, False, False, 4)
        hbox.pack_start(credits_button, False, False, 4)
        hbutton_container = Gtk.Alignment(
            xalign=0.5, xscale=0, yalign=0, yscale=0
        )
        hbutton_container.add(hbox)

        image.set_margin_top(10)
        self.pack_start(image, False, False, 10)
        self.pack_start(version_align, False, False, 2)
        if os_variant:
            self.pack_start(variant_align, False, False, 2)
        self.pack_start(space_align, False, False, 1)
        self.pack_start(temperature_align, False, False, 1)
        self.pack_start(model_align, False, False, 1)
        self.pack_start(cpu_id_align, False, False, 1)
        self.pack_start(hbutton_container, False, False, 3)
        self.pack_start(self.kano_button.align, False, False, 10)

        self.kano_button.connect('button-release-event', self.win.go_to_home)
        self.kano_button.connect('key-release-event', self.win.go_to_home)

        # Refresh window
        self.win.show_all()

    def create_align(self, text, css_class='about_label'):
        '''This styles the status information in the 'about' dialog
        '''

        label = Gtk.Label(text)
        label.get_style_context().add_class(css_class)

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

        kdialog = KanoDialog(_("Terms and conditions"), "",
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
