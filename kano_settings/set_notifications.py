#!/usr/bin/env python
#
# set_notifications.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Controls the UI of the notification setting
# Check result with display_generic_notification function in kano.notifications


from gi.repository import Gdk, Gtk

import kano.notifications as notifications
from kano.utils import run_bg, is_model_2_b

from kano_settings.templates import RadioButtonTemplate
from kano_settings.config_file import get_setting, set_setting


class SetNotifications(RadioButtonTemplate):
    def __init__(self, win):
        RadioButtonTemplate.__init__(
            self,
            "Notifications",
            "Here you can manage the built-in notification system",
            "APPLY CHANGES",
            [
                ["Show all notifications", ""],
                ["Hide all notifications", ""],
                ["Hide only Kano World notifications", ""]
            ]
        )

        self.win = win
        self.win.set_main_widget(self)

        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.win.go_to_home)

        self.enable_all_radiobutton = self.get_button(0)
        self.disable_all_radiobutton = self.get_button(1)
        self.disable_world_radiobutton = self.get_button(2)

        if is_model_2_b():
            self.cpu_monitor_checkbox = Gtk.CheckButton()

            self.buttons.append(self.cpu_monitor_checkbox)
            self.label_button_and_pack(
                self.cpu_monitor_checkbox,
                'Enable LED Speaker CPU Animation', ''
            )

        self.kano_button.connect("button-release-event", self.apply_changes)

        self.show_configuration()
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

    def configure_cpu_monitor_animation(self, checkbox=None):
        is_ticked = self.cpu_monitor_checkbox.get_active()
        was_enabled = get_setting('LED-Speaker-anim')

        if is_ticked and not was_enabled:
            set_setting('LED-Speaker-anim', is_ticked)
            run_bg('kano-speakerleds cpu-monitor start', unsudo=True)
        elif was_enabled and not is_ticked:
            set_setting('LED-Speaker-anim', is_ticked)
            run_bg('kano-speakerleds cpu-monitor stop', unsudo=True)

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
        self.cpu_monitor_checkbox.set_active(get_setting('LED-Speaker-anim'))

    def apply_changes(self, widget, event):
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:
            self.configure_all_notifications()
            self.configure_world_notifications()
            self.configure_cpu_monitor_animation()
            self.win.go_to_home()
