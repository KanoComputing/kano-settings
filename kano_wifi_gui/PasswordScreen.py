#!/usr/bin/env python

# PasswordScreen.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This is the screen where the user has chosen a network and needs to enter a
# password for the network.

import os
import threading
from gi.repository import Gtk, GObject

from kano_wifi_gui.paths import media_dir
from kano.logging import logger
from kano_settings.components.heading import Heading
from kano.gtk3.buttons import KanoButton
from kano.gtk3.kano_dialog import KanoDialog
from kano.network import connect, KwifiCache


class PasswordScreen(Gtk.Box):
    def __init__(self, win, wiface, selected_network, first_attempt=True):
        '''Show the screen with the option of adding a password
        and connecting to a network
        '''

        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.win = win
        self.win.set_main_widget(self)

        self.win.top_bar.enable_prev()
        self.wiface = wiface

        self.selected_network = selected_network
        network_name = self.selected_network['essid']

        heading = Heading(
            "Connect to the network",
            network_name,
            self.win.is_plug()
        )
        heading.set_prev_callback(self.win.go_to_spinner_screen)
        heading.container.set_margin_right(20)
        heading.container.set_margin_left(20)

        # If the user did not enter the correct password the first time,
        # this screen will reload
        if first_attempt:
            image_path = os.path.join(media_dir, "kano-wifi-gui/password.png")
        else:
            image_path = os.path.join(media_dir,
                                      "kano-wifi-gui/password-fail.png")

        self.padlock_image = Gtk.Image.new_from_file(image_path)

        self.password_entry = Gtk.Entry()
        self.password_entry.set_placeholder_text("Password")
        self.password_entry.set_visibility(False)
        self.password_entry.get_style_context().add_class("password_entry")
        self.password_entry.set_margin_left(60)
        self.password_entry.set_margin_right(60)
        self.password_entry.connect("key-release-event",
                                    self.set_button_sensitive)

        # TODO: fix this, this is largely repeated code
        self.connect_btn = KanoButton("CONNECT")
        self.connect_btn.connect('clicked', self.on_connect)
        self.connect_btn.set_sensitive(False)
        self.connect_btn.set_margin_right(100)
        self.connect_btn.set_margin_left(100)
        self.connect_btn.pack_and_align()

        self.show_password = Gtk.CheckButton.new_with_label("Show password")
        self.show_password.get_style_context().add_class("show_password")
        self.show_password.connect("toggled",
                                   self.change_password_entry_visiblity)
        self.show_password.set_active(True)
        self.show_password.set_margin_left(100)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        vbox.pack_start(heading.container, False, False, 10)
        vbox.pack_start(self.padlock_image, False, False, 10)
        vbox.pack_start(self.password_entry, False, False, 10)
        vbox.pack_start(self.show_password, False, False, 10)
        vbox.pack_end(self.connect_btn.align, False, False, 40)

        # Entry should have the keyboard focus
        self.password_entry.grab_focus()

        self.show_all()

    def wrong_password_screen(self):
        '''Change the large padlock image on the screen, clear the password
        entry and bring the text focus to the password entry.
        '''
        image_path = os.path.join(media_dir, "kano-wifi-gui/password-fail.png")
        self.padlock_image.set_from_file(image_path)
        self.password_entry.set_text("")
        self.password_entry.grab_focus()

    def change_password_entry_visiblity(self, widget):
        '''Depending on the checkbox, change the writing in the
        password entry to be readable.
        '''
        visibility = self.show_password.get_active()
        self.password_entry.set_visibility(visibility)

    def go_to_wifi_screen(self, widget=None, event=None):
        from kano_wifi_gui.SpinnerScreen import SpinnerScreen

        self.win.remove_main_widget()
        SpinnerScreen(self.win, self.wiface)

    # TODO: This is largely repeated code
    def on_connect(self, widget):
        '''This is the cb attached to the button widget
        '''
        essid = self.selected_network['essid']
        passphrase = self.password_entry.get_text()
        wpa = self.selected_network['encryption']
        self._connect_(essid, passphrase, wpa)

    def _connect_(self, ssid, passphrase, encryption):
        '''This starts the _connect_thread_ thread
        '''
        logger.debug('Connecting to {}'.format(ssid))

        # disable the buttons
        self._disable_widgets()
        self.connect_btn.start_spinner()

        # start thread
        t = threading.Thread(
            target=self._connect_thread_,
            args=(ssid, encryption, passphrase,)
        )

        t.daemon = False
        t.start()

    def _connect_thread_(self, ssid, encryption, passphrase):
        '''This function runs in a thread so we can run a spinner alongside.
        '''
        success = connect(self.wiface, ssid, encryption, passphrase)

        # save the connection in cache so it reconnects on next system boot
        wificache = KwifiCache()
        if success:
            wificache.save(ssid, encryption, passphrase)
        else:
            wificache.empty()

        logger.debug(
            'Connecting to {} {} {}. Successful: {}'.format(
                ssid, encryption, passphrase, success
            )
        )
        GObject.idle_add(self._thread_finish, success)

    def set_button_sensitive(self, widget, event):
        self.connect_btn.set_sensitive(True)

    def _thread_finish(self, success):
        self.connect_btn.stop_spinner()
        self._enable_widgets()

        if success:
            kdialog = KanoDialog(
                "Excellent, you're connected!",
                "You can talk to the world",
                parent_window=self.win
            )
            kdialog.run()
            Gtk.main_quit()

        else:
            self.wrong_password_screen()

    def _disable_widgets(self):
        self.connect_btn.set_sensitive(False)
        self.win.top_bar.prev_button.set_sensitive(False)
        self.password_entry.set_sensitive(False)
        self.show_password.set_sensitive(False)

    def _enable_widgets(self):
        self.connect_btn.set_sensitive(True)
        self.win.top_bar.prev_button.set_sensitive(True)
        self.password_entry.set_sensitive(True)
        self.show_password.set_sensitive(True)
