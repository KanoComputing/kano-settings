#!/usr/bin/env python

# default_intro.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the layout of the main default intro screen

from gi.repository import Gtk

import kano_settings.set_keyboard as set_keyboard
import kano_settings.set_mouse as set_mouse
import kano_settings.set_font as set_font
import kano_settings.set_audio as set_audio
import kano_settings.set_display.home as set_display_overscan
import kano_settings.set_wifi.home as set_wifi_proxy
import kano_settings.set_wifi.proxy as set_proxy
import kano_settings.set_overclock as set_overclock
import kano_settings.set_account.home as set_account
import kano_settings.set_advance.home as set_advance
import kano_settings.set_wallpaper as set_wallpaper
import kano_settings.components.menu_button as menu_button
import kano_settings.constants as constants
from kano.network import is_internet
from kano.gtk3.scrolled_window import ScrolledWindow
from kano.utils import get_user_unsudoed
from ..config_file import get_setting


names = ["Keyboard", "Mouse", "Audio", "Display", "Wifi", "Overclocking", "Account", "Wallpaper", "Font", "Advanced"]
custom_info = ["Keyboard-country-human", "Mouse", "Audio", "Display-mode", "Wifi", "Overclocking", "Account",
               "Wallpaper", "Font"]
win = None
NUMBER_OF_COLUMNS = 2


class Default_Intro():

    # Initialises the default into screen
    def __init__(self, _win, WINDOW_HEIGHT, WINDOW_WIDTH, TOP_BAR_HEIGHT):
        global win

        win = _win

        for i in win.changeable_content.get_children():
            win.changeable_content.remove(i)

        buttons = []
        self.labels = []

        # The window width and height is reduced for the scrolled window and menu buttons (to account for the scrollbar)
        WINDOW_WIDTH = WINDOW_WIDTH - 20
        WINDOW_HEIGHT = WINDOW_HEIGHT - 101

        # names at top of file
        for x in range(len(names)):
            self.item = menu_button.Menu_button(names[x], '', WINDOW_WIDTH)
            self.labels.append(self.item.description)
            # Update the state of the button, so we know which button has been clicked on.
            self.item.button.state = x
            self.item.button.connect("clicked", self.go_to_level)
            buttons.append(self.item.button)

        # Fill the tabs with the current information
        self.update_intro()

        # Create table
        numRows = len(names) / NUMBER_OF_COLUMNS
        if len(names) % NUMBER_OF_COLUMNS != 0:  # Odd number of elements
            numRows += 1
        self.table = Gtk.Table(numRows, NUMBER_OF_COLUMNS, True)

        # Attach to table
        index = 0
        row = 0
        while index < len(names):
            for j in range(0, NUMBER_OF_COLUMNS):
                if index < len(names):
                    self.table.attach(buttons[index], j, j + 1, row, row + 1,
                                      Gtk.AttachOptions.FILL, Gtk.AttachOptions.FILL, 0, 0)
                    if row % 2:
                        buttons[index].get_style_context().add_class('appgrid_grey')
                    else:
                        buttons[index].get_style_context().add_class('appgrid_white')
                    index += 1
                else:
                    break
            row += 1

        # for scroll bar
        self.scrolled_window = ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.add_with_viewport(self.table)
        self.scrolled_window.set_size_request(WINDOW_WIDTH, WINDOW_HEIGHT)

        win.changeable_content.pack_start(self.scrolled_window, False, False, 0)

    # This is to update the introdction text, so that if the settings are modified and then we go back to the
    # intro screen, the latest information is shown
    def update_intro(self):
        for x in range(len(custom_info)):

            label_info = get_setting(custom_info[x])
            if len(label_info) > 13:
                label_info = label_info[:13] + "..."
            self.labels[x].set_text(label_info)

            if custom_info[x] == 'Wifi':
                text = ''
                # Check for internet
                constants.has_internet = is_internet()
                constants.proxy_enabled = set_proxy.is_enabled()
                if constants.has_internet:
                    text = 'Connected'
                elif constants.proxy_enabled:
                    text = "Proxy enabled"
                else:
                    text = 'Not connected'
                self.labels[x].set_text(text)

            if custom_info[x] == 'Account':
                text = get_user_unsudoed()
                self.labels[x].set_text(text)

    # Takes you back to the introduction screen (on pressing prev button)
    def on_prev(self, arg2=None, arg3=None):
        global win

        for i in win.changeable_content.get_children():
            win.changeable_content.remove(i)

        # If in set_wifi/proxy
        if set_wifi_proxy.in_proxy:
            set_wifi_proxy.to_wifi()
            return

        # If in set_accounts/password
        if set_account.in_password:
            set_account.to_account()
            return

        # If in set_advance/password
        if set_advance.get_in_password():
            for i in win.changeable_content.get_children():
                win.changeable_content.remove(i)
            set_advance.set_in_password(False)
            set_advance.activate(win, win.changeable_content, win.button)
            return

        self.update_intro()
        win.top_bar.disable_prev()
        win.top_bar.enable_next()
        win.changeable_content.pack_start(self.scrolled_window, False, False, 0)
        self.update_next_button(win)
        # Showing main menu
        win.show_all()

    # When clicking next in the default intro screen - takes you to the last level you visited
    def on_next(self, widget=None, arg2=None):
        global win

        for i in win.changeable_content.get_children():
            win.changeable_content.remove(i)

        win.top_bar.enable_prev()
        win.top_bar.disable_next()

        self.state_to_widget(win.last_level_visited).activate(win, win.changeable_content, win.button)
        win.last_level_visited = win.state
        # Do not do win.show_all() as will stop the combotextbox in set_keyboard being hidden properly

    # Apply Changes button needs to be updated depending on which level it's on
    def update_next_button(self, win):
        win.button.set_label("APPLY CHANGES")

    # On clicking a level button on default intro screen
    def go_to_level(self, widget):
        global win

        # Remove element in the dynamic box
        for i in win.changeable_content.get_children():
            win.changeable_content.remove(i)
        # Update current state
        win.state = widget.state
        # Record this level so we can go back to it
        win.last_level_visited = win.state

        # Grey out next arrow and darken prev arrow
        win.top_bar.enable_prev()
        win.top_bar.disable_next()

        # Call next state
        self.state_to_widget(win.state).activate(win, win.changeable_content, win.button)

    # On clicking a level button on default intro screen
    def go_to_level_given_state(self, state):
        global win

        # Remove element in the dynamic box
        for i in win.changeable_content.get_children():
            win.changeable_content.remove(i)
        # Update current state
        win.state = state
        # Record this level so we can go back to it
        win.last_level_visited = win.state

        # Grey out next arrow and darken prev arrow
        win.top_bar.enable_prev()
        win.top_bar.disable_next()

        # Call next state
        self.state_to_widget(win.state).activate(win, win.changeable_content, win.button)

        # Refresh window
        win.show_all()

    # This updates the current level.
    def update(self, widget, event=None):
        if not hasattr(event, 'keyval') or event.keyval == 65293:
            returnValue = self.state_to_widget(win.state).apply_changes(widget)

            # Disable the default flow is apply_changes returns -1
            # This way, can allow files to communicate and decide where they go independently (e.g. set_wifi)
            if returnValue == -1:
                return

            # Go back to intro screen
            self.on_prev()

    def state_to_widget(self, x):
        return {
            0: set_keyboard,
            1: set_mouse,
            2: set_audio,
            3: set_display_overscan,
            4: set_wifi_proxy,
            5: set_overclock,
            6: set_account,
            7: set_wallpaper,
            8: set_font,
            9: set_advance,
        }[x]
