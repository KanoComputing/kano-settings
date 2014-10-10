#!/usr/bin/env python

# set_notifications.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from kano_settings.data import get_data
from kano_settings.templates import Template


class SetNotifications(Template):
    selected_button = 0
    initial_button = 0

    data = get_data("SET_NOTIFICATIONS")

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

        self.kano_button.connect("button-release-event", self.win.go_to_home)
        self.kano_button.connect("key-release-event", self.win.go_to_home)

        # Refresh window
        self.win.show_all()

    def on_button_toggled(self, button):
        pass
