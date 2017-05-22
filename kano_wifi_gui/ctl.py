# ctl.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# WiFi control functions

from kano_networking.ifaces import get_wlan_device


def disconnect_wifi():
    from kano.network import KwifiCache, disconnect
    from kano.gtk3.kano_dialog import KanoDialog

    iface = get_wlan_device()
    disconnect(iface)
    wificache = KwifiCache()
    wificache.empty()

    kdialog = KanoDialog(
        # Text from the content team.
        _("Disconnect complete - you're now offline."),
    )
    kdialog.run()

    return 0


def launch_wifi_gui(socket_id=None, no_confirm_ether=False):
    from gi.repository import GObject
    from kano_wifi_gui.wifi_window import create_wifi_gui

    GObject.threads_init()

    is_plug = socket_id is not None
    create_wifi_gui(is_plug, socket_id, no_confirm_ether)

    return 0
