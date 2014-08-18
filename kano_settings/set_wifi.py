#!/usr/bin/env python

# set_wifi.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
import os
from kano_settings.templates import Template, TopBarTemplate
from kano.gtk3.buttons import OrangeButton, KanoButton
from kano.gtk3.heading import Heading
from kano.gtk3.kano_dialog import KanoDialog

import kano_settings.constants as constants
from kano_settings.wifi.functions import network_info, launch_chromium, is_enabled, set_settings, enable, disable
from kano.network import is_internet
from kano_settings.config_file import get_setting, set_setting
from kano_settings.data import get_data


class SetWifi(Template):
    wifi_connection_attempted = False
    data = get_data("SET_WIFI")
    data_wifi = get_data("SET_WIFI_WIFI")
    data_ethernet = get_data("SET_WIFI_ETHERNET")
    data_offline = get_data("SET_WIFI_OFFLINE")

    def __init__(self, win):

        Template.__init__(self, "", "to be set", "COMPLETE")

        self.win = win
        self.win.set_main_widget(self)

        self.kano_button.connect("button-release-event", self.win.go_to_home)

        constants.has_internet = is_internet()

        internet_img = Gtk.Image()

        # Very hacky way to centre the Proxy button - put spaces in the label
        self.proxy_button = OrangeButton("Proxy  ")
        self.proxy_button.connect("button-release-event", self.go_to_proxy)
        self.disable_proxy = OrangeButton("Disable proxy")

        self.top_bar.set_prev_callback(self.win.go_to_home)
        self.top_bar.enable_prev()

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
        self.box.pack_start(container, False, False, 0)

        if constants.has_internet:
            self.kano_button.set_label("COMPLETE")

            status_box.pack_start(internet_status, False, False, 3)
            status_box.pack_start(internet_action, False, False, 3)
            status_box.pack_start(configure_container, False, False, 3)

            network = network_info()[0]
            ip = network_info()[1]

            internet_img.set_from_file(constants.media + "/Graphics/Internet-Connection.png")

            internet_status.set_text(network)
            internet_action.set_text(ip)

            go_to_portal_button = OrangeButton("Browser Login")
            go_to_portal_button.connect("button-press-event", launch_chromium)
            configure_container.pack_start(go_to_portal_button, False, False, 0)
            divider_label = Gtk.Label("|")
            configure_container.pack_start(divider_label, False, False, 3)

            if network == "Ethernet":
                title = self.data_ethernet["LABEL_1"]
                description = self.data_ethernet["LABEL_2"]
                kano_label = self.data_ethernet["KANO_BUTTON"]

                # Change to ethernet image here
                internet_img.set_from_file(constants.media + "/Graphics/Internet-ethernetConnection.png")

            else:
                title = self.data_wifi["LABEL_1"]
                description = self.data_wifi["LABEL_2"]
                kano_label = self.data_wifi["KANO_BUTTON"]

                configure_button = OrangeButton("Configure")
                configure_button.connect("button_press_event", self.configure_wifi)
                configure_container.pack_start(configure_button, False, False, 0)
                divider_label = Gtk.Label("|")
                configure_container.pack_start(divider_label, False, False, 3)

            configure_container.pack_end(self.proxy_button, False, False, 0)

        elif constants.proxy_enabled and self.disable_proxy:

            container.pack_start(self.disable_proxy, False, False, 0)

        else:
            title = self.data_offline["LABEL_1"]
            description = self.data_offline["LABEL_2"]
            kano_label = self.data_offline["KANO_BUTTON"]

            self.add_connection = KanoButton("WIFI")
            self.add_connection.connect("button_release_event", self.configure_wifi)
            self.add_connection.connect("key_release_event", self.configure_wifi)
            status_box.pack_start(self.add_connection, False, False, 0)
            internet_img.set_from_file(constants.media + "/Graphics/Internet-noConnection.png")
            self.title.title.set_text("Get connected")
            self.title.description.set_text("Let's set up Internet")
            internet_status.set_text("No network found")
            self.kano_button.set_label(kano_label)

        self.title.title.set_text(title)
        self.title.description.set_text(description)
        self.win.show_all()

    def go_to_proxy(self, widget, event):
        self.win.clear_win()
        SetProxy(self.win)

    def configure_wifi(self, widget=None, event=None):
        # If is a mouse click event or key pressed is ENTER
        if not hasattr(event, 'keyval') or event.keyval == 65293:
            self.kano_button.set_sensitive(True)
            self.wifi_connection_attempted = True

            # Disconnect this handler once the user regains focus to the window
            self.focus_in_handler = self.win.connect("focus-in-event", self.refresh)
            # Call WiFi config
            os.system('rxvt -title \'WiFi\' -e /usr/bin/kano-wifi')

    def refresh(self, widget=None, event=None):
        self.win.clear_win()
        SetWifi(self.win)
        self.win.disconnect(self.focus_in_handler)


