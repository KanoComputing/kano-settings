# RefreshNetwork.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Show spinner screen while reloading the networks
#

from gi.repository import GObject
from kano_wifi_gui.NetworkScreen import NetworkScreen
from kano.network import IWList
from kano_wifi_gui.SpinnerScreen import SpinnerScreen


class RefreshNetworks():
    def __init__(self, win):
        self._win = win
        self._wiface = self._win.wiface
        self._refresh_networks()

    def _refresh_networks(self):
        title = "Searching for networks"
        description = "Any minute now"
        self._win.remove_main_widget()
        SpinnerScreen(self._win, title, description, self._scan_networks)

    def _go_to_network_screen(self, network_list):
        self._win.remove_main_widget()
        NetworkScreen(self._win, network_list)

    # Get networks and pass to network screen
    def _scan_networks(self):

        # Perform a network re-scan
        network_list = IWList(self._win.wiface).getList(unsecure=False, first=False)
        GObject.idle_add(self._go_to_network_screen, network_list)
