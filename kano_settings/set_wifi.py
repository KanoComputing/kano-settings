#!/usr/bin/env python

# set_wifi.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Pango
import os
import kano_settings.components.heading as heading
import kano_settings.components.fixed_size_box as fixed_size_box
import kano_settings.constants as constants
import kano_settings.config_file as config_file
import kano.utils as utils

network_message = ""
win = None
box = None
update = None
WIFI_IMG_HEIGHT = 110


def activate(_win, _box, _update, to_proxy_button):
    global network_message, box, win, update

    win = _win
    box = _box
    update = _update

    title = heading.Heading("", "")
    box.pack_start(title.container, False, False, 0)

    #proxy_button = Gtk.Button("Proxy Button")
    #proxy_button.connect("button-press-event", proxy_button_press)
    #box.pack_start(proxy_button, False, False, 0)

    # Table
    settings = fixed_size_box.Fixed()
    box.pack_start(settings.box, False, False, 0)

    internet_img = Gtk.Image()

    internet_status = Gtk.Label()
    internet_status.modify_font(Pango.FontDescription("Bariol bold 16"))
    internet_status_style = internet_status.get_style_context()

    internet_action = Gtk.Label()
    internet_action.modify_font(Pango.FontDescription("Bariol 14"))
    internet_action_style = internet_action.get_style_context()
    internet_status_style.add_class("internet_status_top")
    internet_action_style.add_class("internet_status_bottom")

    status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    status_box.props.valign = Gtk.Align.CENTER

    configure_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    configure_container.props.halign = Gtk.Align.CENTER

    container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    container.pack_start(status_box, False, False, 2)
    container.pack_start(internet_img, False, False, 2)

    add_connection_button = Gtk.EventBox()
    add_connection_button.get_style_context().add_class("apply_changes_button")
    add_connection_button.get_style_context().add_class("green")
    add_connection_label = Gtk.Label("ADD CONNECTION")
    add_connection_label.modify_font(Pango.FontDescription("Bariol bold 14"))
    add_connection_label.get_style_context().add_class("apply_changes_text")
    add_connection_button.add(add_connection_label)
    add_connection_button.set_size_request(200, 44)
    add_connection_button.connect("button_press_event", configure_wifi)

    if constants.has_internet:

        update.green_background()
        update.text.set_text("FINISH")

        status_box.pack_start(internet_status, False, False, 3)
        status_box.pack_start(internet_action, False, False, 3)
        status_box.pack_start(configure_container, False, False, 3)

        network = network_info()[0]
        ip = network_info()[1]

        internet_img.set_from_file(constants.media + "/Graphics/Internet-Connection.png")
        title.title.set_text("Connection found!")
        title.description.set_text("Great!")
        proxy_button = to_proxy_button

        internet_status.set_text(network)
        internet_action.set_text(ip)

        if network == "Ethernet":
            # Change to ethernet image here
            internet_img.set_from_file(constants.media + "/Graphics/Internet-ethernetConnection.png")

        else:
            configure_button = Gtk.EventBox()
            configure_label = Gtk.Label("Configure")
            configure_label.get_style_context().add_class("orange")
            configure_label.modify_font(Pango.FontDescription("Bariol 13"))
            configure_button.add(configure_label)
            configure_button.connect("button_press_event", configure_wifi)
            configure_container.pack_start(configure_button, False, False, 0)
            divider_label = Gtk.Label("|")
            configure_container.pack_start(divider_label, False, False, 3)

        configure_container.pack_start(proxy_button, False, False, 0)

    else:
        status_box.pack_start(configure_container, False, False, 0)
        internet_img.set_from_file(constants.media + "/Graphics/Internet-noConnection.png")
        title.title.set_text("No network found")
        title.description.set_text("Aw, man.")
        internet_status.set_text("No network found")
        configure_container.pack_start(add_connection_button, False, False, 0)
        # Change colour of update button here.
        update.grey_background()
        update.text.set_text("SKIP THIS STEP")

    # So everything is centred even if we change the window height
    valign = Gtk.Alignment(xalign=0.5, yalign=0, xscale=0, yscale=0)
    padding_above = (settings.height - WIFI_IMG_HEIGHT) / 2
    valign.set_padding(padding_above, 0, 0, 0)
    valign.add(container)
    settings.box.pack_start(valign, False, False, 0)

    box.pack_start(update.box, False, False, 0)
    update.enable()


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
    print "Network: %s IP: %s" % (network.rstrip(), ip.rstrip())

    return [network.rstrip(), ip.rstrip()]


def configure_wifi(event=None, button=None):
    # Call WiFi config
    os.system('rxvt -title \'WiFi\' -e sudo /usr/bin/kano-wifi')
    config_file.replace_setting("Wifi", network_message)


def apply_changes(event=None, button=None):
    return
