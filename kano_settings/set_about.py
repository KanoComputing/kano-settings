#!/usr/bin/env python

# set_about.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import subprocess
import os
from gi.repository import Gtk
from kano.gtk3.kano_dialog import KanoDialog
from kano.gtk3.buttons import OrangeButton, KanoButton
from kano_profile.paths import legal_dir
from kano_settings.common import media
from kano_settings.data import get_data
from kano_settings.templates import TopBarTemplate


class SetAbout(TopBarTemplate):
    selected_button = 0
    initial_button = 0

    data = get_data("SET_ABOUT")

    def __init__(self, win):

        kano_label = self.data["KANO_BUTTON"]

        TopBarTemplate.__init__(self)

        self.win = win
        self.win.set_main_widget(self)
        self.top_bar.enable_prev()

        self.top_bar.enable_prev()
        self.top_bar.set_prev_callback(self.win.go_to_home)

        image = Gtk.Image.new_from_file(media + "/Graphics/about-screen.png")

        version_align = self.create_version_align()

        space_available = self.get_space_available()
        temperature = self.get_temperature()

        space_align = self.create_other_align(space_available)
        temperature_align = self.create_other_align(temperature)

        terms_and_conditions = OrangeButton("Terms and conditions")
        terms_and_conditions.connect("button_release_event", self.show_terms_and_conditions)

        self.kano_button = KanoButton(kano_label)
        self.kano_button.pack_and_align()

        image.set_margin_top(30)
        self.pack_start(image, False, False, 10)
        self.pack_start(version_align, False, False, 2)
        self.pack_start(space_align, False, False, 2)
        self.pack_start(temperature_align, False, False, 2)
        self.pack_start(terms_and_conditions, False, False, 3)
        self.pack_start(self.kano_button.align, False, False, 10)

        self.kano_button.connect("button-release-event", self.win.go_to_home)
        self.kano_button.connect("key-release-event", self.win.go_to_home)

        # Refresh window
        self.win.show_all()

    def get_current_version(self):
        output = subprocess.check_output(["cat", "/etc/kanux_version"])
        version_number = output.split("-")[-1].strip()
        return "Kano OS v." + version_number

    def get_space_available(self):
        output = subprocess.check_output("df -h | grep rootfs", shell=True)
        items = output.strip().split(" ")
        items = filter(None, items)
        total_space = items[1]
        space_used = items[2]
        return "Disk space used: " + space_used + " / " + total_space

    def get_temperature(self):
        degree_sign = u'\N{DEGREE SIGN}'
        output = subprocess.check_output("cputemp0=`cat /sys/class/thermal/thermal_zone0/temp`; \
                                         cputemp1=$(($cputemp0/1000)); \
                                         cputemp2=$(($cputemp0/100)); \
                                         cputemp=$(($cputemp2%$cputemp1)); \
                                         echo $cputemp1\".\"$cputemp", shell=True)
        output = output.strip()
        return "Temperature: " + output + degree_sign + "C"

    def create_version_align(self):
        text = self.get_current_version()
        label = Gtk.Label(text)
        label.get_style_context().add_class("about_version")

        align = Gtk.Alignment(xalign=0.5, xscale=0, yalign=0, yscale=0)
        align.add(label)

        return align

    def create_other_align(self, text):
        label = Gtk.Label(text)
        label.get_style_context().add_class("about_label")

        align = Gtk.Alignment(xalign=0.5, xscale=0, yalign=0, yscale=0)
        align.add(label)

        return align

    def show_terms_and_conditions(self, widget, event):

        legal_text = ''
        for file in os.listdir(legal_dir):
            with open(legal_dir + file, 'r') as f:
                legal_text = legal_text + f.read() + '\n\n\n'

        kdialog = KanoDialog("Terms and conditions", "",
                             scrolled_text=legal_text,
                             parent_window=self.win)
        kdialog.run()
