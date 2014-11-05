#!/usr/bin/env python
#
# set_notifications.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Controls the UI of the notification setting
# Check result with display_generic_notification function in kano.notifications

from gi.repository import Gdk
from kano_settings.templates import RadioButtonTemplate
from kano_settings.data import get_data
import kano.notifications as notifications


class SetNotifications(RadioButtonTemplate):
    data = get_data("SET_NOTIFICATIONS")

    def __init__(self, win):

        main_title = self.data["LABEL_1"]
        main_description = self.data["LABEL_2"]
        radiobox_desc_1 = self.data["DESCRIPTION_1"]
        radiobox_desc_2 = self.data["DESCRIPTION_2"]
        radiobox_desc_3 = self.data["DESCRIPTION_3"]
        kano_button_label = self.data["KANO_BUTTON"]

        RadioButtonTemplate.__init__(self, main_title, main_description,
                                     kano_button_label,
                                     [[radiobox_desc_1, ""],
                                      [radiobox_desc_2, ""],
                                      [radiobox_desc_3, ""]])

        self.win = win
        self.win.set_main_widget(self)

        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.win.go_to_home)

        self.enable_all_radiobutton = self.get_button(0)
        self.disable_all_radiobutton = self.get_button(1)
        self.disable_world_radiobutton = self.get_button(2)
        self.show_configuration()

        self.kano_button.connect("button-release-event", self.apply_changes)

        self.win.show_all()

    def configure_all_notifications(self):
        if self.disable_all_radiobutton.get_active():
            notifications.disable()
        else:
            notifications.enable()

    def configure_world_notifications(self):
        if self.disable_world_radiobutton.get_active():
            notifications.disallow_world_notifications()
        else:
            notifications.allow_world_notifications()

    def show_configuration(self):
        enable_all = False
        disable_all = False
        disable_world = False

        if not notifications.is_enabled():
            disable_all = True
        elif not notifications.world_notifications_allowed():
            disable_world = True
        else:
            enable_all = True

        self.disable_world_radiobutton.set_active(disable_world)
        self.enable_all_radiobutton.set_active(enable_all)
        self.disable_all_radiobutton.set_active(disable_all)

    def apply_changes(self, widget, event):
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:
            self.configure_all_notifications()
            self.configure_world_notifications()
            self.win.go_to_home()
