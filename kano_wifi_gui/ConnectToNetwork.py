# ConnectToNetwork.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Show spinner screen while connecting to a network
#

import os
import threading
from gi.repository import Gtk, GObject

from kano.logging import logger
from kano.network import KwifiCache, connect
from kano.network import RC_CONNECTED, RC_BAD_PASSWORD, RC_AP_NOT_IN_RANGE, \
   RC_NO_DHCP_LEASE, RC_INCORRECT_PASSWORD_LEN, RC_INTERNAL_ERROR

from kano_wifi_gui.paths import img_dir
from kano_wifi_gui.SpinnerScreen import SpinnerScreen
from kano_wifi_gui.Template import Template


class ConnectToNetwork():

    # Pass details of the network to this screen
    def __init__(self, win, network_name, passphrase, encryption):
        self._win = win
        self._wiface = self._win.wiface
        self._network_name = network_name
        self._passphrase = passphrase
        self._encryption = encryption

        self._connect_to_network()

    def _connect_to_network(self):
        title = _("Connecting to {}").format(self._network_name)
        description = _("Any minute now")
        SpinnerScreen(self._win, title, description,
                      self._launch_connect_thread)

    def _go_to_spinner_screen(self, button=None, event=None):
        from kano_wifi_gui.RefreshNetworks import RefreshNetworks

        RefreshNetworks(self._win)

    def _thread_finish(self, rc):
        '''
        Callback invoked after the connect() method returns
        Decide why the connection failed, and alert the user accordingly
        '''
        if rc == RC_CONNECTED:
            self._success_screen()
        elif rc == RC_BAD_PASSWORD:
            self._wrong_password_screen()
        elif rc == RC_INCORRECT_PASSWORD_LEN:
            self._wrong_password_screen()
        else:
            # For now, assume the signal is too weak, because
            # the network was correctly chosen from the scan list.
            self._weak_signal_screen()

    def _wrong_password_screen(self):
        from kano_wifi_gui.PasswordScreen import PasswordScreen

        self._win.remove_main_widget()
        PasswordScreen(self._win, self._win.wiface,
                       self._network_name, self._encryption,
                       wrong_password=True)

    def _weak_signal_screen(self):
        '''
        The network cannot be joined because the signal is too weak.
        Show an error message dialog, so the user can easily fix and retry.
        '''
        win.remove_main_widget()
        title = _("Cannot connect!")
        description = _("Maybe the signal was too weak to connect.")
        buttons = [
            {
                'label': ""
            },
            {
                'label': _("TRY AGAIN"),
                'type': 'KanoButton',
                'color': 'green',
                # Go to the network refresh screen
                'callback': self._go_to_spinner_screen
            },
            {
                'label': _("QUIT"),
                'type': 'OrangeButton',
                'callback': Gtk.main_quit
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

    def _success_screen(self):
        self._win.remove_main_widget()
        title = _("Success")
        description = _("You're connected")
        buttons = [
            {
                'label': _("OK"),
                'type': 'KanoButton',
                'color': 'green',
                'callback': Gtk.main_quit
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

    def _launch_connect_thread(self):
        logger.debug("Connecting to {}".format(self._network_name))

        # start thread
        t = threading.Thread(
            target=_connect_thread_,
            args=(
                self._win.wiface,
                self._network_name,
                self._passphrase,
                self._encryption,
                self._thread_finish
            )
        )

        t.daemon = True
        t.start()


def _connect_thread_(wiface, network_name, passphrase, encryption,
                     thread_finish_cb):
    '''
    This function runs in a thread so we can run a spinner alongside.

    :param wiface: wifi card id
    :param network_name: network id
    :param passphrase: password entered by user
    :param encryption: type of encryption
    :param disable_widget_cb: the callback for any widgets that need to be
                              disabled
    :param thread_finish_cb: the callback to be run when the thread is finished
    '''

    rc = connect(wiface, network_name, encryption, passphrase)

    # save the connection in cache so it reconnects on next system boot
    wificache = KwifiCache()
    if not rc:
        wificache.save(network_name, encryption, passphrase)
    else:
        wificache.empty()

    logger.debug(
        "Connecting to {} {} {}. Return code: {}".format(
            network_name, encryption, passphrase, rc
        )
    )

    GObject.idle_add(thread_finish_cb, rc)
