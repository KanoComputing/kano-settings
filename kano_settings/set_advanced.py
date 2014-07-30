#!/usr/bin/env python

# set_advance.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
from kano.gtk3.kano_dialog import KanoDialog
from kano import logging
from kano_settings.templates import CheckButtonTemplate, Template
from advanced.parental import get_parental_enabled, set_parental_enabled


class SetAdvanced(CheckButtonTemplate):

    def __init__(self, win):
        CheckButtonTemplate.__init__(self, "Advanced options", "Toggle parental lock and debug mode", "APPLY CHANGES",
                                     [["Parental lock", "Restrict online content"],
                                      ["Debug mode", "Having problems? Enable this mode and report a bug"]])
        self.set_button_spacing(10)
        self.win = win

        debug_mode = self.get_stored_debug_mode()

        self.parental_button = self.get_button(0)
        self.parental_button.set_active(get_parental_enabled())
        self.parental_button.connect("clicked", self.go_to_password)
        self.debug_button = self.get_button(1)
        self.debug_button.set_active(debug_mode)
        self.debug_button.connect("clicked", self.on_debug_toggled)

        self.win.set_main_widget(self)

        self.top_bar.set_prev_callback(self.win.go_to_home)
        self.top_bar.enable_prev()

        self.kano_button.connect("button-release-event", self.apply_changes)
        self.win.show_all()

    def go_to_password(self, event=None):
        self.win.clear_win()
        SetPassword(self.win)

    def apply_changes(self, button, event):
        old_debug_mode = self.get_stored_debug_mode()
        new_debug_mode = self.debug_button.get_active()
        if new_debug_mode == old_debug_mode:
            logging.Logger().debug('skipping debug mode change')
            return

        if new_debug_mode:
            # set debug on:
            logging.set_system_log_level('debug')
            logging.Logger().info('setting logging to debug')
            msg = "Activated"
        else:
            # set debug off:
            logging.set_system_log_level('error')
            logging.Logger().info('setting logging to error')
            msg = "De-activated"

        kdialog = KanoDialog("Debug mode", msg)
        kdialog.run()

        self.kano_button.set_sensitive(False)
        self.win.go_to_home()

    def on_debug_toggled(self, checkbutton):
        self.kano_button.set_sensitive(True)

    def get_stored_debug_mode(self):
        ll = logging.Logger().get_log_level()
        debug_mode = ll == 'debug'
        logging.Logger().debug('stored debug-mode: {}'.format(debug_mode))
        return debug_mode


class SetPassword(Template):

    def __init__(self, win):

        self.parental_enabled = get_parental_enabled()

        # Entry container
        entry_container = Gtk.Grid(column_homogeneous=False,
                                   column_spacing=22,
                                   row_spacing=10)

        # if enabled, turning off
        if self.parental_enabled:
            Template.__init__(self, "Unlock the parental lock", "Enter your password", "UNLOCK")
            self.entry = Gtk.Entry()
            self.entry.set_size_request(300, 44)
            self.entry.props.placeholder_text = "Enter your selected password"
            self.entry.set_visibility(False)
            self.entry.connect("key_release_event", self.enable_button)
            entry_container.attach(self.entry, 0, 0, 1, 1)

        # if disabled, turning on
        else:
            Template.__init__(self, "Set up your parental lock", "Choose a password", "LOCK")
            self.entry1 = Gtk.Entry()
            self.entry1.set_size_request(300, 44)
            self.entry1.props.placeholder_text = "Select password"
            self.entry1.set_visibility(False)

            self.entry2 = Gtk.Entry()
            self.entry2.props.placeholder_text = "Confirm password"
            self.entry2.set_visibility(False)

            self.entry1.connect("key_release_event", self.enable_button)
            self.entry2.connect("key_release_event", self.enable_button)

            entry_container.attach(self.entry1, 0, 0, 1, 1)
            entry_container.attach(self.entry2, 0, 1, 1, 1)

        self.top_bar.set_prev_callback(self.go_to_advanced)
        self.top_bar.enable_prev()

        self.win = win
        self.win.set_main_widget(self)

        self.kano_button.set_sensitive(False)
        self.kano_button.connect("button-release-event", self.apply_changes)

        self.box.add(entry_container)
        self.win.show_all()

    def go_to_advanced(self, widget=None, event=None):
        self.win.clear_win()
        SetAdvanced(self.win)

    def apply_changes(self, button, event):
        password = None

        # if disabled, turning on
        if not self.parental_enabled:
            password = self.entry1.get_text()
            password2 = self.entry2.get_text()
            passed_test = (password == password2)
            error_heading = "Careful"
            error_description = "The passwords don't match! Try again"

        # if enabled, turning off
        else:
            password = self.entry.get_text()
            passed_test = True

        # if test passed, update parental configuration
        if passed_test:
            self.update_config(password)

        # else, display try again dialog
        else:
            response = self.create_dialog(error_heading, error_description)
            if response == -1:
                if not self.parental_enabled:
                    self.entry1.set_text("")
                    self.entry2.set_text("")
                else:
                    self.entry.set_text("")
            else:
                self.go_to_advanced()

    def create_dialog(self, message1, message2):
        kdialog = KanoDialog(
            message1,
            message2,
            {
                "TRY AGAIN": {
                    "return_value": -1
                },
                "GO BACK": {
                    "return_value": 0,
                    "color": "red"
                }
            }
        )

        response = kdialog.run()
        return response

    def enable_button(self, widget, event):
        # if disabled, turning on
        if not self.parental_enabled:
            text1 = self.entry1.get_text()
            text2 = self.entry2.get_text()
            self.kano_button.set_sensitive(text1 != "" and text2 != "")

        # if enabled, turning off
        else:
            text = self.entry.get_text()
            self.kano_button.set_sensitive(text != "")

    def update_config(self, password):
        if self.parental_enabled:
            success, msg = set_parental_enabled(False, password)
            self.parental_enabled = get_parental_enabled()

        else:
            success, msg = set_parental_enabled(True, password)
            self.parental_enabled = get_parental_enabled()

        if success:
            heading = "Success"
        else:
            heading = "Error"

        kdialog = KanoDialog(heading, msg)
        kdialog.run()

        self.go_to_advanced()
