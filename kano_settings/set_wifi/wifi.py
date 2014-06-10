#!/usr/bin/env python

# set_wifi.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
import os
#from os.path import isfile
from kano.gtk3.heading import Heading
from kano.gtk3.buttons import KanoButton, OrangeButton
import kano_settings.components.fixed_size_box as fixed_size_box
import kano_settings.constants as constants
import kano.utils as utils
from kano.network import is_internet
from ..config_file import get_setting

network_message = ""
win = None
box = None
button = None
proxy_button = None
disable_proxy = None
WIFI_IMG_HEIGHT = 110
handler = None


def activate(_win, _box, _button, _proxy_button, _disable_proxy=None):
    global network_message, box, win, button, proxy_button

    constants.has_internet = is_internet()

    win = _win
    box = _box
    button = _button
    proxy_button = _proxy_button

    title = Heading("", "")
    box.pack_start(title.container, False, False, 0)

    # Table
    settings = fixed_size_box.Fixed()
    box.pack_start(settings.box, False, False, 0)

    internet_img = Gtk.Image()

    internet_status = Gtk.Label()
    internet_status_style = internet_status.get_style_context()
    internet_status.set_alignment(xalign=1, yalign=0.5)

    internet_action = Gtk.Label()
    internet_action_style = internet_action.get_style_context()
    internet_status_style.add_class("internet_status_top")
    internet_action_style.add_class("internet_status_bottom")
    internet_action.set_alignment(xalign=1, yalign=0.5)

    status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    status_box.props.valign = Gtk.Align.CENTER

    configure_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

    container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    container.pack_start(status_box, False, False, 2)
    container.pack_start(internet_img, False, False, 2)

    add_connection_button = KanoButton("WIFI")
    add_connection_button.connect("button_press_event", configure_wifi)

    if constants.has_internet:

        button.set_label("FINISH")

        status_box.pack_start(internet_status, False, False, 3)
        status_box.pack_start(internet_action, False, False, 3)
        status_box.pack_start(configure_container, False, False, 3)

        network = network_info()[0]
        ip = network_info()[1]

        internet_img.set_from_file(constants.media + "/Graphics/Internet-Connection.png")
        title.title.set_text("Connection found!")
        title.description.set_text("Great!")

        internet_status.set_text(network)
        internet_action.set_text(ip)

        if network == "Ethernet":
            # Change to ethernet image here
            internet_img.set_from_file(constants.media + "/Graphics/Internet-ethernetConnection.png")

        else:
            configure_button = OrangeButton("Configure")
            configure_button.connect("button_press_event", configure_wifi)
            configure_container.pack_start(configure_button, False, False, 0)
            divider_label = Gtk.Label("|")
            configure_container.pack_start(divider_label, False, False, 3)

        # Very hacky way to centre the Proxy button - put spaces in the label
        proxy_button.set_label("Proxy  ")
        configure_container.pack_end(proxy_button, False, False, 0)

    elif constants.proxy_enabled and disable_proxy:

        container.pack_start(disable_proxy, False, False, 0)

    else:
        status_box.pack_start(configure_container, False, False, 0)
        internet_img.set_from_file(constants.media + "/Graphics/Internet-noConnection.png")
        title.title.set_text("Get connected")
        title.description.set_text("Let's set up Internet")
        internet_status.set_text("No network found")
        configure_container.pack_start(add_connection_button, False, False, 0)
        # Change colour of update button here.
        button.set_label("SKIP THIS STEP")

    # So everything is centred even if we change the window height
    valign = Gtk.Alignment(xalign=0.5, yalign=0, xscale=0, yscale=0)
    padding_above = (settings.height - WIFI_IMG_HEIGHT) / 2
    valign.set_padding(padding_above, 0, 0, 0)
    valign.add(container)
    settings.box.pack_start(valign, False, False, 0)

    box.pack_start(button.align, False, False, 0)
    button.set_sensitive(True)
    box.show_all()


def network_info():
    network = ''
    command_ip = ''
    command_network = '/sbin/iwconfig wlan0 | grep \'ESSID:\' | awk \'{print $4}\' | sed \'s/ESSID://g\' | sed \'s/\"//g\''
    out, e, _ = utils.run_cmd(command_network)
    if e:
        network = "Ethernet"
        command_ip = '/sbin/ifconfig eth0 | grep inet | awk \'{print $2}\' | cut -d\':\' -f2'
    else:
        network = out
        command_ip = '/sbin/ifconfig wlan0 | grep inet | awk \'{print $2}\' | cut -d\':\' -f2'
    ip, _, _ = utils.run_cmd(command_ip)

    return [network.rstrip(), ip.rstrip()]


def configure_wifi(event=None, button=None):
    global network_message, win, handler

    # Disconnect this handler once the user regains focus to the window
    handler = win.connect("focus-in-event", refresh)
    # Call WiFi config
    os.system('rxvt -title \'WiFi\' -e sudo /usr/bin/kano-wifi')
    network_message = get_setting("Wifi")


def refresh(widget=None, event=None):
    global box, win, button, proxy_button, handler

    for child in box.get_children():
        box.remove(child)
    activate(win, box, button, proxy_button)
    win.disconnect(handler)


def apply_changes(event=None, button=None):
    return
