#!/usr/bin/env python

# default_intro.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the layout of the main default intro screen

from gi.repository import Gtk

import kano_settings.set_intro as set_intro
import kano_settings.set_email as set_email
import kano_settings.set_keyboard as set_keyboard
import kano_settings.set_audio as set_audio
import kano_settings.set_display as set_display
import kano_settings.set_wifi as set_wifi
import kano_settings.config_file as config_file
import kano_settings.components.menu_button as menu_button
import kano_settings.constants as constants
from kanowifilib import is_internet

names = ["Keyboard", "Email", "Audio", "Display", "Wifi"]
custom_info = ["Keyboard-country-human", "Email", "Audio", "Display-mode", "Wifi"]
win = None


class Default_Intro():

    # Initialises the default into screen
    def __init__(self, _win):
        global win

        win = _win

        for i in win.changeable_content.get_children():
            win.changeable_content.remove(i)

        self.table = Gtk.Table(3, 2, True)

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
        # Fill the tabs with the current information
        self.update_intro()

        # Attach to table
        self.table.attach(buttons[0], 0, 1, 0, 1, Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 5, 5)
        self.table.attach(buttons[1], 0, 1, 1, 2, Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 5, 5)
        self.table.attach(buttons[2], 0, 1, 2, 3, Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 5, 5)
        self.table.attach(buttons[3], 1, 2, 0, 1, Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 5, 5)
        self.table.attach(buttons[4], 1, 2, 1, 2, Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 5, 5)
        #self.table.set_size_request(450, 100)
        win.changeable_content.pack_start(self.table, False, False, 0)

    # This is to update the introdction text, so that if the settings are modified and then we go back to the
    # intro screen, the latest information is shown
    def update_intro(self):
        for x in range(len(custom_info) - 1):
            config_file.read_from_file(custom_info[x])
            label_info = str(config_file.read_from_file(custom_info[x]))
            if len(label_info) > 13:
                label_info = label_info[:13] + "..."
            self.labels[x].set_text(label_info)

        # Check for internet
        constants.has_internet = is_internet()
        text = ''
        if constants.has_internet:
            text = 'Connected'
        else:
            text = 'Not connected'
        self.labels[len(custom_info) - 1].set_text(text)

    # Takes you back to the introduction screen (on pressing prev button)
    def on_prev(self, arg2=None):
        global win
        # save last level?
        for i in win.changeable_content.get_children():
            win.changeable_content.remove(i)

        self.update_intro()

        win.changeable_content.pack_start(self.table, False, False, 0)

    # When clicking next in the default intro screen - takes you to the last level you visited
    def on_next(self, widget=None):
        if win.last_level_visited == 0:
            return

        for i in win.changeable_content.get_children():
            win.changeable_content.remove(i)

        self.state_to_widget(win.last_level_visited).activate(win, win.changeable_content, win.update)
        win.last_level_visited = win.state
        win.show_all()

    # On clicing a level button on default intro screen
    def go_to_level(self, widget):
        global win
        # Remove element in the dynamic box
        for i in win.changeable_content.get_children():
            win.changeable_content.remove(i)
        # Update current state
        win.state = widget.state + 1
        # Record this level so we can go back to it
        win.last_level_visited = win.state
        # Call next state
        self.state_to_widget(win.state).activate(win, win.changeable_content, win.update)
        # Refresh window
        win.show_all()

    # This updates the current level.
    def update(self, widget):
        returnValue = self.state_to_widget(win.state).apply_changes(widget)
        if returnValue == -1:
            return

        # Go back to intro screen
        self.on_prev()

    def state_to_widget(self, x):
        return {
            0: set_intro,
            1: set_keyboard,
            2: set_email,
            3: set_audio,
            4: set_display,
            5: set_wifi,
        }[x]


# On closing window, will alert if any of the listed booleans are True
def close_window(event="delete-event", button=win):

    if set_audio.reboot or set_display.reboot:
        #Bring in message dialog box

        dialog = Gtk.MessageDialog(button, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK, "So you know...")
        dialog.format_secondary_text(
            "..you will need to reboot to see all your changes")

        response = dialog.run()
        print("INFO dialog closed")

        if response == Gtk.ResponseType.OK:
            dialog.destroy()
            Gtk.main_quit()
            return
        else:
            dialog.destroy()
    else:
        Gtk.main_quit()
