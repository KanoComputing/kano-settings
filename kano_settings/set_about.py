#!/usr/bin/env python

# set_about.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import subprocess
from gi.repository import Gtk
from kano_settings.data import get_data
from kano_settings.templates import Template


class SetAbout(Template):
    selected_button = 0
    initial_button = 0

    data = get_data("SET_ABOUT")

    def __init__(self, win):

        title = self.data["LABEL_1"]
        description = self.data["LABEL_2"]
        kano_label = self.data["KANO_BUTTON"]

        Template.__init__(self, title, description, kano_label)

        self.win = win
        self.win.set_main_widget(self)
        self.top_bar.enable_prev()

        self.top_bar.enable_prev()
        self.top_bar.set_prev_callback(self.win.go_to_home)

        current_version = self.get_current_version()
        space_available = self.get_space_available()
        temperature = self.get_temperature()

        version_label = Gtk.Label(current_version)
        space_label = Gtk.Label(space_available)
        temperature_label = Gtk.Label(temperature)

        self.box.pack_start(version_label, False, False, 0)
        self.box.pack_start(space_label, False, False, 0)
        self.box.pack_start(temperature_label, False, False, 0)

        self.kano_button.connect("button-release-event", self.win.go_to_home)
        self.kano_button.connect("key-release-event", self.win.go_to_home)

        # Refresh window
        self.win.show_all()

    def get_current_version(self):
        output = subprocess.check_output(["cat", "/etc/kanux_version"])
        return output.strip()

    def get_space_available(self):
        output = subprocess.check_output("df -h | grep rootfs", shell=True)
        space_available = output.strip().split(" ")[-2]
        return space_available

    def get_temperature(self):
        degree_sign = u'\N{DEGREE SIGN}'
        output = subprocess.check_output("cputemp0=`cat /sys/class/thermal/thermal_zone0/temp`; \
                                         cputemp1=$(($cputemp0/1000)); \
                                         cputemp2=$(($cputemp0/100)); \
                                         cputemp=$(($cputemp2%$cputemp1)); \
                                         echo $cputemp1\".\"$cputemp", shell=True)
        output = output.strip()
        return output + degree_sign + "C"
