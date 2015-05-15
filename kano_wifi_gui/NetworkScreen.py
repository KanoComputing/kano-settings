#!/usr/bin/env python

# NetworkScreen.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# This is the screen which shows all the networks detected.

import os
import threading
from gi.repository import Gtk, GObject, Gdk

from kano.gtk3.heading import Heading
from kano.gtk3.scrolled_window import ScrolledWindow
from kano.gtk3.buttons import KanoButton
from kano.gtk3.kano_dialog import KanoDialog
from kano.gtk3.cursor import attach_cursor_events
from kano_wifi_gui.misc import tick_icon
from kano.logging import logger
from kano_wifi_gui.paths import media_dir
from kano_wifi_gui.PasswordScreen import PasswordScreen
from kano.network import (connect, is_connected, KwifiCache, disconnect,
                          is_internet, network_info)


def disconnect_dialog(wiface='wlan0', win=None):
    disconnect(wiface)
    kdialog = KanoDialog(
        # Text from the content team.
        "Disconnect complete - you're now offline.",
        parent_window=win
    )
    kdialog.run()


class NetworkScreen(Gtk.Box):

    def __init__(self, win, _wiface, network_list):

        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.win = win
        self.wiface = _wiface
        self.set_size_request(self.win.width, self.win.height)

        # Setting new window here
        self.win.set_main_widget(self)

        # This could cause problems
        self.network_list = network_list
        self.win.top_bar.disable_prev()

        self.width = 350
        self.height = 405

        # Find out if connected to wireless, ethernet or not at all
        # This determines the variable self.connection, which tells us
        # the current internet connection.
        has_internet = is_internet()

        if has_internet:
            network_info_dict = network_info()
            network = network_info_dict.keys()[0]
            network_name = network_info_dict[network]["nice_name"]

            if network_name.upper() != "ETHERNET":
                self.connection = "WIFI"
            else:
                self.connection = "ETHERNET"
        else:
            self.connection = "DISCONNECTED"

        box = self.create_box()
        self.add(box)

        self.win.show_all()

    def create_network_box(self):
        '''Create the box containing the list of networks
        '''
        # Setting up the box in which the network elements are to be positioned
        self.network_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._pack_networks()

    def _pack_networks(self):
        '''Display the networks on buttons that the user can select.
        Pack these buttons into a grid networks into a box.
        '''

        self.network_btns = []
        network_connection = is_connected(self.wiface)

        image_path = os.path.join(media_dir,
                                  "kano-wifi-gui/padlock.png")

        # If the network list is empty, display a message to show it's not
        # broken
        if not len(self.network_list):
            no_networks_label = Gtk.Label("No networks detected!")
            no_networks_label.get_style_context().add_class('no_networks_label')
            no_networks_label.set_margin_top(80)
            self.network_box.pack_start(no_networks_label, False, False, 0)
            self.show_all()
            return

        # Otherwise, pack the networks into the scrolled window
        for network in self.network_list:

            # Network selection must be able to receive events
            network_btn = Gtk.Button()

            # Needs a box packed into it for the label and possibly
            # an icon
            box = Gtk.Box()
            network_btn.add(box)
            network_btn.get_style_context().add_class("network_btn")
            attach_cursor_events(network_btn)

            # Box must contain label of the network name
            label = Gtk.Label(network['essid'])
            box.pack_start(label, False, False, 0)

            if network['essid'] == network_connection[0]:
                tick = tick_icon()
                box.pack_start(tick, False, False, 0)

            network_btn.connect(
                "clicked", self._select_network, network, network_connection
            )

            # Add padlock to the
            if network['encryption'] != 'off':
                padlock_image = Gtk.Image.new_from_file(image_path)
                box.pack_end(padlock_image, False, False, 0)

            # Pack into the GUI for the networks
            self.network_box.pack_start(network_btn, False, False, 0)
            self.network_btns.append(network_btn)

        self.show_all()

    def create_box(self):
        '''Show the screen with the different wifi networks
        '''

        self.selected_network = {}
        self.heading = Heading("Connect to WiFi", 'Choose a network')
        self.create_network_box()

        # This box is to pack everything in the window
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # For now, pack the network into a scrolled window
        sw = ScrolledWindow()
        sw.apply_styling_to_widget()
        sw.set_size_request(-1, 215)
        sw.add(self.network_box)
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Pack the scrolled window into an event box to give the illusion of a
        # border
        sw_border = self.add_border_to_widget(sw)
        sw_border.set_margin_right(30)
        sw_border.set_margin_left(30)
        sw_border.set_margin_bottom(20)
        sw_border.set_margin_top(10)

        # Then pack all the elements into the vbox
        vbox.pack_start(self.heading.container, False, False, 0)
        vbox.pack_start(sw_border, False, False, 0)

        # Pack in the refresh connect buttons
        button_box = self.create_refresh_connect_buttons()
        vbox.pack_end(button_box, False, False, 30)

        return vbox

    def add_border_to_widget(self, widget):
        '''Add a grey border to the widget that is entered as an argument.
        This is done by creating a grey event box and packing a white box with
        a margin in it.
        '''

        white_foreground = Gtk.EventBox()
        white_foreground.get_style_context().add_class("white")
        white_foreground.set_margin_left(3)
        white_foreground.set_margin_bottom(3)
        white_foreground.set_margin_top(3)
        white_foreground.set_margin_right(3)

        # Pack the scrolled window into an event box to give the illusion of a border
        grey_border = Gtk.EventBox()
        grey_border.get_style_context().add_class("grey")
        grey_border.add(white_foreground)

        white_foreground.add(widget)

        return grey_border

    def create_refresh_connect_buttons(self):
        '''Create the buttons used for the refresh button and the
        to connect to a network, and pack them into a button box.
        Returns the button box.
        '''

        self.connect_btn = KanoButton('CONNECT')
        self.connect_handler = self.connect_btn.connect('clicked', self.first_time_connect)
        self.connect_btn.set_sensitive(False)
        self.refresh_btn = self.create_refresh_button()

        # For now, show both connect and refresh buttons
        buttonbox = Gtk.ButtonBox()
        buttonbox.set_layout(Gtk.ButtonBoxStyle.CENTER)
        buttonbox.set_spacing(10)
        buttonbox.pack_start(self.refresh_btn, False, False, 0)
        buttonbox.pack_start(self.connect_btn, False, False, 0)

        blank_label = Gtk.Label("")
        buttonbox.pack_start(blank_label, False, False, 0)

        return buttonbox

    def set_connect_btn_status(self, connect=True):
        self.connect_btn.disconnect(self.connect_handler)

        if connect:
            self.connect_handler = self.connect_btn.connect(
                'clicked', self.first_time_connect
            )
            self.connect_btn.set_color("green")
            self.connect_btn.set_label("CONNECT")
        else:
            self.connect_handler = self.connect_btn.connect(
                'clicked', self.launch_disconnect_dialog
            )
            self.connect_btn.set_color("red")
            self.connect_btn.set_label("DISCONNECT")

    def launch_disconnect_dialog(self, widget=None):
        watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        self.win.get_window().set_cursor(watch_cursor)
        self.connect_btn.start_spinner()
        self.connect_btn.set_sensitive(False)

        # Force the spinner to show on the window.
        while Gtk.events_pending():
            Gtk.main_iteration()

        t = threading.Thread(target=self.threaded_disconnect)
        t.start()

    def threaded_disconnect(self):
        '''This is needed so we can show a spinner while the user is
        disconnecting
        '''
        disconnect(self.wiface)

        def done():
            kdialog = KanoDialog(
                # Text from the content team.
                "Disconnect complete - you're now offline.",
                parent_window=self.win
            )
            kdialog.run()

            self.win.get_window().set_cursor(None)
            self.connect_btn.stop_spinner()
            self.connect_btn.set_sensitive(True)
            self.go_to_spinner_screen()

        GObject.idle_add(done)

    def create_refresh_button(self):
        '''Create the refresh button. This it quite involved as you have
        to pack an image into the button which need to change when the
        cursor hovers over it, and change the cursor to be a
        hand over it.
        '''
        refresh_icon_filepath = os.path.join(
            media_dir, "kano-wifi-gui/refresh.png"
        )
        refresh_icon = Gtk.Image.new_from_file(refresh_icon_filepath)
        refresh_btn = Gtk.Button()
        refresh_btn.get_style_context().add_class("refresh_btn")
        refresh_btn.set_image(refresh_icon)
        attach_cursor_events(refresh_btn)

        # These are here in case we want to change the icon on mouse over
        refresh_btn.connect("enter-notify-event", self.set_hover_icon)
        refresh_btn.connect("leave-notify-event", self.set_normal_icon)

        refresh_btn.connect('clicked', self.go_to_spinner_screen)
        return refresh_btn

    # This is linked to enter-notify-event, hence the extra arguments
    def set_hover_icon(self, widget=None, event=None):
        '''Change the refresh button's icon to the hover icon.
        '''
        selected_path = os.path.join(media_dir, "kano-wifi-gui/rescan-hover.png")
        image = Gtk.Image.new_from_file(selected_path)
        self.refresh_btn.set_image(image)

    # This is linked to leave-notify-event, hence the extra arguments
    def set_normal_icon(self, widget=None, event=None):
        '''Change the refresh button's icon to the norma icon.
        '''
        unselected_path = os.path.join(media_dir, "kano-wifi-gui/refresh.png")
        image = Gtk.Image.new_from_file(unselected_path)
        self.refresh_btn.set_image(image)

    def first_time_connect(self, widget=None):
        '''Check the selected network.  If a password is needed,
        take the user to the password screen.  Otherwise, try and connect.
        '''
        if self.selected_network['encryption'] == "off":
            essid = self.selected_network['essid']
            encryption = 'off'
            passphrase = ''
            self._connect_(essid, passphrase, encryption)
        else:
            self.go_to_password_screen()

    def go_to_spinner_screen(self, button=None, event=None):
        '''Loading networks and showing the spinner screen.
        '''
        from kano_wifi_gui.SpinnerScreen import SpinnerScreen

        self.win.remove_main_widget()
        SpinnerScreen(self.win, self.wiface)

    def _unpack_networks(self):
        for child in self.network_box.get_children():
            self.network_box.remove(child)

    def go_to_password_screen(self):
        self.win.remove_main_widget()
        PasswordScreen(self.win, self.wiface, self.selected_network)

    def _select_network(self, button, network, network_connection=None):
        for network_btn in self.network_btns:
            network_btn.get_style_context().remove_class("selected")

        self.selected_network = network
        button.get_style_context().add_class("selected")

        # If we are already connected to this network,
        # offer option to disconnect.
        if network['essid'] == network_connection[0]:
            self.set_connect_btn_status(connect=False)
        else:
            self.set_connect_btn_status(connect=True)

        self.connect_btn.set_sensitive(True)

    def on_connect(self, widget, entry):
        '''This is the cb attached to the button widget
        '''
        essid = self.selected_network['essid']
        passphrase = entry.get_text()
        wpa = self.selected_network['encryption']
        self._connect_(essid, passphrase, wpa)

    def _connect_(self, ssid, passphrase, encryption):
        '''This starts the _connect_thread_ thread
        '''
        logger.debug('Connecting to {}'.format(ssid))
        # disable the buttons
        self.refresh_btn.set_sensitive(False)
        self.connect_btn.set_sensitive(False)
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

        logger.debug('Connecting to {} {} {}. Successful: {}'.format(
            ssid, encryption, passphrase, success)
        )
        GObject.idle_add(self._thread_finish, success)

    def _thread_finish(self, success):
        '''When the thread finishes, stop the spinner, enable the buttons
        and launch a dialog with an appropriate message depending on whether
        the user successfully connected to the internet.
        '''
        self.connect_btn.stop_spinner()
        self.connect_btn.set_sensitive(True)
        self.refresh_btn.set_sensitive(True)

        if success:
            kdialog = KanoDialog(
                "Excellent, you're connected!",
                "You can talk to the world",
                parent_window=self.win
            )
            kdialog.run()
            Gtk.main_quit()

        else:
            kdialog = KanoDialog(
                "Cannot connect!",
                "Maybe the signal was too weak to connect.",
                parent_window=self.win
            )
            self.win.remove_main_widget()
            NetworkScreen(
                self.win, self.wiface,
                self.selected_network,
                first_attempt=False
            )
