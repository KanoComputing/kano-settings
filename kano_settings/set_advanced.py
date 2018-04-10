#
# set_advance.py
#
# Copyright (C) 2014-2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#

from gi import require_version
require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk
from kano.gtk3.kano_dialog import KanoDialog
from kano.gtk3.buttons import OrangeButton

from kano import logging
from kano_settings.templates import Template, LabelledListTemplate
from system.advanced import get_parental_enabled, set_parental_enabled, is_ssh_enabled, \
    set_ssh_enabled
from parental_config import ParentalConfig


class SetAdvanced(Template):
    def __init__(self, win):

        Template.__init__(
            self,
            _("Advanced options"),
            _("Toggle parental lock and debug mode"),
            _("APPLY CHANGES"),
            win.is_plug(),
            back_btn=False
        )

        parental_box = self.create_parental_button()
        debug_box = self.create_debug_button()
        ssh_box = self.create_ssh_button()

        self.box.set_spacing(20)
        self.box.pack_start(parental_box, False, False, 0)
        self.box.pack_start(debug_box, False, False, 0)
        self.box.pack_start(ssh_box, False, False, 0)

        self.win = win

        debug_mode = self.get_stored_debug_mode()
        self.ssh_preference = is_ssh_enabled()

        self.parental_button.set_active(get_parental_enabled())
        self.parental_button.connect('clicked', self.go_to_password)
        self.debug_button.set_active(debug_mode)
        self.debug_button.connect('clicked', self.on_debug_toggled)
        self.ssh_button.set_active(self.ssh_preference)
        self.ssh_button.connect('clicked', self.on_ssh_button_clicked)

        self.win.set_main_widget(self)

        # Add the callbacks to the top bar and to the extra back button
        self.set_prev_callback(self.win.go_to_home)
        self.win.change_prev_callback(self.win.go_to_home)
        self.win.top_bar.enable_prev()

        self.kano_button.connect('button-release-event', self.apply_changes)
        self.kano_button.connect('key-release-event', self.apply_changes)
        self.win.show_all()

    def create_parental_button(self):
        desc = (
            _(" Use different levels to:\n"
              "- Block mature content in browser and YouTube\n"
              "- Or restrict internet access to only Kano World activity")
        ).split('\n')

        self.parental_button = Gtk.CheckButton()
        box = LabelledListTemplate.label_button(
            self.parental_button,
            _("Parental lock"),
            desc[0])

        grid = self._labelled_list_helper(desc, box)

        if get_parental_enabled():
            parental_config_button = OrangeButton(_("Configure"))
            parental_config_button.connect('button-press-event',
                                           self.go_to_parental_config)
            grid.attach(parental_config_button, 0, len(desc), 1, 1)

        return grid

    def go_to_parental_config(self, button=None, event=None):
        self.win.clear_win()
        ParentalConfig(self.win)

    def create_debug_button(self):
        desc = (
            _(" Having problems?\n"
              "1) Enable this mode\n"
              "2) Report a bug with the ? tool on the Desktop")
        ).split('\n')
        self.debug_button = Gtk.CheckButton()
        box = LabelledListTemplate.label_button(
            self.debug_button,
            _("Debug mode"),
            desc[0]
        )
        return self._labelled_list_helper(desc, box)

    def create_ssh_button(self):
        desc = (
            _(" Connect securely to your Kano from another computer")
        ).split('\n')
        self.ssh_button = Gtk.CheckButton()
        box = LabelledListTemplate.label_button(
            self.ssh_button,
            _("SSH client"),
            desc[0]
        )
        return self._labelled_list_helper(desc, box)

    def _labelled_list_helper(self, desc, box):
        grid = Gtk.Grid()
        grid.attach(box, 0, 0, 1, 1)

        i = 1

        for text in desc[1:]:
            label = Gtk.Label(text)
            label.set_alignment(xalign=0, yalign=0.5)
            label.set_padding(xpad=25, ypad=0)
            label.get_style_context().add_class('normal_label')
            grid.attach(label, 0, i, 1, 1)
            i = i + 1

        return grid

    def go_to_password(self, event=None):
        self.win.clear_win()
        SetPassword(self.win)

    def apply_changes(self, button, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

            if self.ssh_preference is not is_ssh_enabled():
                set_ssh_enabled(self.ssh_preference)

            old_debug_mode = self.get_stored_debug_mode()
            new_debug_mode = self.debug_button.get_active()
            if new_debug_mode == old_debug_mode:
                logging.Logger().debug('skipping debug mode change')
                self.win.go_to_home()
                return

            if new_debug_mode:
                # set debug on:
                logging.set_system_log_level('debug')
                logging.Logger().info("setting logging to debug")
                msg = _("Activated")
            else:
                # set debug off:
                logging.set_system_log_level('error')
                logging.Logger().info("setting logging to error")
                msg = _("De-activated")

            kdialog = KanoDialog(_("Debug mode"), msg, parent_window=self.win)
            kdialog.run()

            self.kano_button.set_sensitive(False)
            self.win.go_to_home()

    def on_debug_toggled(self, checkbutton):
        self.kano_button.set_sensitive(True)

    def get_stored_debug_mode(self):
        ll = logging.Logger().get_log_level()
        debug_mode = ll == 'debug'
        logging.Logger().debug("stored debug-mode: {}".format(debug_mode))
        return debug_mode

    def on_ssh_button_clicked(self, checkbutton):
        self.ssh_preference = checkbutton.get_active()


class SetPassword(Template):
    def __init__(self, win):

        self.parental_enabled = get_parental_enabled()

        # Entry container
        entry_container = Gtk.Grid(column_homogeneous=False,
                                   column_spacing=22,
                                   row_spacing=10)

        # if enabled, turning off
        if self.parental_enabled:
            Template.__init__(
                self,
                _("Unlock parental lock"),
                _("Enter your password"),
                _("UNLOCK"),
                win.is_plug(),
                True
            )
            self.entry = Gtk.Entry()
            self.entry.set_size_request(300, 44)
            self.entry.props.placeholder_text = _("Enter your selected password")
            self.entry.set_visibility(False)
            self.entry.connect('key_release_event', self.enable_button)
            entry_container.attach(self.entry, 0, 0, 1, 1)

        # if disabled, turning on
        else:
            Template.__init__(
                self,
                _("Set up parental lock"),
                _("Choose a password"),
                _("LOCK"),
                win.is_plug()
            )

            self.entry1 = Gtk.Entry()
            self.entry1.set_size_request(300, 44)
            self.entry1.props.placeholder_text = _("Select password")
            self.entry1.set_visibility(False)

            self.entry2 = Gtk.Entry()
            self.entry2.props.placeholder_text = _("Confirm password")
            self.entry2.set_visibility(False)

            self.entry1.connect('key_release_event', self.enable_button)
            self.entry2.connect('key_release_event', self.enable_button)

            entry_container.attach(self.entry1, 0, 0, 1, 1)
            entry_container.attach(self.entry2, 0, 1, 1, 1)

        self.win = win
        self.win.set_main_widget(self)
        self.set_prev_callback(self.go_to_advanced)
        self.win.change_prev_callback(self.go_to_advanced)
        self.win.top_bar.enable_prev()

        self.kano_button.set_sensitive(False)

        self.kano_button.connect('button-release-event', self.apply_changes)
        self.kano_button.connect('key-release-event', self.apply_changes)

        self.box.add(entry_container)
        self.win.show_all()

    def go_to_advanced(self, widget=None, event=None):
        self.win.clear_win()
        SetAdvanced(self.win)

    def go_to_parental_config(self, button=None, event=None):
        self.win.clear_win()
        ParentalConfig(self.win)

    def apply_changes(self, button, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

            # Disable buttons and entry fields during validation
            # we save the current parental state now because it will flip
            # during this function
            is_locked = self.parental_enabled
            if is_locked:
                self.entry.set_sensitive(False)
                button.set_sensitive(False)
            else:
                self.entry1.set_sensitive(False)
                self.entry2.set_sensitive(False)
                button.set_sensitive(False)

            if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

                password = None

                # if disabled, turning on
                if not self.parental_enabled:
                    password = self.entry1.get_text()
                    password2 = self.entry2.get_text()
                    passed_test = (password == password2)

                # if enabled, turning off
                else:
                    password = self.entry.get_text()
                    passed_test = True

                # if test passed, update parental configuration
                if passed_test:
                    self.update_config(password)

                # else, display try again dialog
                else:
                    do_try_again = self.create_dialog(
                        _("Careful"),
                        _("The passwords don't match! Try again")
                    )
                    if do_try_again:
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
            [
                {
                    'label': _("GO BACK"),
                    'color': 'red',
                    'return_value': False
                },
                {
                    'label': _("TRY AGAIN"),
                    'color': 'green',
                    'return_value': True
                }
            ],
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
            heading = _("Success")
        else:
            heading = _("Error")

        kdialog = KanoDialog(heading, msg, parent_window=self.win)
        kdialog.run()

        # If the user has just turned the parental control on, take them to
        # the config screen.
        if self.parental_enabled:
            self.go_to_parental_config()
        else:
            self.go_to_advanced()