class SetProxy(TopBarTemplate):
    data = get_data("SET_PROXY")

    def __init__(self, win):

        title = self.data["LABEL_1"]
        description = self.data["LABEL_2"]
        self.kano_label_enable = self.data["KANO_BUTTON_ENABLE"]
        self.kano_label_disable = self.data["KANO_BUTTON_DISABLE"]

        TopBarTemplate.__init__(self)
        self.kano_button = KanoButton()

        self.win = win
        self.win.set_main_widget(self)

        self.heading = Heading(title, description)

        grid = Gtk.Grid(column_homogeneous=False, column_spacing=10, row_spacing=10)

        self.kano_button.connect("button-release-event", self.apply_changes)
        self.kano_button.connect("key-release-event", self.apply_changes)
        self.top_bar.enable_prev()
        self.top_bar.set_prev_callback(self.go_to_wifi)

        self.ip_entry = Gtk.Entry()
        self.ip_entry.props.placeholder_text = "IP address"
        self.ip_entry.connect("key-release-event", self.proxy_enabled)

        self.username_entry = Gtk.Entry()
        self.username_entry.props.placeholder_text = "Username"
        self.username_entry.connect("key-release-event", self.proxy_enabled)

        self.port_entry = Gtk.Entry()
        self.port_entry.props.placeholder_text = "Port"
        self.port_entry.connect("key-release-event", self.proxy_enabled)

        self.password_entry = Gtk.Entry()
        self.password_entry.props.placeholder_text = "Password"
        self.password_entry.set_visibility(False)
        self.password_entry.connect("key-release-event", self.proxy_enabled)

        password_box = Gtk.Box()
        password_box.add(self.password_entry)

        checkbutton = Gtk.CheckButton("enable proxy")
        enabled = is_enabled()
        checkbutton.set_active(enabled)
        checkbutton.connect("clicked", self.proxy_status)
        checkbutton.set_can_focus(False)

        self.radio1 = Gtk.RadioButton.new_with_label_from_widget(None, "socks_v4 socks_v5")
        self.radio2 = Gtk.RadioButton.new_with_label_from_widget(self.radio1, "http_v1.0")

        self.radio1.connect("toggled", self.set_proxy_type)

        # Run once so we have the correct string proxy_type
        self.set_proxy_type(self.radio1)
        self.read_config()

        bottom_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        bottom_row.pack_start(checkbutton, False, False, 0)
        bottom_row.pack_start(self.kano_button, False, False, 60)
        bottom_row.set_margin_bottom(30)
        bottom_row.set_margin_left(70)

        grid.attach(self.ip_entry, 0, 0, 2, 2)
        grid.attach(self.username_entry, 0, 2, 2, 2)
        grid.attach(self.port_entry, 2, 0, 2, 2)
        grid.attach(password_box, 2, 2, 3, 2)
        grid.attach(self.radio1, 4, 0, 1, 1)
        grid.attach(self.radio2, 4, 1, 1, 1)

        grid_alignment = Gtk.Alignment(xscale=0, xalign=0.5, yscale=0, yalign=0.2)
        grid_alignment.add(grid)

        self.pack_start(self.heading.container, False, False, 0)
        self.pack_start(grid_alignment, True, True, 0)
        self.pack_end(bottom_row, False, False, 0)

        self.proxy_status(checkbutton)
        self.kano_button.set_sensitive(False)

        # Change text of kano button depending on if proxy is enabled
        if checkbutton.get_active():
            self.kano_button.set_label(self.kano_label_enable)
        else:
            self.kano_button.set_label(self.kano_label_disable)

        self.win.show_all()

    def clear_entries(self):
        self.ip_entry.set_text("")
        self.username_entry.set_text("")
        self.port_entry.set_text("")
        self.password_entry.set_text("")

    def go_to_wifi(self, widget=None, event=None):
        self.win.clear_win()
        SetWifi(self.win)

    # Update for proxy
    def read_config(self):
        port_text = get_setting("Proxy-port")
        self.port_entry.set_text(port_text)

        ip_text = get_setting("Proxy-ip")
        self.ip_entry.set_text(ip_text)

        username_text = get_setting("Proxy-username")
        self.username_entry.set_text(username_text)

        self.proxy_type = get_setting("Proxy-type")
        self.set_proxy_type_button()

    # Update for proxy
    def update_config(self, proxyip, proxyport, proxy_type, username):
        set_setting("Proxy-port", proxyport)
        set_setting("Proxy-ip", proxyip)
        set_setting("Proxy-username", username)
        set_setting("Proxy-type", self.proxy_type)

    def apply_changes(self, button, event):

        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == 65293:
            if self.enable_proxy:
                proxyip = self.ip_entry.get_text()
                proxyport = self.port_entry.get_text()
                username = self.username_entry.get_text()
                password = self.password_entry.get_text()
                set_settings(proxyip, proxyport, self.proxy_type, username, password)
                enable()

                # if successfully enabled, save in config file
                if is_enabled():
                    self.update_config(proxyip, proxyport, self.proxy_type, username)
                    constants.proxy_enabled = True
                    kdialog = KanoDialog("Proxy enabled!", parent_window=self.win)
                    self.go_to_wifi()
                # else, let user know the proxy is not turned on
                else:
                    kdialog = KanoDialog(
                        "Could not enable proxy",
                        "Try again?",
                        {
                            "OK":
                            {
                                "return_value": 0
                            },
                            "GO BACK":
                            {
                                "color": "red",
                                "return_value": 1
                            }
                        },
                        parent_window=self.win
                    )
                    response = kdialog.run()
                    if response == 1:
                        self.go_to_wifi()

            elif is_enabled():
                disable()
                constants.proxy_enabled = is_enabled()
                self.go_to_wifi()

    # Validation functions
    # If the "enable proxy" checkbox is checked/uncheckout, this function is activated
    # Disables the text entries if enable proxy is not checked
    def proxy_status(self, widget):
        self.enable_proxy = widget.get_active()
        if self.enable_proxy:
            self.ip_entry.set_sensitive(True)
            self.port_entry.set_sensitive(True)
            self.password_entry.set_sensitive(True)
            self.username_entry.set_sensitive(True)
            self.radio1.set_sensitive(True)
            self.radio2.set_sensitive(True)
            # Run to see if it need enabling
            self.proxy_enabled()
            self.kano_button.set_label(self.kano_label_enable)

        else:
            self.ip_entry.set_sensitive(False)
            self.port_entry.set_sensitive(False)
            self.password_entry.set_sensitive(False)
            self.username_entry.set_sensitive(False)
            self.radio1.set_sensitive(False)
            self.radio2.set_sensitive(False)
            self.kano_button.set_label(self.kano_label_disable)
            self.kano_button.set_sensitive(True)

    # if proxy enabled: ip address, port, and type are mandatory
    def proxy_enabled(self, widget=None, event=None):
        # Get IP address
        # Get port
        # Get type
        # If these entries are non empty, good - else, disable the next button
        ip_text = self.ip_entry.get_text()
        port_text = self.port_entry.get_text()

        if ip_text == "" or port_text == "":
            self.kano_button.set_sensitive(False)
            return False

        if self.valid_ip_address():
            self.kano_button.set_sensitive(True)
            return True

        return False

    # ip address needs to be a pure ipv4 format at this moment: x.y.z.q (no segment mask as in /xx)
    def valid_ip_address(self):

        # Find the index of "/"
        # Split into substring from "."
        # Check there are 4 (?).
        # Return/show tick if good, else do not allow them to click the next button
        ip_text = self.ip_entry.get_text()
        ip_array = ip_text.split(".")
        slash_array = ip_text.split("/")

        if len(slash_array) == 1 and len(ip_array) == 4:
            self.kano_button.set_sensitive(True)
            return True

        else:
            self.kano_button.set_sensitive(False)
            return False

    def set_proxy_type(self, radio_button):
        if radio_button.get_active():
            self.proxy_type = "socks_v4 socks_v5"
        else:
            self.proxy_type = "http_v1.0"

    def set_proxy_type_button(self):
        if self.proxy_type == "socks_v4 socks_v5":
            self.radio1.set_active(True)
            self.radio2.set_active(False)
        else:
            self.radio1.set_active(False)
            self.radio2.set_active(True)
