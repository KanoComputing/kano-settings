#!/usr/bin/env python

# default_intro.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the layout of the main default intro screen

from gi.repository import Gtk

import kano_settings.set_email as set_email
import kano_settings.set_keyboard as set_keyboard
import kano_settings.set_mouse as set_mouse
import kano_settings.set_audio as set_audio
import kano_settings.set_display as set_display
import kano_settings.set_wifi_proxy as set_wifi_proxy
import kano_settings.set_proxy as set_proxy
import kano_settings.set_overclock as set_overclock
import kano_settings.set_account as set_account
import kano_settings.config_file as config_file
import kano_settings.components.menu_button as menu_button
import kano_settings.components.cursor as cursor
import kano_settings.constants as constants
from kano.network import is_internet

names = ["Keyboard", "Mouse", "Audio", "Display", "Email", "Wifi", "Overclocking", "Account"]
custom_info = ["Keyboard-country-human", "Mouse", "Audio", "Display-mode", "Email", "Wifi", "Overclocking", "Account"]
win = None
NUMBER_OF_ROWS = 4
NUMBER_OF_COLUMNS = 2
ROW_PADDING = 5
COLUMN_PADDING = 30


class Default_Intro():

    # Initialises the default into screen
    def __init__(self, _win, WINDOW_HEIGHT, WINDOW_WIDTH, TOP_BAR_HEIGHT):
        global win

        win = _win

        for i in win.changeable_content.get_children():
            win.changeable_content.remove(i)

        self.table = Gtk.Table(NUMBER_OF_ROWS, NUMBER_OF_COLUMNS, True)

        buttons = []
        self.labels = []

        # names at top of file
        for x in range(len(names)):
            self.item = menu_button.Menu_button(names[x], '')
            self.labels.append(self.item.description)
            # Update the state of the button, so we know which button has been clicked on.
            self.item.button.state = x
            self.item.button.connect("clicked", self.go_to_level)
            buttons.append(self.item.button)

            self.item.button.connect('enter-notify-event',
                                     cursor.hand_cursor, win)
            self.item.button.connect('leave-notify-event',
                                     cursor.arrow_cursor, win)

        # Fill the tabs with the current information
        self.update_intro()

        # Attach to table
        index = 0
        row = 0
        while index < len(names):
            for j in range(0, NUMBER_OF_COLUMNS):
                if index < len(names):
                    self.table.attach(buttons[index], j, j + 1, row, row + 1,
                                      Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, COLUMN_PADDING, ROW_PADDING)
                    index += 1
                else:
                    break
            row += 1

        # for scroll bar
        self.scrolled_window = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.scrolled_window.add_with_viewport(self.table)

        WINDOW_WIDTH = WINDOW_WIDTH - 20
        WINDOW_HEIGHT = WINDOW_HEIGHT - 85
        self.scrolled_window.set_size_request(WINDOW_WIDTH, WINDOW_HEIGHT)

        win.changeable_content.pack_start(self.scrolled_window, False, False, 0)

    # This is to update the introdction text, so that if the settings are modified and then we go back to the
    # intro screen, the latest information is shown
    def update_intro(self):
        for x in range(len(custom_info)):

            config_file.read_from_file(custom_info[x])
            label_info = str(config_file.read_from_file(custom_info[x]))
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

    # Takes you back to the introduction screen (on pressing prev button)
    def on_prev(self, arg2=None, arg3=None):
        global win
        for i in win.changeable_content.get_children():
            win.changeable_content.remove(i)

        # If in set_proxy
        if set_wifi_proxy.in_proxy:
            set_wifi_proxy.to_wifi()
            return

        self.update_intro()
        win.top_bar.disable_prev()
        win.top_bar.enable_next()
        win.changeable_content.pack_start(self.scrolled_window, False, False, 0)
        self.update_next_button(win)
        win.show_all()

    # When clicking next in the default intro screen - takes you to the last level you visited
    def on_next(self, widget=None, arg2=None):
        global win

        for i in win.changeable_content.get_children():
            win.changeable_content.remove(i)

        win.top_bar.enable_prev()
        win.top_bar.disable_next()

        self.state_to_widget(win.last_level_visited).activate(win, win.changeable_content, win.update)
        win.last_level_visited = win.state
        win.show_all()

    # Apply Changes button needs to be updated depending on which level it's on
    def update_next_button(self, win):
        win.update.green_background()
        win.update.text.set_text("APPLY CHANGES")

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
        self.state_to_widget(win.state).activate(win, win.changeable_content, win.update)

        # Refresh window
        win.show_all()

        # Change cursor to arrow
        cursor.arrow_cursor(None, None, win)

    # This updates the current level.
    def update(self, widget, arg2=None):

        returnValue = self.state_to_widget(win.state).apply_changes(widget)
        if returnValue == -1:
            return

        # Go back to intro screen
        self.on_prev()

        # Change cursor to arrow
        cursor.arrow_cursor(None, None, win)

    def state_to_widget(self, x):
        return {
            0: set_keyboard,
            1: set_mouse,
            2: set_audio,
            3: set_display,
            4: set_email,
            5: set_wifi_proxy,
            6: set_overclock,
            7: set_account,
        }[x]
