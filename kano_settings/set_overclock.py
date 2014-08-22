#!/usr/bin/env python

# set_overclock.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gdk
from kano_settings.templates import RadioButtonTemplate
import kano_settings.constants as constants
from kano.logging import logger
from kano_settings.config_file import set_setting
from kano_settings.boot_config import set_config_value, get_config_value
from kano_settings.data import get_data


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

        RadioButtonTemplate.__init__(self, title, description, kano_label,
                                     [[option1, desc1],
                                      [option2, desc2],
                                      [option3, desc3],
                                      [option4, desc4]])
        self.win = win
        self.win.set_main_widget(self)

        # Show the current setting by electing the appropriate radio button
        self.current_setting()
        self.selected_button = self.initial_button
        self.get_button(self.initial_button).set_active(True)

        self.top_bar.enable_prev()
        self.top_bar.set_prev_callback(self.win.go_to_home)

        self.kano_button.connect("button-release-event", self.set_overclock)
        self.kano_button.connect("key-release-event", self.set_overclock)

        self.win.show_all()

    def set_overclock(self, widget, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

            #  Mode      arm_freq    core_freq    sdram_freq   over_voltage
            # "None"   "700MHz ARM, 250MHz core, 400MHz SDRAM, 0 overvolt"
            # "Modest" "800MHz ARM, 300MHz core, 400MHz SDRAM, 0 overvolt"
            # "Medium" "900MHz ARM, 333MHz core, 450MHz SDRAM, 2 overvolt"
            # "High"   "950MHz ARM, 450MHz core, 450MHz SDRAM, 6 overvolt"

            # Mode has no changed
            if self.initial_button == self.selected_button:
                self.win.go_to_home()
                return

            # None configuration
            if self.selected_button == 0:
                config = "None"
                arm_freq = 700
                core_freq = 250
                sdram_freq = 400
                over_voltage = 0
            # Modest configuration
            elif self.selected_button == 1:
                config = "Modest"
                arm_freq = 800
                core_freq = 300
                sdram_freq = 400
                over_voltage = 0
            # Medium configuration
            elif self.selected_button == 2:
                config = "Medium"
                arm_freq = 900
                core_freq = 333
                sdram_freq = 450
                over_voltage = 2
            # High configuration
            elif self.selected_button == 3:
                config = "High"
                arm_freq = 950
                core_freq = 450
                sdram_freq = 450
                over_voltage = 6
            else:
                logger.error('kano-settings: set_overclock: SetOverclock: set_overclock(): ' +
                             'was called with an invalid self.selected_button={}'.format(self.selected_button))
                return

            logger.info('set_overclock / apply_changes: config:{} arm_freq:{} core_freq:{} sdram_freq:{} over_voltage:{}'.format(
                config, arm_freq, core_freq, sdram_freq, over_voltage))

            # Apply changes
            set_config_value("arm_freq", arm_freq)
            set_config_value("core_freq", core_freq)
            set_config_value("sdram_freq", sdram_freq)
            set_config_value("over_voltage", over_voltage)

            # Update config
            set_setting("Overclocking", config)

            # Tell user to reboot to see changes
            constants.need_reboot = True

            self.win.go_to_home()

    def current_setting(self):
        freq = get_config_value('core_freq')

        if freq == 250:
            self.initial_button = 0
        elif freq == 300:
            self.initial_button = 1
        elif freq == 333:
            self.initial_button = 2
        elif freq == 450:
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
