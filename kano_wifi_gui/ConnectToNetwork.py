# ConnectToNetwork.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Show spinner screen while connecting to a network
#

from gi.repository import GObject
from kano_wifi_gui.SpinnerScreen import SpinnerScreen
import threading
from kano.logging import logger
from kano.network import KwifiCache, connect
from kano_wifi_gui.Template import Template
from gi.repository import Gtk
import os
from kano_wifi_gui.paths import img_dir


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
        title = "Connecting to {}".format(self._network_name)
        description = "Any minute now"
        SpinnerScreen(self._win, title, description,
                      self._launch_connect_thread)

    def _go_to_network_screen(self, network_list):
        from kano_wifi_gui.NetworkScreen import NetworkScreen

        self._win.remove_main_widget()
        NetworkScreen(self._win, network_list)

    def _thread_finish(self, success):
        if success:
            self._success_screen()
        else:
            self._wrong_password_screen()

    def _wrong_password_screen(self):
        from kano_wifi_gui.PasswordScreen import PasswordScreen

        self._win.remove_main_widget()
        PasswordScreen(self._win, self._win.wiface,
                       self._network_name, self._encryption,
                       wrong_password=True)

    def _fail_screen(self, win):
        win.remove_main_widget()
        title = "Cannot connect!"
        description = "Maybe the signal was too weak to connect."
        buttons = [
            {
                "label": ""
            },
            {
                "label": "TRY AGAIN",
                "type": "KanoButton",
                "color": "green",
                # Go to the network refresh screen
                "callback": self._go_to_network_screen
            },
            {
                "label": "QUIT",
                "type": "OrangeButton",
                "callback": Gtk.main_quit
            }
        ]
        img_path = os.path.join(img_dir, "no-wifi.png")

        win.set_main_widget(
            Template(
                title,
                description,
                buttons,
                win.is_plug(),
                img_path
            )
        )

    def _success_screen(self):
        self._win.remove_main_widget()
        title = "Success"
        description = "You're connected"
        buttons = [
            {
                "label": "OK",
                "type": "KanoButton",
                "color": "green",
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

    def _launch_connect_thread(self):
        logger.debug('Connecting to {}'.format(self._network_name))

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

    success = connect(wiface, network_name, encryption, passphrase)

    # save the connection in cache so it reconnects on next system boot
    wificache = KwifiCache()
    if success:
        wificache.save(network_name, encryption, passphrase)
    else:
        wificache.empty()

    logger.debug(
        'Connecting to {} {} {}. Successful: {}'.format(
            network_name, encryption, passphrase, success
        )
    )

    GObject.idle_add(thread_finish_cb, success)
