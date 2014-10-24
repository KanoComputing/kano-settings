#!/usr/bin/env python
#
# set_notifications.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Controls the UI of the notification setting

from gi.repository import Gdk
from kano_settings.templates import CheckButtonTemplate
from kano_settings.data import get_data
import kano.notifications as notifications  # enable, disable, allow_world_notifications, disallow_world_notifications


class SetNotifications(CheckButtonTemplate):
    data = get_data("SET_NOTIFICATIONS")

    def __init__(self, win):

        main_title = self.data["LABEL_1"]
        main_description = self.data["LABEL_2"]
        checkbox_desc_1 = self.data["DESCRIPTION_1"]
        checkbox_desc_2 = self.data["DESCRIPTION_2"]
        kano_button_label = self.data["KANO_BUTTON"]

        CheckButtonTemplate.__init__(self, main_title, main_description,
                                     kano_button_label,
                                     [[checkbox_desc_1, ""], [checkbox_desc_2, ""]])

        self.win = win
        self.win.set_main_widget(self)

        self.top_bar.enable_prev()
        self.top_bar.set_prev_callback(self.win.go_to_home)

        self.disable_all_checkbutton = self.get_button(0)
        self.disable_world_checkbutton = self.get_button(1)

        self.kano_button.connect("button-release-event", self.apply_changes)

        self.win.show_all()

    def configure_all_notifications(self):
        if self.disable_all_checkbutton.get_active():
            notifications.disable()
        else:
            notifications.enable()

    def configure_world_notifications(self):
        if self.disable_world_checkbutton.get_active():
            notifications.disallow_world_notifications()
        else:
            notifications.allow_world_notifications()

    def show_configuration(self):
        self.disable_all_checkbutton.set_enabled(not notifications.is_enabled())
        self.disable_world_checkbutton.set_enabled(not notifications.world_notifications_allowed())

    def apply_changes(self, widget, event):
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:
            self.configure_all_notifications()
            self.configure_world_notifications()
            self.win.go_to_home()

