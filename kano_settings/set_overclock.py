#!/usr/bin/env python

# set_overclock.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gdk

from kano.gtk3.kano_dialog import KanoDialog
from kano.utils.hardware import get_rpi_model

from kano_settings.templates import RadioButtonTemplate
import kano_settings.common as common
from kano_settings.boot_config import get_config_value, end_config_transaction
from kano_settings.system.overclock import change_overclock_value, \
    is_dangerous_overclock_value
from kano_settings.system.boards import get_board_props


class SetOverclock(RadioButtonTemplate):
    selected_button = 0
    initial_button = 0

    def __init__(self, win):
        self._model = get_rpi_model()
        self._board_props = get_board_props(self._model)
        self._board_clocking = self._board_props.CLOCKING

        options = []
        for mode in self._board_clocking['modes']:
            options.append([
                mode,
                "{arm_freq}HZ ARM, "
                "{core_freq}HZ CORE, "
                "{sdram_freq}MHZ SDRAM, "
                "{over_voltage} OVERVOLT"
                .format(**self._board_clocking['values'][mode])
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

            config = self._board_clocking['modes'][self.selected_button]
            change_overclock = True

            if is_dangerous_overclock_value(config, self._model):

                kdialog = KanoDialog(
                    title_text="Warning",
                    description_text=(
                        "For a small percentage of users, this setting makes "
                        "the Pi behave unpredictably. Do you want to "
                        "continue?"
                    ),
                    button_dict=[
                        {
                            'label': "NO",
                            'color': 'red',
                            'return_value': False
                        },
                        {
                            'label': "YES",
                            'color': 'green',
                            'return_value': True
                        }
                    ],
                    parent_window=self.win
                )
                change_overclock = kdialog.run()

            if change_overclock:
                change_overclock_value(config, self._model)

                # Tell user to reboot to see changes
                end_config_transaction()
                common.need_reboot = True

                self.win.go_to_home()

    def current_setting(self):
        # The initial button defaults to zero (above) if the user has
        # selected a different frequency
        freq = get_config_value('arm_freq')

        for mode in self._board_clocking['modes']:
            if self._board_clocking['values'][mode]['arm_freq'] == freq:
                self.initial_button = self._board_clocking['modes'].index(mode)

    def on_button_toggled(self, button, selected):
        if button.get_active():
            self.selected_button = selected
