#!/usr/bin/env python

# set_wifi.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from gi.repository import Gtk, Gdk, GObject
import threading

import kano_settings.common as common
from kano_settings.templates import Template
from kano.gtk3.buttons import OrangeButton, KanoButton
from kano.gtk3.heading import Heading
from kano.gtk3.kano_dialog import KanoDialog
from kano.network import is_internet, network_info, launch_chromium
from kano_settings.system.proxy import get_all_proxies, set_all_proxies, test_proxy


class SetWifi(Template):
    wifi_connection_attempted = False

    def __init__(self, win):

        Template.__init__(self, "", "to be set", "COMPLETE")

        self.win = win
        self.win.set_main_widget(self)

        self.kano_button.connect("button-release-event", self.win.go_to_home)

        internet_img = Gtk.Image()

        # Very hacky way to centre the Proxy button - put spaces in the label
        self.proxy_button = OrangeButton("Proxy  ")
        self.proxy_button.connect("button-release-event", self.go_to_proxy)
        self.disable_proxy = OrangeButton("Disable proxy")

        self.win.change_prev_callback(self.win.go_to_home)
        self.win.top_bar.enable_prev()

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

        network_info_dict = network_info()
        common.has_internet = is_internet()

        if not common.has_internet or not network_info_dict:
            if network_info_dict:
                description = "Use the browser to log in or configure proxy"
            else:
                description = "Configure wireless"

            title = "Get connected"

            self.add_connection = KanoButton("WIFI")
            self.add_connection.connect("button_release_event", self.configure_wifi)
            # We removed the ability to use keyboard to click, so we also remove ability
            # to get keyboard focus
            self.add_connection.set_can_focus(False)

            # For now, this is removed as the event listener is interefering with the
            # kano-connect
            #self.add_connection.connect("key_release_event", self.configure_wifi)

            status_box.pack_start(self.add_connection, False, False, 0)
            internet_img.set_from_file(common.media + "/Graphics/Internet-noConnection.png")
            internet_status.set_text("No network found")
            self.kano_button.set_label("BACK")

            status_box.pack_start(configure_container, False, False, 3)

            go_to_portal_button = OrangeButton("Browser Login")
            go_to_portal_button.connect("button-press-event", launch_chromium)
            configure_container.pack_start(go_to_portal_button, False, False, 0)

            divider_label = Gtk.Label("|")
            configure_container.pack_start(divider_label, False, False, 3)

            configure_container.pack_end(self.proxy_button, False, False, 0)

        else:
            self.kano_button.set_label("COMPLETE")

            status_box.pack_start(internet_status, False, False, 3)
            status_box.pack_start(internet_action, False, False, 3)
            status_box.pack_start(configure_container, False, False, 3)

            network = network_info_dict.keys()[0]
            ip = network_info_dict[network]['address']
            network_text = network_info_dict[network]['nice_name']

            internet_img.set_from_file(common.media + "/Graphics/Internet-Connection.png")

            internet_status.set_text(network_text)
            internet_action.set_text(ip)

            go_to_portal_button = OrangeButton("Browser Login")
            go_to_portal_button.connect("button-press-event", launch_chromium)
            configure_container.pack_start(go_to_portal_button, False, False, 0)

            if network_text == 'Ethernet':
                title = "Connection found!"
                description = "You're on a wired network"
                # Change to ethernet image here
                internet_img.set_from_file(common.media + "/Graphics/Internet-ethernetConnection.png")

            else:
                title = "Connection found!"
                description = "You're on a wireless network"

                divider_label = Gtk.Label("|")
                configure_container.pack_start(divider_label, False, False, 3)

                configure_button = OrangeButton("Configure")
                configure_button.connect("button_press_event", self.configure_wifi)
                configure_container.pack_start(configure_button, False, False, 0)

            divider_label = Gtk.Label("|")
            configure_container.pack_start(divider_label, False, False, 3)
            configure_container.pack_end(self.proxy_button, False, False, 0)

        self.title.title.set_text(title)
        self.title.description.set_text(description)
        self.win.show_all()

    def go_to_proxy(self, widget, event):
        self.win.clear_win()
        SetProxy(self.win)

    def configure_wifi(self, widget=None, event=None):
        # If is a mouse click event or key pressed is ENTER
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:
            self.kano_button.set_sensitive(True)
            self.wifi_connection_attempted = True

            # Call WiFi config
            os.system('rxvt -title \'WiFi Setup\' -e /usr/bin/kano-wifi')
            # Refresh window after WiFi Setup
            self.win.clear_win()
            SetWifi(self.win)


