#!/usr/bin/env python

# PasswordScreen.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# This is the screen where the user has chosen a network and needs to enter a
# password for the network.

import os
from gi.repository import Gtk, Gdk

from kano_wifi_gui.paths import img_dir
from kano_settings.components.heading import Heading
from kano.gtk3.buttons import KanoButton
from kano_wifi_gui.Template import Template
from kano_wifi_gui.ConnectToNetwork import ConnectToNetwork


class PasswordScreen(Gtk.Box):
    def __init__(
        self,
        win,
        wiface,
        network_name,
        encryption,
        wrong_password=False
    ):

        '''
        Show the screen with the option of adding a password
        and connecting to a network
        '''

        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self._win = win
        self._win.set_main_widget(self)
        self._win.top_bar.enable_prev()
        self._wiface = wiface
        self._network_name = network_name
        self._encryption = encryption

        # Keep track if the user has already entered the wrong password before
        # so that we only pack the "password incorrect" label once
        self._wrong_password_used_before = False

        self._heading = Heading(
            "Connect to the network",
            self._network_name,
            self._win.is_plug(),
            True
        )

        self._heading.set_prev_callback(self._refresh_networks)
        self._heading.container.set_margin_right(20)
        self._heading.container.set_margin_left(20)

        if wrong_password:
            image_path = os.path.join(img_dir, "password-fail.png")
            wrong_password = self._create_wrong_password_label()
            self._heading.container.pack_start(wrong_password, True, True, 0)
        else:
            image_path = os.path.join(img_dir, "password.png")

        self._padlock_image = Gtk.Image.new_from_file(image_path)

        self._password_entry = Gtk.Entry()
        self._password_entry.set_placeholder_text("Password")
        self._password_entry.set_visibility(False)
        self._password_entry.get_style_context().add_class("password_entry")
        self._password_entry.set_margin_left(60)
        self._password_entry.set_margin_right(60)
        self._password_entry.connect("key-release-event",
                                     self._set_button_sensitive)
        # If Enter key is pressed on the password entry, we want to act as
        # though the connect_btn was clicked
        self._password_entry.connect(
            "key-release-event", self._on_connect_key_wrapper
        )

        self._connect_btn = KanoButton("CONNECT")
        self._connect_btn.connect('clicked', self._on_connect)
        self._connect_btn.set_sensitive(False)
        self._connect_btn.set_margin_right(100)
        self._connect_btn.set_margin_left(100)
        self._connect_btn.pack_and_align()

        self._show_password = Gtk.CheckButton.new_with_label("Show password")
        self._show_password.get_style_context().add_class("show_password")
        self._show_password.connect("toggled",
                                    self._change_password_entry_visiblity)
        self._show_password.set_active(True)
        self._show_password.set_margin_left(100)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        vbox.pack_start(self._heading.container, False, False, 10)
        vbox.pack_start(self._padlock_image, False, False, 10)
        vbox.pack_start(self._password_entry, False, False, 10)
        vbox.pack_start(self._show_password, False, False, 10)
        vbox.pack_end(self._connect_btn.align, False, False, 40)

        # Entry should have the keyboard focus
        self._password_entry.grab_focus()

        self.show_all()

    def _create_wrong_password_label(self):
        label = Gtk.Label("Password incorrect")
        label.get_style_context().add_class("wrong_password_label")
        return label

    def _change_password_entry_visiblity(self, widget):
        '''
        Depending on the checkbox, change the writing in the
        password entry to be readable.
        '''
        visibility = self._show_password.get_active()
        self._password_entry.set_visibility(visibility)

    def _refresh_networks(self, widget=None):
        from kano_wifi_gui.RefreshNetworks import RefreshNetworks
        RefreshNetworks(self._win)

    def _on_connect_key_wrapper(self, widget, event):
        if event.keyval == Gdk.KEY_Return:
            self._on_connect()

    def _on_connect(self, widget=None):
        passphrase = self._password_entry.get_text()
        ConnectToNetwork(
            self._win,
            self._network_name,
            passphrase,
            self._encryption
        )

    def _set_button_sensitive(self, widget, event):
        self._connect_btn.set_sensitive(True)

    def _thread_finish(self, success):

        if success:
            self._success_screen()
        else:
            self._wrong_password_screen()

    def _success_screen(self):
        self._win.remove_main_widget()

        title = "Success!"
        description = "You're connected"
        buttons = [
            {
                "label": "OK",
                "color": "green",
                "type": "KanoButton",
                "callback": Gtk.main_quit
            }
        ]
        img_path = os.path.join(img_dir, "internet.png")

        self._win.set_main_widget(
            Template(
                title,
                description,
                buttons,
                self._win.is_plug(),
                img_path
            )
        )

    def _disable_widgets_start_spinner(self):
        self._connect_btn.start_spinner()
        self._connect_btn.set_sensitive(False)
        self._win.top_bar.prev_button.set_sensitive(False)
        self._password_entry.set_sensitive(False)
        self._show_password.set_sensitive(False)

    def _enable_widgets_stop_spinner(self):
        self._connect_btn.stop_spinner()
        self._connect_btn.set_sensitive(True)
        self._win.top_bar.prev_button.set_sensitive(True)
        self._password_entry.set_sensitive(True)
        self._show_password.set_sensitive(True)
