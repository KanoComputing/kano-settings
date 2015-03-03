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
from kano_settings.system.overclock import change_overclock_value
from kano_settings.system.overclock import rpi1_modes, rpi1_overclock_values
from kano_settings.system.overclock import rpi2_modes, rpi2_overclock_values
from kano.utils import is_model_2_b


class SetOverclock(RadioButtonTemplate):
    selected_button = 0
    initial_button = 0
    boot_config_file = "/boot/config.txt"

    def __init__(self, win):
        self.is_pi2 = is_model_2_b()

        if self.is_pi2:
            self.modes = rpi2_modes
            self.overclock_values = rpi2_overclock_values
        else:
            self.modes = rpi1_modes
            self.overclock_values = rpi1_overclock_values

        options = []
        for m in self.modes:
            v = self.overclock_values.get(m)
            options.append([
                m,
                "{}HZ ARM, {}HZ CORE, {}MHZ SDRAM, {} OVERVOLT".format(
                    v['arm_freq'],
                    v['core_freq'],
                    v['sdram_freq'],
                    v['over_voltage']
                )
            ])

        RadioButtonTemplate.__init__(
            self,
            "Overclock your processor",
            "Make your computer's brain think faster, but run hotter.",
            "APPLY CHANGES",
            options
        )
        
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

            change_overclock_value(self.modes[self.selected_button],self.is_pi2)

            # Tell user to reboot to see changes
            common.need_reboot = True

            self.win.go_to_home()

    def current_setting(self):
        # The initial button defaults to zero (above) if the user has
        # selected a different frequency
        freq = get_config_value('arm_freq')

        for x in self.modes:
            if self.overclock_values[x]['arm_freq'] == freq:
                self.initial_button = self.modes.index(x)

    def on_button_toggled(self, button):

        if button.get_active():
            label = button.get_label()
            self.selected_button = self.modes.index(label)
