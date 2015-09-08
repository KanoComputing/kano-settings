#!/usr/bin/env python

# SpinnerScreen.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import os
import threading
from gi.repository import Gtk, GObject, GdkPixbuf

from kano_settings.components.heading import Heading
from kano.network import IWList
from kano_wifi_gui.paths import media_dir
from kano_wifi_gui.NetworkScreen import NetworkScreen


class SpinnerScreen(Gtk.Box):

    # wiface is only here to pass onto the ConnectWifi screen
    def __init__(self, win, wiface):

        self.win = win
        self.win.top_bar.disable_prev()
        self.wiface = wiface
        self.show_spinner_screen_while_loading()

    def show_spinner_screen_while_loading(self):

        self.show_spinner_screen()

        # check the wifi networks present here
        t = threading.Thread(target=self.scan_networks)
        t.start()

    def show_spinner_screen(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.set_size_request(self.win.width, self.win.height)

        self.win.set_main_widget(self)

        title = Heading("Searching for networks", "Any minute now")
        self.pack_start(title.container, False, False, 0)

        spinner = Gtk.Image()

        if self.win.is_plug():
            filename = os.path.join(media_dir, "kano-wifi-gui/loading_bar.gif")
        else:
            filename = os.path.join(media_dir, "kano-wifi-gui/wifi-spinner-smaller.gif")
        anim = GdkPixbuf.PixbufAnimation.new_from_file(filename)
        spinner.set_from_animation(anim)
        self.pack_start(spinner, False, False, 30)

        self.win.show_all()

    def scan_networks(self):

        # Perform a network re-scan
        network_list = IWList(self.wiface).getList(unsecure=False, first=False)
        GObject.idle_add(self.go_to_wifi_screen, network_list)

    def go_to_wifi_screen(self, network_list):
        self.win.remove_main_widget()
        NetworkScreen(self.win, self.wiface, network_list)
