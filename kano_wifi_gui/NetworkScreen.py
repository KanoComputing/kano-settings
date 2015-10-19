#!/usr/bin/env python

# NetworkScreen.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# This is the screen which shows all the networks detected.

import os
import sys
import threading
from gi.repository import Gtk, GObject, Gdk

from kano_settings.components.heading import Heading
from kano.gtk3.scrolled_window import ScrolledWindow
from kano.gtk3.buttons import KanoButton
from kano_wifi_gui.WhiteButton import WhiteButton
from kano.gtk3.cursor import attach_cursor_events
from kano_wifi_gui.misc import tick_icon
from kano_wifi_gui.paths import img_dir
from kano_wifi_gui.PasswordScreen import PasswordScreen
from kano_wifi_gui.Template import Template
from kano.network import is_connected, disconnect
from kano_wifi_gui.ConnectToNetwork import ConnectToNetwork


class NetworkScreen(Gtk.Box):

    def __init__(self, win, network_list):

        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self._win = win
        self._wiface = self._win.wiface

        # The network that the user selects
        self._selected_network = {}

        # Setting new window here
        self._win.set_main_widget(self)
        self._win.top_bar.disable_prev()

        box = self._create_main_box(network_list)
        self.add(box)

        self._win.show_all()

    def _create_main_box(self, network_list):
        '''Show the screen with the different WiFi networks
        '''

        heading = Heading(
            "Connect to WiFi",
            'Choose a network',
            self._win.is_plug(),
            back_btn=False
        )

        # This box is to pack everything in the window
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # For now, pack the network into a scrolled window
        sw = ScrolledWindow()
        sw.apply_styling_to_widget()
        sw.set_size_request(-1, 215)
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self._network_box = self._create_network_box(network_list)
        sw.add(self._network_box)

        # Pack the scrolled window into an event box to give the illusion of a
        # border
        sw_border = self._add_border_to_widget(sw)
        sw_border.set_margin_right(30)
        sw_border.set_margin_left(30)
        sw_border.set_margin_bottom(20)
        sw_border.set_margin_top(10)

        # Then pack all the elements into the vbox
        vbox.pack_start(heading.container, False, False, 0)
        vbox.pack_start(sw_border, False, False, 0)

        # Pack in the refresh connect buttons
        button_box = self._create_refresh_connect_buttons()
        vbox.pack_end(button_box, False, False, 30)

        return vbox

    def _create_network_box(self, network_list):
        '''Create the box containing the list of networks
        '''
        # Setting up the box in which the network elements are to be positioned
        network_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Are these used anywhere?
        self._network_btns = []
        network_connection = is_connected(self._wiface)

        # The network connection
        network_name = network_connection[0]
        connected = network_connection[3]

        image_path = os.path.join(img_dir, "padlock.png")

        # If the network list is empty, display a message to show it's not
        # broken
        if not len(network_list):
            no_networks_label = Gtk.Label("No networks detected!")
            no_networks_label.get_style_context().add_class('no_networks_label')
            no_networks_label.set_margin_top(80)
            network_box.pack_start(no_networks_label, False, False, 0)
            return network_box

        # Otherwise, pack the networks into the scrolled window
        for network in network_list:

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

            # If the network name of the button matches the last attempted
            # connection, and we're connected to the internet, then
            # put a tick next to the name.

            # TODO: Since connected shows if you're connected to internet
            # you can be connected to ethernet and thus be shown to be
            # connected to the wrong network.
            if network['essid'] == network_name and \
                    connected:
                tick = tick_icon()
                box.pack_start(tick, False, False, 0)

            network_btn.connect(
                "clicked", self._select_network, network, network_connection
            )

            # Add padlock to the items that require a password
            if network['encryption'] != 'off':
                padlock_image = Gtk.Image.new_from_file(image_path)
                box.pack_end(padlock_image, False, False, 0)

            # Pack into the GUI for the networks
            network_box.pack_start(network_btn, False, False, 0)
            self._network_btns.append(network_btn)

        return network_box

    def _add_border_to_widget(self, widget):
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

        # Pack the scrolled window into an event box to give the illusion of a
        # border
        grey_border = Gtk.EventBox()
        grey_border.get_style_context().add_class("grey")
        grey_border.add(white_foreground)

        white_foreground.add(widget)

        return grey_border

    def _create_refresh_connect_buttons(self):
        '''Create the buttons used for the refresh button and the
        to connect to a network, and pack them into a button box.
        Returns the button box.
        '''

        self._connect_btn = KanoButton('CONNECT')
        self._connect_btn.pack_and_align()
        self.connect_handler = self._connect_btn.connect(
            'clicked', self._first_time_connect
        )
        self._connect_btn.set_sensitive(False)
        self._refresh_btn = self._create_refresh_button()

        # For now, show both connect and refresh buttons
        buttonbox = Gtk.ButtonBox()
        buttonbox.set_layout(Gtk.ButtonBoxStyle.CENTER)
        buttonbox.set_spacing(10)
        buttonbox.pack_start(self._refresh_btn, False, False, 0)
        buttonbox.pack_start(self._connect_btn.align, False, False, 0)

        if self._win.is_plug():
            self._skip_btn = WhiteButton("Skip")
            buttonbox.pack_start(self._skip_btn, False, False, 0)
            self._skip_btn.connect("clicked", self.skip)
        else:
            blank_label = Gtk.Label("")
            buttonbox.pack_start(blank_label, False, False, 0)

        return buttonbox

    # Attached to a callback, hence the extra argument
    def skip(self, skip_btn=None):
        # Exit with an extreme exit code so the init-flow knows the user
        # pressed SKIP
        sys.exit(100)

    def _set_connect_btn_status(self, connect=True):
        self._connect_btn.disconnect(self.connect_handler)

        if connect:
            self.connect_handler = self._connect_btn.connect(
                'clicked', self._first_time_connect
            )
            self._connect_btn.set_color("green")
            self._connect_btn.set_label("CONNECT")

        else:
            self.connect_handler = self._connect_btn.connect(
                'clicked', self._launch_disconnect_thread
            )
            self._connect_btn.set_color("red")
            self._connect_btn.set_label("DISCONNECT")

    def _launch_disconnect_thread(self, widget=None):
        watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        self._win.get_window().set_cursor(watch_cursor)
        self._connect_btn.start_spinner()
        self._connect_btn.set_sensitive(False)

        # Force the spinner to show on the window.
        while Gtk.events_pending():
            Gtk.main_iteration()

        t = threading.Thread(target=self._threaded_disconnect)
        t.start()

    def _disconnect_screen(self):
        self._win.remove_main_widget()
        title = "Disconnect complete."
        description = "You're now offline"
        buttons = [
            {
                "label": "CLOSE",
                "type": "KanoButton",
                "color": "red",
                "callback": Gtk.main_quit
            },
            {
                "label": "CONNECT",
                "type": "KanoButton",
                "color": "green",
                "callback": self._go_to_spinner_screen
            }
        ]
        img_path = os.path.join(img_dir, "no-wifi.png")
        self._win.set_main_widget(
            Template(
                title,
                description,
                buttons,
                self._win.is_plug(),
                img_path
            )
        )

    def _threaded_disconnect(self):
        '''
        This is needed so we can show a spinner while the user is
        disconnecting
        '''
        disconnect(self._wiface)

        def done():
            self._disconnect_screen()
            self._win.get_window().set_cursor(None)
            self._connect_btn.stop_spinner()
            self._connect_btn.set_sensitive(True)

        GObject.idle_add(done)

    def _create_refresh_button(self):
        '''Create the refresh button. This it quite involved as you have
        to pack an image into the button which need to change when the
        cursor hovers over it, and change the cursor to be a
        hand over it.
        '''
        refresh_icon_filepath = os.path.join(img_dir, "refresh.png")
        refresh_icon = Gtk.Image.new_from_file(refresh_icon_filepath)
        refresh_btn = Gtk.Button()
        refresh_btn.get_style_context().add_class("refresh_btn")
        refresh_btn.set_image(refresh_icon)
        attach_cursor_events(refresh_btn)

        # These are here in case we want to change the icon on mouse over
        refresh_btn.connect("enter-notify-event", self._set_refresh_hover_icon)
        refresh_btn.connect("leave-notify-event", self._set_refresh_normal_icon)

        refresh_btn.connect('clicked', self._go_to_spinner_screen)
        return refresh_btn

    # This is linked to enter-notify-event, hence the extra arguments
    def _set_refresh_hover_icon(self, widget=None, event=None):
        '''Change the refresh button's icon to the hover icon.
        '''
        selected_path = os.path.join(img_dir, "rescan-hover.png")
        image = Gtk.Image.new_from_file(selected_path)
        self._refresh_btn.set_image(image)

    # This is linked to leave-notify-event, hence the extra arguments
    def _set_refresh_normal_icon(self, widget=None, event=None):
        '''Change the refresh button's icon to the normal icon.
        '''
        unselected_path = os.path.join(img_dir, "refresh.png")
        image = Gtk.Image.new_from_file(unselected_path)
        self._refresh_btn.set_image(image)

    def _first_time_connect(self, widget=None):
        '''Check the selected network.  If a password is needed,
        take the user to the password screen.  Otherwise, try and connect.
        '''
        if self._selected_network['encryption'] == "off":
            essid = self._selected_network['essid']
            encryption = 'off'
            passphrase = ''
            ConnectToNetwork(self._win, essid, passphrase, encryption)
        else:
            self._go_to_password_screen()

    def _go_to_spinner_screen(self, button=None, event=None):
        '''Loading networks and showing the spinner screen.
        '''

        from kano_wifi_gui.RefreshNetworks import RefreshNetworks
        RefreshNetworks(self._win)

    def _go_to_password_screen(self):
        self._win.remove_main_widget()
        PasswordScreen(self._win, self._wiface,
                       self._selected_network["essid"],
                       self._selected_network["encryption"])

    def _select_network(self, button, network, network_connection):
        for network_btn in self._network_btns:
            network_btn.get_style_context().remove_class("selected")

        network_name = network_connection[0]
        connected = network_connection[3]

        self._selected_network = network
        button.get_style_context().add_class("selected")

        # If we are already connected to this network,
        # offer option to disconnect.
        if network['essid'] == network_name and connected:
            self._set_connect_btn_status(connect=False)
        else:
            self._set_connect_btn_status(connect=True)

        self._connect_btn.set_sensitive(True)

    def _disable_widgets_start_spinner(self):
        self._connect_btn.start_spinner()
        self._disable_widgets()

    def _enable_widgets_stop_spinner(self):
        self._connect_btn.stop_spinner()
        self._enable_widgets()

    def _disable_widgets(self):
        self._set_sensitivity_of_buttons(False)

    def _enable_widgets(self):
        self._connect_btn.stop_spinner()
        self._set_sensitivity_of_buttons(True)

    def _set_sensitivity_of_buttons(self, sensitivity):
        self._connect_btn.set_sensitive(sensitivity)
        self._refresh_btn.set_sensitive(sensitivity)

        # Do we want to block this? Or just make sure the application doesn't
        # fall over afterwards
        if hasattr(self, "_skip_btn"):
            # Skip button should be defined
            self._skip_btn.set_sensitive(sensitivity)
