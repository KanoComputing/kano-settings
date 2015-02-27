#!/usr/bin/env python

# set_overclock.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gdk
from kano_settings.templates import RadioButtonTemplate
import kano_settings.common as common
from kano_settings.boot_config import get_config_value
from kano_settings.data import get_data
from kano_settings.system.overclock import change_overclock_value, rpi1_modes, rpi1_overclock_values

# 0 = None
# 1 = Modest
# 2 = Medium
# 3 = High
# 4 = Turbo



class SetOverclock(RadioButtonTemplate):
    selected_button = 0
    initial_button = 0
    boot_config_file = "/boot/config.txt"

    data = get_data("SET_OVERCLOCK")

    def __init__(self, win):

        title = self.data["LABEL_1"]
        description = self.data["LABEL_2"]
        kano_label = self.data["KANO_BUTTON"]
        option1 = self.data["OPTION_1"]
        desc1 = self.data["DESCRIPTION_1"]
        option2 = self.data["OPTION_2"]
        desc2 = self.data["DESCRIPTION_2"]
        option3 = self.data["OPTION_3"]
        desc3 = self.data["DESCRIPTION_3"]
        option4 = self.data["OPTION_4"]
        desc4 = self.data["DESCRIPTION_4"]
        option5 = self.data["OPTION_5"]
        desc5 = self.data["DESCRIPTION_5"]

        self.modes = rpi1_modes
        self.overclock_values = rpi1_overclock_values

        RadioButtonTemplate.__init__(self, title, description, kano_label,
                                     [[option1, desc1],
                                      [option2, desc2],
                                      [option3, desc3],
                                      [option4, desc4],
                                      [option5, desc5]])
        self.win = win
        self.win.set_main_widget(self)

        # Show the current setting by electing the appropriate radio button
        self.current_setting()
        self.selected_button = self.initial_button
        self.get_button(self.initial_button).set_active(True)

        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.win.go_to_home)

        self.kano_button.connect("button-release-event", self.set_overclock)
        self.kano_button.connect("key-release-event", self.set_overclock)

        self.win.show_all()

    def set_overclock(self, widget, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

            # Mode has no changed
            if self.initial_button == self.selected_button:
                self.win.go_to_home()
                return

            change_overclock_value(self.modes[self.selected_button])

            # Tell user to reboot to see changes
            common.need_reboot = True

            self.win.go_to_home()

    def current_setting(self):
        freq = get_config_value('arm_freq')

        for x in self.modes:
            if self.overclock_values[x]['arm_freq'] == freq:
                self.initial_button = self.modes.index(x)

    def on_button_toggled(self, button):

        if button.get_active():
            label = button.get_label()
            self.selected_button = self.modes.index(label)
