#!/usr/bin/env python

# set_font.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from kano.utils import get_user_unsudoed
from kano_settings.templates import RadioButtonTemplate
from kano.logging import logger
from .config_file import get_setting, set_setting, file_replace
from kano_settings.data import get_data

selected_button = 0
initial_button = 0

SIZE_SMALL = 10
SIZE_NORMAL = 14
SIZE_BIG = 18

username = get_user_unsudoed()
config_file = os.path.join('/home', username, '.config/lxsession/LXDE/desktop.conf')


class SetFont(RadioButtonTemplate):
    selected_button = 0
    initial_button = 0

    data = get_data("SET_FONT")

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

        RadioButtonTemplate.__init__(self, title, description, kano_label,
                                     [[option1, desc1],
                                      [option2, desc2],
                                      [option3, desc3]])

        self.win = win
        self.win.set_main_widget(self)

        self.top_bar.enable_prev()
        self.top_bar.set_prev_callback(self.win.go_to_home)

        # Show the current setting by electing the appropriate radio button
        self.current_setting()
        self.selected_button = self.initial_button
        self.get_button(self.initial_button).set_active(True)

        self.kano_button.connect("button-release-event", self.change_font)
        self.win.show_all()

    def change_font(self, widget, event):

        #  Mode   size
        # Small    SIZE_SMALL
        # Normal   SIZE_NORMAL
        # Big      SIZE_BIG

        # Mode has no changed
        if self.initial_button == self.selected_button:
            self.win.go_to_home()
            return

        config = "Small"
        # Slow configuration
        if self.selected_button == 0:
            config = "Small"
        # Modest configuration
        elif self.selected_button == 1:
            config = "Normal"
        # Medium configuration
        elif self.selected_button == 2:
            config = "Big"

        # Update config
        set_setting("Font", config)

        self.win.go_to_home()

    def change_font_size(self):

        font = "sGtk/FontName=Bariol "
        font_pattern = font + "[0-9][0-9]"

        # Small configuration
        if self.selected_button == 0:
            font += str(SIZE_SMALL)
        # Normal configuration
        elif self.selected_button == 1:
            font += str(SIZE_NORMAL)
        # Big configurations
        elif self.selected_button == 2:
            font += str(SIZE_BIG)

        logger.debug('set_font / change_font_size: selected_button:{}'.format(selected_button))

        # Apply changes
        file_replace(config_file, font_pattern, font)
        # Reload lxsession
        os.system("lxsession -r")

    def current_setting(self):

        font = get_setting("Font")
        if font == "Small":
            self.initial_button = 0
        elif font == "Normal":
            self.initial_button = 1
        elif font == "Big":
            self.initial_button = 2

    def on_button_toggled(self, button):
        if button.get_active():
            label = button.get_label()
            if label == "Small":
                self.selected_button = 0
            elif label == "Normal":
                self.selected_button = 1
            elif label == "Big":
                self.selected_button = 2

            # Apply changes so speed can be tested
            self.change_font_size()
