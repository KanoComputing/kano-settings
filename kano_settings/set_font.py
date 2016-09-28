#!/usr/bin/env python

# set_font.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gdk
import os
from kano.utils import get_user_unsudoed
from kano_settings.templates import RadioButtonTemplate
from .config_file import get_setting, set_setting
from kano_settings.system.font import change_font_size

selected_button = 0
initial_button = 0

username = get_user_unsudoed()
config_file = os.path.join('/home', username, '.config/lxsession/LXDE/desktop.conf')


MODES = [_("Small"), _("Normal"), _("Big")]


class SetFont(RadioButtonTemplate):
    selected_button = 0
    initial_button = 0

    def __init__(self, win):
        RadioButtonTemplate.__init__(
            self,
            _("Font"),
            _("Choose a comfortable text size"),
            _("APPLY CHANGES"),
            [
                [_("Small"), _("BETTER FOR SMALL SCREENS")],
                [_("Normal"), _("DEFAULT")],
                [_("Big"), _("BETTER FOR BIG SCREENS")]
            ]
        )

        self.win = win
        self.win.set_main_widget(self)

        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.reset_and_go_home)

        # Show the current setting by electing the appropriate radio button
        try:
            self.initial_button = MODES.index(get_setting('Font'))
        except ValueError:
            self.initial_button = 0

        self.selected_button = self.initial_button
        self.get_button(self.initial_button).set_active(True)

        self.kano_button.connect('clicked', self.change_font)
        self.win.show_all()

    def reset_and_go_home(self, widget=None, event=None):
        change_font_size(self.initial_button)
        self.win.go_to_home()

    def change_font(self, button):
        try:
            config = MODES[self.selected_button]
        except IndexError:
            config = _("Normal")

        if not config == get_setting('Font'):
            set_setting('Font', config)
        self.win.go_to_home()

    def on_button_toggled(self, button, selected):
        if button.get_active():
            self.selected_button = selected
            # Apply changes so font can be tested
            change_font_size(selected)
