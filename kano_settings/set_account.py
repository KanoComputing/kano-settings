#!/usr/bin/env python
#
# account.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Controls the UI of the account setting

from gi.repository import Gtk, Gdk, GObject
import threading
import os

from kano.gtk3.heading import Heading
import kano.gtk3.kano_dialog as kano_dialog
from kano.gtk3.buttons import KanoButton
from kano.gtk3.labelled_entries import LabelledEntries

from kano.utils import ensure_dir
import kano_settings.common as common
from kano_settings.templates import Template

from kano_settings.system.account import add_user, delete_user, \
    verify_current_password, change_password, UserError


class SetAccount(Gtk.Box):
    def __init__(self, win):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.win = win
        self.win.set_main_widget(self)

        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.win.go_to_home)

        self.added_or_removed_account = False

        main_heading = Heading(
            "System account settings",
            "Set your account"
        )

        self.pass_button = KanoButton("CHANGE PASSWORD")
        self.pass_button.pack_and_align()
        self.pass_button.connect("button-release-event", self.go_to_password_screen)
        self.pass_button.connect("key-release-event", self.go_to_password_screen)

        self.add_button = KanoButton("ADD ACCOUNT")
        self.add_button.set_size_request(200, 44)
        self.add_button.connect("button-release-event", self.add_account)
        self.add_button.connect("key-release-event", self.add_account)

        self.remove_button = KanoButton("REMOVE ACCOUNT", color="red")
        self.remove_button.set_size_request(200, 44)
        self.remove_button.connect("button-release-event", self.remove_account_dialog)
        self.remove_button.connect("key-release-event", self.remove_account_dialog)

        button_container = Gtk.Box()
        button_container.pack_start(self.add_button, False, False, 10)
        button_container.pack_start(self.remove_button, False, False, 10)

        button_align = Gtk.Alignment(xscale=0, xalign=0.5)
        button_align.add(button_container)

        accounts_heading = Heading(
            "Accounts",
            "Add or remove accounts"
        )

        # Check if we already scheduled an account add or remove
        # We import kano-init locally to avoid circular dependency
        # the packages.
	try:
            from kano_init.utils import is_any_task_scheduled
            if is_any_task_scheduled():
                self.disable_buttons()
        except ImportError:
            self.disable_buttons()

        self.pack_start(main_heading.container, False, False, 0)
        self.pack_start(self.pass_button.align, False, False, 0)
        self.pack_start(accounts_heading.container, False, False, 0)
        self.pack_start(button_align, False, False, 0)

        self.win.show_all()

    def go_to_password_screen(self, widget, event):

        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:
            self.win.clear_win()
            SetPassword(self.win)

    # Gets executed when ADD button is clicked
    def add_account(self, widget=None, event=None):
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:
            kdialog = None

            try:
                # add new user command
                add_user()
            except UserError as e:
                kdialog = kano_dialog.KanoDialog(
                    "Error creating new user",
                    str(e),
                    parent_window=self.win
                )   
            else:
                kdialog = kano_dialog.KanoDialog(
                    "Reboot the system",
                    "A new account will be created next time you reboot.",
                    parent_window=self.win
                )

                # Tell user to reboot to see changes
                common.need_reboot = True

            kdialog.run()
            self.disable_buttons()


    # Gets executed when REMOVE button is clicked
    def remove_account_dialog(self, widget=None, event=None):
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:
            # Bring in message dialog box
            kdialog = kano_dialog.KanoDialog(
                "Are you sure you want to delete the current user?",
                "You will lose all the data on this account!",
                [
                    {
                        'label': "CANCEL",
                        'color': 'red',
                        'return_value': False
                    },
                    {
                        'label': "OK",
                        'color': 'green',
                        'return_value': True
                    }
                ],
                parent_window=self.win
            )
            do_delete_user = kdialog.run()
            if do_delete_user:
                self.disable_buttons()
                try:
                    delete_user()
                except UserError as e:
                    kdialog = kano_dialog.KanoDialog(
                        "Error deleting user",
                        str(e),
                        parent_window=self.win
                    )
                    return
                    

                kdialog = kano_dialog.KanoDialog(
                    "To finish removing this account, you need to reboot",
                    "Do you want to reboot?",
                    [
                        {
                            'label': "LATER",
                            'color': 'grey',
                            'return_value': False
                        },
                        {
                            'label': "REBOOT NOW",
                            'color': 'orange',
                            'return_value': True
                        }
                    ],
                    parent_window=self.win
                )
                do_reboot_now = kdialog.run()
                if do_reboot_now:
                    os.system("sudo reboot")

    # Disables both buttons and makes the temp 'flag' folder
    def disable_buttons(self):

        self.add_button.set_sensitive(False)
        self.remove_button.set_sensitive(False)
        self.added_or_removed_account = True


