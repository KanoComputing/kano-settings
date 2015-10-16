#!/usr/bin/env python

# connect_functions.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Common connect functions between screens on kano-wif-gui

from gi.repository import GObject
from kano.network import KwifiCache, connect
from kano.logging import logger
import threading


# Added extra window argument
def launch_connect_thread(wiface, ssid, passphrase, encryption,
                          disable_widget_cb, thread_finish_cb,
                          win):

    '''
    This disables the buttons on the application,
    starts and spinner and starts the _connect_thread_ thread

    :param wiface: wifi card id
    :param ssid: network id
    :param passphrase: password entered by user
    :param encryption: type of encryption
    :param disable_widget_cb: the callback for any widgets that need to be
                              disabled
    :param thread_finish_cb: the callback to be run when the thread is finished
    '''

    logger.debug('Connecting to {}'.format(ssid))

    # Start thread
    t = threading.Thread(
        target=_connect_thread_,
        args=(wiface, ssid, passphrase, encryption, thread_finish_cb)
    )

    t.daemon = True
    t.start()


def _connect_thread_(wiface, ssid, passphrase, encryption, thread_finish_cb):
    '''
    This function runs in a thread so we can run a spinner alongside.

    :param wiface: wifi card id
    :param ssid: network id
    :param passphrase: password entered by user
    :param encryption: type of encryption
    :param disable_widget_cb: the callback for any widgets that need to be
                              disabled
    :param thread_finish_cb: the callback to be run when the thread is finished
    '''

    success = connect(wiface, ssid, encryption, passphrase)

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

    GObject.idle_add(thread_finish_cb, success)