class SetProxy(Gtk.Box):
    def __init__(self, win):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.kano_button = KanoButton()

        self.win = win
        self.win.set_main_widget(self)

        self.heading = Heading(
            "Proxy",
            "Connect via a friend"
        )

        grid = Gtk.Grid(column_homogeneous=False, column_spacing=10, row_spacing=10)

        self.kano_button.connect("button-release-event", self.apply_changes)
        self.kano_button.connect("key-release-event", self.apply_changes)
        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.go_to_wifi)

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

        self.checkbutton = Gtk.CheckButton("enable proxy")
        self.read_config()
        self.checkbutton.connect("clicked", self.proxy_status)
        self.checkbutton.set_can_focus(False)

        bottom_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        bottom_row.pack_start(self.checkbutton, False, False, 0)
        bottom_row.pack_start(self.kano_button, False, False, 60)
        bottom_row.set_margin_bottom(30)
        bottom_row.set_margin_left(70)

        grid.attach(self.ip_entry, 0, 0, 2, 2)
        grid.attach(self.username_entry, 0, 2, 2, 2)
        grid.attach(self.port_entry, 2, 0, 2, 2)
        grid.attach(password_box, 2, 2, 3, 2)

        grid_alignment = Gtk.Alignment(xscale=0, xalign=0.5, yscale=0, yalign=0.2)
        grid_alignment.add(grid)

        self.pack_start(self.heading.container, False, False, 0)
        self.pack_start(grid_alignment, True, True, 0)
        self.pack_end(bottom_row, False, False, 0)

        self.proxy_status(self.checkbutton)
        self.kano_button.set_sensitive(False)

        # Change text of kano button depending on if proxy is enabled
        if self.checkbutton.get_active():
            self.kano_button.set_label("ENABLE PROXY")
        else:
            self.kano_button.set_label("DISABLE PROXY")

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
        self.enable_proxy, data, _ = get_all_proxies()
        self.enabled_init = self.enable_proxy
        if self.enable_proxy:
            try:
                self.ip_entry.set_text(data['host'])
                self.port_entry.set_text(data['port'])
                if data['username']:
                    self.username_entry.set_text(data['username'])
                if data['password']:
                    self.password_entry.set_text(data['password'])
            except:
                # Something went wrong > disable proxy
                set_all_proxies(False)
                common.proxy_enabled = False
                self.enable_proxy = False
                self.enabled_init = False
                self.clear_entries()
        self.checkbutton.set_active(self.enable_proxy)

    def apply_changes(self, button, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == 65293:

            # This is a callback called by the main loop, so it's safe to
            # manipulate GTK objects:
            watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
            self.win.get_window().set_cursor(watch_cursor)
            self.kano_button.start_spinner()
            self.kano_button.set_sensitive(False)

            def lengthy_process():

                if self.enable_proxy:
                    host = self.ip_entry.get_text()
                    port = self.port_entry.get_text()
                    username = self.username_entry.get_text()
                    password = self.password_entry.get_text()
                    set_all_proxies(enable=True, host=host, port=port, username=username, password=password)
                    common.proxy_enabled = True

                    success, text = test_proxy()
                    if not success:
                        title = "Error with proxy"
                        description = text
                        return_value = 1

                        # disable proxy if we couldn't successfully enable it
                        set_all_proxies(False)
                        common.proxy_enabled = False
                    else:
                        title = "Successfully enabled proxy"
                        description = ""
                        return_value = 0

                else:
                    set_all_proxies(False)
                    common.proxy_enabled = False
                    title = "Successfully disabled proxy"
                    description = ""
                    return_value = 0

                def done(title, description, return_value):
                    kdialog = KanoDialog(
                        title,
                        description,
                        {
                            "OK":
                            {
                                "return_value": return_value
                            }
                        },
                        parent_window=self.win
                    )
                    response = kdialog.run()
                    self.win.get_window().set_cursor(None)
                    self.kano_button.stop_spinner()

                    if response == 0:
                        self.go_to_wifi()
                    elif response == 1:
                        self.checkbutton.set_active(False)
                        self.kano_button.set_sensitive(False)

                GObject.idle_add(done, title, description, return_value)

            thread = threading.Thread(target=lengthy_process)
            thread.start()

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
            # Run to see if it need enabling
            self.proxy_enabled()
            self.kano_button.set_label("ENABLE PROXY")

        else:
            self.ip_entry.set_sensitive(False)
            self.port_entry.set_sensitive(False)
            self.password_entry.set_sensitive(False)
            self.username_entry.set_sensitive(False)
            self.kano_button.set_label("DISABLE PROXY")
            self.kano_button.set_sensitive(True)

    # if proxy enabled: ip address, port are mandatory
    def proxy_enabled(self, widget=None, event=None):
        # Get IP address
        # Get port
        # Get
        # If these entries are non empty, good - else, disable the next button
        ip_text = self.ip_entry.get_text()
        port_text = self.port_entry.get_text()

        if ip_text == "" or port_text == "":
            self.kano_button.set_sensitive(False)
            return False

        else:
            self.kano_button.set_sensitive(True)
            return True

        return False
