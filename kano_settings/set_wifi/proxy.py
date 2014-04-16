#!/usr/bin/env python

# set_proxy.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
import kano_settings.components.heading as heading
import kano_settings.components.fixed_size_box as fixed_size_box
import kano_settings.proxy as proxy
import kano_settings.constants as constants
import kano_settings.config_file as config_file

win = None
box = None
ip_entry = None
port_entry = None
username_entry = None
password_entry = None
proxy_type = None
enable_proxy = False
next_button = None
update = None

GRID_HEIGHT = 150

libpreload = proxy.LibPreload()
pxysettings = proxy.ProxySettings()


def is_enabled():
    return libpreload.is_enabled()


def enable():
    libpreload.proxify(True)


def disable():
    libpreload.proxify(False)


def get_settings():
    return pxysettings.get_settings()


def set_settings(proxyip, proxyport, proxytype, username=None, password=None):
    settings = {
        'proxy-ip': proxyip,
        'proxy-port': proxyport,
        'proxy-type': proxytype,   # one of : "socks_v4 socks_v5" or "http_v1.0"
        'username': username,
        'password': password
    }
    pxysettings.set_settings(settings)


# Validation functions
# If the "enable proxy" checkbox is checked/uncheckout, this function is activated
# Disables the text entries if enable proxy is not checked
def proxy_status(widget):
    global win, next_button, ip_entry, port_entry, password_entry, username_entry, enable_proxy

    enable_proxy = widget.get_active()
    if enable_proxy:
        ip_entry.set_sensitive(True)
        port_entry.set_sensitive(True)
        password_entry.set_sensitive(True)
        username_entry.set_sensitive(True)
        # Run to see if it need enabling
        proxy_enabled()

    else:
        ip_entry.set_sensitive(False)
        port_entry.set_sensitive(False)
        password_entry.set_sensitive(False)
        username_entry.set_sensitive(False)
        next_button.set_sensitive(True)


# if proxy enabled: ip address, port, and type are mandatory
def proxy_enabled(widget=None, event=None):
    global win, ip_entry, password_entry, port_entry, next_button

    # Get IP address
    # Get port
    # Get type
    # If these entries are non empty, good - else, disable the next button
    ip_text = ip_entry.get_text()
    port_text = port_entry.get_text()
    if ip_text == "" or port_text == "":
        next_button.set_sensitive(False)
        return False

    if valid_ip_address(ip_text):
        next_button.set_sensitive(True)
        return True

    return False


# ip address needs to be a pure ipv4 format at this moment: x.y.z.q (no segment mask as in /xx)
def valid_ip_address(ip_widget, event=None):
    global win, next_button

    # Find the index of "/"
    # Split into substring from "."
    # Check there are 4 (?).
    # Return/show tick if good, else do not allow them to click the next button
    ip_array = ip_widget.split(".")
    slash_array = ip_widget.split("/")
    if len(slash_array) == 1 and len(ip_array) == 4:
        next_button.set_sensitive(True)
        return True

    else:
        next_button.set_sensitive(False)
        return False


def set_proxy_type(radio_button):
    global proxy_type

    if radio_button.get_active():
        proxy_type = "socks_v4 socks_v5"
    else:
        proxy_type = "http_v1.0"


def set_proxy_type_button(radio1, radio2):

    if proxy_type == "socks_v4 socks_v5":
        radio1.set_active(True)
        radio2.set_active(False)
    else:
        radio1.set_active(False)
        radio2.set_active(True)


