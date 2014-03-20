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
import set_proxy_grid

network_message = ""
win = None
box = None
update = None
WIFI_IMG_HEIGHT = 110


def activate(_win, _box, _update):
    global network_message, box, win, update

    win = _win
    box = _box
    update = _update

    title = heading.Heading("", "")
    box.pack_start(title.container, False, False, 0)

    proxy_button = Gtk.Button("Proxy Button")
    proxy_button.connect("button-press-event", proxy_button_press)
    #box.pack_start(proxy_button, False, False, 0)

    # Table
    settings = fixed_size_box.Fixed()
    box.pack_start(settings.box, False, False, 0)

    internet_img = Gtk.Image()

    internet_status = Gtk.Label()
    internet_status.modify_font(Pango.FontDescription("Bariol bold 13"))
    internet_status_style = internet_status.get_style_context()

    internet_action = Gtk.Label()
    internet_action.modify_font(Pango.FontDescription("Bariol bold 12"))
    internet_action_style = internet_action.get_style_context()
    internet_action_style.add_class("white")
    internet_status_style.add_class("internet_status_top")
    internet_action_style.add_class("internet_status_bottom")

    status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    status_box.pack_start(internet_status, False, False, 2)
    status_box.pack_start(internet_action, False, False, 2)
    status_box.props.valign = Gtk.Align.CENTER

    event_box = Gtk.EventBox()
    event_box.add(status_box)
    event_box_style = event_box.get_style_context()
    event_box.props.valign = Gtk.Align.CENTER
    # The size of the event box depends on WIFI_IMG_HEIGHT so that it is always centred.
    message_box_size = WIFI_IMG_HEIGHT - 25
    event_box.set_size_request(200, message_box_size)

    container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    container.pack_start(event_box, False, False, 0)
    container.pack_start(internet_img, False, False, 0)

    #event_box.set_events("button-press-event", self.on_button_press_event)
    event_box.connect("button-press-event", apply_changes)

    if constants.has_internet:
        # Get information
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
        print "Network: %s IP: %s" % (network, ip)

        internet_img.set_from_file(constants.media + "/Graphics/Internet-Connection.png")
        title.title.set_text("Connected")
        title.description.set_text(network)
        internet_status.set_text(network)
        internet_status_style.remove_class("dark_red")
        internet_status_style.add_class("dark_green")
        internet_action.set_text("Configure")
        event_box_style.add_class("connected")

    else:
        internet_img.set_from_file(constants.media + "/Graphics/Internet-noConnection.png")
        title.title.set_text("No network found")
        title.description.set_text("Shit man")
        internet_status.set_text("No network found")
        internet_status_style.remove_class("dark_green")
        internet_status_style.add_class("dark_red")
        internet_action.set_text("+ Click to add")
        event_box_style.add_class("not_connected")

    # So everything is centred even if we change the window height
    valign = Gtk.Alignment(xalign=0.5, yalign=0, xscale=0, yscale=0)
    padding_above = (settings.height - WIFI_IMG_HEIGHT) / 2
    valign.set_padding(padding_above, 0, 0, 0)
    valign.add(container)
    settings.box.pack_start(valign, False, False, 0)

    box.pack_start(update.box, False, False, 0)
    update.enable()


def proxy_button_press(event=None, button=None):
    global win, update, box

    # Remove element in the dynamic box
    for i in box.get_children():
        box.remove(i)

    set_proxy_grid.activate(win, box, update)
    win.show_all()


def apply_changes(event=None, button=None):
    # Call WiFi config
    os.system('rxvt -title \'WiFi\' -e sudo /usr/bin/kano-wifi')
    config_file.replace_setting("Wifi", network_message)