class SetPassword(Template):
    def __init__(self, win):
        Template.__init__(
            self,
            "Change your password",
            "",
            "CHANGE PASSWORD"
        )

        self.labelled_entries = LabelledEntries(
            [{"heading": "Old password", "subheading": "\"kano\" is default"},
             {"heading": "New password", "subheading": ""},
             {"heading": "Repeat new password", "subheading": ""}]
        )

        self.entry1 = self.labelled_entries.get_entry(0)
        self.entry1.set_size_request(300, 44)
        self.entry1.set_visibility(False)
        self.entry1.props.placeholder_text = "Old password"

        self.entry2 = self.labelled_entries.get_entry(1)
        self.entry2.set_size_request(300, 44)
        self.entry2.set_visibility(False)
        self.entry2.props.placeholder_text = "New password"

        self.entry3 = self.labelled_entries.get_entry(2)
        self.entry3.set_size_request(300, 44)
        self.entry3.set_visibility(False)
        self.entry3.props.placeholder_text = "Repeat new password"

        self.entry1.connect("key_release_event", self.enable_button)
        self.entry2.connect("key_release_event", self.enable_button)
        self.entry3.connect("key_release_event", self.enable_button)

        self.entry1.grab_focus()

        self.win = win
        self.win.set_main_widget(self)

        self.box.pack_start(self.labelled_entries, False, False, 0)

        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.go_to_accounts)

        self.kano_button.set_sensitive(False)
        self.kano_button.connect("button-release-event", self.apply_changes)
        self.kano_button.connect("key-release-event", self.apply_changes)

        self.win.show_all()

    def apply_changes(self, button, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

            # This is a callback called by the main loop, so it's safe to
            # manipulate GTK objects:
            watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
            self.win.get_window().set_cursor(watch_cursor)
            self.kano_button.start_spinner()
            self.kano_button.set_sensitive(False)

            def lengthy_process():
                old_password = self.entry1.get_text()
                new_password1 = self.entry2.get_text()
                new_password2 = self.entry3.get_text()

                success = False
                password_verified = verify_current_password(old_password)

                if not password_verified:
                    title = "Could not change password"
                    description = "Your old password is incorrect!"
                elif new_password1 == new_password2:
                    title, description, success = self.try_change_password(new_password1)
                else:
                    title = "Could not change password"
                    description = "Your new passwords don't match! Try again."

                def done(title, description, success):
                    if success:
                        create_success_dialog(title, description, self.win)
                        do_try_again = False
                    else:
                        do_try_again = create_error_dialog(title, description, self.win)

                    self.win.get_window().set_cursor(None)
                    self.kano_button.stop_spinner()
                    self.clear_text()

                    if not do_try_again:
                        self.go_to_accounts()

                GObject.idle_add(done, title, description, success)

            thread = threading.Thread(target=lengthy_process)
            thread.start()

    # Returns a title, description and whether the process was successful or not
    def try_change_password(self, new_password):
        success = False

        cmdvalue = change_password(new_password)

        # if password is not changed
        if cmdvalue != 0:
            title = "Could not change password"
            description = "Your new password is not long enough or contains special characters."
        else:
            title = "Password changed!"
            description = ""
            success = True

        return (title, description, success)

    def go_to_accounts(self, widget=None, event=None):
        self.win.clear_win()
        SetAccount(self.win)

    def clear_text(self):
        self.entry1.set_text("")
        self.entry2.set_text("")
        self.entry3.set_text("")
        self.entry1.grab_focus()

    def enable_button(self, widget, event):
        text1 = self.entry1.get_text()
        text2 = self.entry2.get_text()
        text3 = self.entry3.get_text()
        self.kano_button.set_sensitive(text1 != "" and text2 != "" and text3 != "")


def create_error_dialog(message1="Could not change password", message2="", win=None):
    kdialog = kano_dialog.KanoDialog(
        message1,
        message2,
        [
            {
                'label': "GO BACK",
                'color': 'red',
                'return_value': False
            },
            {
                'label': "TRY AGAIN",
                'color': 'green',
                'return_value': True
            }
        ],
        parent_window=win
    )

    response = kdialog.run()
    return response


def create_success_dialog(message1, message2, win):
    kdialog = kano_dialog.KanoDialog(
        message1,
        message2,
        parent_window=win
    )
    response = kdialog.run()
    return response
