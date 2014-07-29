#!/usr/bin/env python

# set_overclock.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from kano_settings.templates import RadioButtonTemplate
import kano_settings.constants as constants
from kano.logging import logger
from .config_file import set_setting, file_replace


class SetOverclock(RadioButtonTemplate):
    selected_button = 0
    initial_button = 0
    boot_config_file = "/boot/config.txt"

    def __init__(self, win):
        RadioButtonTemplate.__init__(self, "Overclocking", "Let\'s put some power here", "APPLY CHANGES",
                                     [["None", "700MHZ ARM, 250MHZ CORE, 400MHZ SDRAM, 0 OVERVOLT"],
                                      ["Modest", "800MHZ ARM, 300MHZ CORE, 400MHZ SDRAM, 0 OVERVOLT"],
                                      ["Medium", "900MHZ ARM, 333MHZ CORE, 450MHZ SDRAM, 2 OVERVOLT"],
                                      ["High", "950MHZ ARM, 450MHZ CORE, 450MHZ SDRAM, 6 OVERVOLT"]])
        self.win = win
        self.win.set_main_widget(self)

        # Show the current setting by electing the appropriate radio button
        self.current_setting()
        self.selected_button = self.initial_button
        self.get_button(self.initial_button).set_active(True)

        self.top_bar.enable_prev()
        self.top_bar.set_prev_callback(self.win.go_to_home)

        self.kano_button.connect("button-release-event", self.set_overclock)

        self.win.show_all()

    def set_overclock(self, widget, event):

        #  Mode      arm_freq    core_freq    sdram_freq   over_voltage
        # "None"   "700MHz ARM, 250MHz core, 400MHz SDRAM, 0 overvolt"
        # "Modest" "800MHz ARM, 300MHz core, 400MHz SDRAM, 0 overvolt"
        # "Medium" "900MHz ARM, 333MHz core, 450MHz SDRAM, 2 overvolt"
        # "High"   "950MHz ARM, 450MHz core, 450MHz SDRAM, 6 overvolt"

        # Mode has no changed
        if self.initial_button == self.selected_button:
            return

        config = "High"
        arm_freq = "arm_freq="
        core_freq = "core_freq="
        sdram_freq = "sdram_freq="
        over_voltage = "over_voltage="
        arm_freq_pattern = "arm_freq=[0-9][0-9][0-9]"
        core_freq_pattern = "core_freq=[0-9][0-9][0-9]"
        sdram_freq_pattern = "sdram_freq=[0-9][0-9][0-9]"
        over_voltage_pattern = "over_voltage=[0-9]"
        # None configuration
        if self.selected_button == 0:
            config = "None"
            arm_freq += "700"
            core_freq += "250"
            sdram_freq += "400"
            over_voltage += "0"
        # Modest configuration
        elif self.selected_button == 1:
            config = "Modest"
            arm_freq += "800"
            core_freq += "300"
            sdram_freq += "400"
            over_voltage += "0"
        # Medium configuration
        elif self.selected_button == 2:
            config = "Medium"
            arm_freq += "900"
            core_freq += "333"
            sdram_freq += "450"
            over_voltage += "2"
        # High configuration
        elif self.selected_button == 3:
            config = "High"
            arm_freq += "950"
            core_freq += "450"
            sdram_freq += "450"
            over_voltage += "6"

        logger.info('set_overclock / apply_changes: config:{} arm_freq:{} core_freq:{} sdram_freq:{} over_voltage:{}'.format(
            config, arm_freq, core_freq, sdram_freq, over_voltage))

        # Apply changes
        file_replace(self.boot_config_file, arm_freq_pattern, arm_freq)
        file_replace(self.boot_config_file, core_freq_pattern, core_freq)
        file_replace(self.boot_config_file, sdram_freq_pattern, sdram_freq)
        file_replace(self.boot_config_file, over_voltage_pattern, over_voltage)

        # Update config
        set_setting("Overclocking", config)

        # Tell user to reboot to see changes
        constants.need_reboot = True

    def current_setting(self):
        f = open(self.boot_config_file, 'r')
        file_string = str(f.read())
        none_string = "core_freq=250"
        modest_string = "core_freq=300"
        medium_string = "core_freq=333"
        high_string = "core_freq=450"

        if file_string.find(none_string) != -1:
            self.initial_button = 0
        elif file_string.find(modest_string) != -1:
            self.initial_button = 1
        elif file_string.find(medium_string) != -1:
            self.initial_button = 2
        elif file_string.find(high_string) != -1:
            self.initial_button = 3

    def on_button_toggled(self, button):

        if button.get_active():
            label = button.get_label()
            if label == "None":
                self.selected_button = 0
            elif label == "Modest":
                self.selected_button = 1
            elif label == "Medium":
                self.selected_button = 2
            elif label == "High":
                self.selected_button = 3
