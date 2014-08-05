#!/usr/bin/env python

# set_advance.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
from kano.gtk3.kano_dialog import KanoDialog

from kano import logging
from kano_settings.templates import Template, LabelledListTemplate
from advanced.parental import get_parental_enabled, set_parental_enabled

from kano_settings.data import get_data


class SetAdvanced(Template):
    data = get_data("SET_ADVANCED")

    def __init__(self, win):

        title = self.data["LABEL_1"]
        description = self.data["LABEL_2"]
        kano_label = self.data["KANO_BUTTON"]

        Template.__init__(self, title, description, kano_label)

        parental_box = self.create_parental_button()
        debug_box = self.create_debug_button()

        self.box.set_spacing(20)
        self.box.pack_start(parental_box, False, False, 0)
        self.box.pack_start(debug_box, False, False, 0)

        self.win = win

        debug_mode = self.get_stored_debug_mode()

        self.parental_button.set_active(get_parental_enabled())
        self.parental_button.connect("clicked", self.go_to_password)
        self.debug_button.set_active(debug_mode)
        self.debug_button.connect("clicked", self.on_debug_toggled)

        self.win.set_main_widget(self)

        self.top_bar.set_prev_callback(self.win.go_to_home)
        self.top_bar.enable_prev()

        self.kano_button.connect("button-release-event", self.apply_changes)
        self.win.show_all()

    def create_parental_button(self):
        title = self.data["OPTION_1"]
        desc_1 = self.data["DESCRIPTION_1_1"]
        desc_2 = self.data["DESCRIPTION_1_2"]
        desc_3 = self.data["DESCRIPTION_1_3"]
        self.parental_button = Gtk.CheckButton()
        box = LabelledListTemplate.label_button(self.parental_button,
                                                title, desc_1)

        text_array = [desc_2, desc_3]

        grid = Gtk.Grid()
        grid.attach(box, 0, 0, 1, 1)

        i = 1

        for text in text_array:
            label = Gtk.Label(text)
            label.set_alignment(xalign=0, yalign=0.5)
            label.set_padding(xpad=25, ypad=0)
            label.get_style_context().add_class("normal_label")
            grid.attach(label, 0, i, 1, 1)
            i = i + 1

        return grid

    def create_debug_button(self):
        title = self.data["OPTION_2"]
        desc_1 = self.data["DESCRIPTION_2_1"]
        self.debug_button = Gtk.CheckButton()
        box = LabelledListTemplate.label_button(self.debug_button, title,
                                                desc_1)

        return box

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

        kdialog = KanoDialog("Debug mode", msg, parent_window=self.win)
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
    data_lock = get_data("PARENTAL_LOCK")
    data_unlock = get_data("PARENTAL_UNLOCK")

    def __init__(self, win):

        self.parental_enabled = get_parental_enabled()

        # Entry container
        entry_container = Gtk.Grid(column_homogeneous=False,
                                   column_spacing=22,
                                   row_spacing=10)

        # if enabled, turning off
        if self.parental_enabled:
            title = self.data_unlock["LABEL_1"]
            description = self.data_unlock["LABEL_2"]
            kano_label = self.data_unlock["KANO_BUTTON"]
            placeholder_1 = self.data_lock["PLACEHOLDER_1"]

            Template.__init__(self, title, description, kano_label)
            self.entry = Gtk.Entry()
            self.entry.set_size_request(300, 44)
            self.entry.props.placeholder_text = placeholder_1
            self.entry.set_visibility(False)
            self.entry.connect("key_release_event", self.enable_button)
            entry_container.attach(self.entry, 0, 0, 1, 1)

        # if disabled, turning on
        else:
            title = self.data_lock["LABEL_1"]
            description = self.data_lock["LABEL_2"]
            kano_label = self.data_lock["KANO_BUTTON"]
            placeholder_1 = self.data_lock["PLACEHOLDER_1"]
            placeholder_2 = self.data_lock["PLACEHOLDER_2"]

            Template.__init__(self, title, description, kano_label)
            self.entry1 = Gtk.Entry()
            self.entry1.set_size_request(300, 44)
            self.entry1.props.placeholder_text = placeholder_1
            self.entry1.set_visibility(False)

            self.entry2 = Gtk.Entry()
            self.entry2.props.placeholder_text = placeholder_2
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
        self.kano_button.connect("key-release-event", self.apply_changes)

        self.box.add(entry_container)
        self.win.show_all()

    def go_to_advanced(self, widget=None, event=None):
        self.win.clear_win()
        SetAdvanced(self.win)

    def apply_changes(self, button, event):
        # Disable buttons and entry fields during validation
        # we save the current parental state now because it will flip during this function
        is_locked = self.parental_enabled
        if is_locked:
            self.entry.set_sensitive(False)
            button.set_sensitive(False)
        else:
            self.entry1.set_sensitive(False)
            self.entry2.set_sensitive(False)
            button.set_sensitive(False)

        if not hasattr(event, 'keyval') or event.keyval == 65293:

            password = None

            # if disabled, turning on
            if not self.parental_enabled:
                password = self.entry1.get_text()
                password2 = self.entry2.get_text()
                passed_test = (password == password2)
                error_heading = self.data_lock["ERROR_LABEL_1"]
                error_description = self.data_lock["ERROR_LABEL_2"]

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

        # Restore the UI controls (re-enable input focus)
        if is_locked:
            self.entry.set_sensitive(True)
            button.set_sensitive(True)
        else:
            self.entry1.set_sensitive(True)
            self.entry2.set_sensitive(True)

            # For new password input dialog (2 entry fields) the lock button
            # will be enabled only after the user enters text
            # in both password fields (self.enable_button)
            button.set_sensitive(False)

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
            },
            parent_window=self.win
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

        kdialog = KanoDialog(heading, msg, parent_window=self.win)
        kdialog.run()

        self.go_to_advanced()