def activate(_win, _box, _update, to_wifi_button):
    global win, ip_entry, port_entry, username_entry, password_entry, box, next_button

    win = _win
    box = _box
    title = heading.Heading("Proxy", "Connect via a friend")
    settings = fixed_size_box.Fixed()
    grid = Gtk.Grid(column_homogeneous=False, column_spacing=10, row_spacing=10)

    ip_entry = Gtk.Entry()
    ip_entry.props.placeholder_text = "IP address"

    username_entry = Gtk.Entry()
    username_entry.props.placeholder_text = "Username"

    port_entry = Gtk.Entry()
    port_entry.props.placeholder_text = "Port"

    password_entry = Gtk.Entry()
    password_entry.props.placeholder_text = "Password"
    password_entry.set_visibility(False)
    password_box = Gtk.Box()
    password_box.add(password_entry)

    checkbutton = Gtk.CheckButton("enable proxy")
    enabled = is_enabled()
    checkbutton.set_active(enabled)
    checkbutton.connect("clicked", proxy_status)
    checkbutton.set_can_focus(False)

    radio1 = Gtk.RadioButton.new_with_label_from_widget(None, "socks_v4 socks_v5")
    radio1.set_can_focus(False)
    radio2 = Gtk.RadioButton.new_with_label_from_widget(radio1, "http_v1.0")
    radio2.set_can_focus(False)

    radio1.connect("toggled", set_proxy_type)

    # Run once so we have the correct string proxy_type
    set_proxy_type(radio1)

    read_config(radio1, radio2)
    next_button = to_wifi_button

    apply_changes_alignment = Gtk.Alignment(xalign=0, yalign=0, xscale=0, yscale=0)
    apply_changes_alignment.add(next_button)

    bottom_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    bottom_row.pack_start(checkbutton, False, False, 0)
    bottom_row.pack_start(apply_changes_alignment, False, False, 0)
    apply_changes_alignment.set_padding(2, 2, 60, 2)

    grid.attach(ip_entry, 0, 0, 2, 2)
    grid.attach(username_entry, 0, 2, 2, 2)
    grid.attach(port_entry, 2, 0, 2, 2)
    grid.attach(password_box, 2, 2, 3, 2)
    grid.attach(radio1, 4, 0, 1, 1)
    grid.attach(radio2, 4, 1, 1, 1)

    grid_alignment = Gtk.Alignment(xalign=0, yalign=0, xscale=0, yscale=0)
    grid_alignment.add(grid)
    padding_above = (settings.height - GRID_HEIGHT) / 2
    grid_alignment.set_padding(padding_above, 0, 0, 0)
    settings.box.pack_start(grid_alignment, False, False, 0)

    box.pack_start(title.container, False, False, 0)
    box.pack_start(settings.box, False, False, 0)
    box.pack_end(bottom_row, False, False, 0)

    proxy_status(checkbutton)

    # Need to disconnect this on exit
    win.connect("key-release-event", proxy_enabled)


# Update for proxy
def read_config(radio1, radio2):
    global port_entry, username_entry, ip_entry, proxy_type

    port_text = config_file.read_from_file("Proxy-port")
    port_entry.set_text(port_text)

    ip_text = config_file.read_from_file("Proxy-ip")
    ip_entry.set_text(ip_text)

    username_text = config_file.read_from_file("Proxy-username")
    username_entry.set_text(username_text)

    proxy_type = config_file.read_from_file("Proxy_type")
    set_proxy_type_button(radio1, radio2)


# Update for proxy
def update_config(proxyip, proxyport, proxy_type, username):
    config_file.replace_setting("Proxy-port", proxyport)
    config_file.replace_setting("Proxy-ip", proxyip)
    config_file.replace_setting("Proxy-username", username)
    config_file.replace_setting("Proxy_type", proxy_type)


def apply_changes(button=None, arg2=None):

    if enable_proxy:
        proxyip = ip_entry.get_text()
        proxyport = port_entry.get_text()
        username = username_entry.get_text()
        password = password_entry.get_text()
        set_settings(proxyip, proxyport, proxy_type, username, password)
        enable()
        update_config(proxyip, proxyport, proxy_type, username)
        constants.proxy_enabled = True

    elif is_enabled():
        disable()
        constants.proxy_enabled = is_enabled()

    return
