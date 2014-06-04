#!/usr/bin/env python

# first_run.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the flow of the projects on the first run of Kano-settings

from gi.repository import Gtk
import os
import kano_settings.constants as constants
import kano_settings.set_intro as set_intro
import kano_settings.set_keyboard as set_keyboard
import kano_settings.set_audio as set_audio
import kano_settings.set_wifi.home as set_wifi_proxy
import kano.gtk3.kano_dialog as kano_dialog


win = None
MAX_STATE = 4


class First_Run():
    def __init__(self, _win):
        global win

        win = _win

    def update(self, widget=None, arg2=None):
        global win

        returnValue = self.state_to_widget(win.state).apply_changes(win.button.align)

        if returnValue == -1:
            return

        self.on_next()

    # When clicking previous arrow on first run through
    def on_prev(self, widget=None, arg2=None):
        global win

        # Check if we're in set_proxy screen
        if set_wifi_proxy.in_proxy:
            set_wifi_proxy.to_wifi()
            return

        # Update current state
        win.state = (win.state - 1)
        # Check we're in a valid state
        if win.state == -1:
            win.state = 0
            win.top_bar.disable_prev()
            return

        # Remove element in the dynamic box
        for i in win.changeable_content.get_children():
            win.changeable_content.remove(i)

        # Call next state
        self.state_to_widget(win.state).activate(win, win.changeable_content, win.button)
        self.update_next_button(win)

        # Refresh window
        win.show_all()

    # When clicking next arrow button on first run through
    def on_next(self, widget=None, arg2=None):
        global grid, box, state, win

        # If finished, needs a separate logic
        if win.state == MAX_STATE - 1:
            # Finished, so close window
            close_window()
            return

        # Update current state
        win.state = (win.state + 1)

        # Remove element in the dynamic box
        for i in win.changeable_content.get_children():
            win.changeable_content.remove(i)

        # Call next state
        self.state_to_widget(win.state).activate(win, win.changeable_content, win.button)
        self.update_next_button(win)

        # Refresh window
        win.show_all()

    # Apply Changes button needs to be updated depending on which level it's on
    def update_next_button(self, win):

        # Change label on Apply Changes button
        if win.state == MAX_STATE - 1:
            win.button.set_label("FINISH")
            win.top_bar.enable_prev()
            win.top_bar.disable_next()
        elif win.state == 0:
            win.button.set_label("GET STARTED")
            win.top_bar.disable_prev()
            win.top_bar.enable_next()
        else:
            win.button.set_label("NEXT")
            win.top_bar.enable_prev()
            win.top_bar.enable_next()

    def state_to_widget(self, x):
        return {
            0: set_intro,
            1: set_keyboard,
            2: set_audio,
            3: set_wifi_proxy,
        }[x]


# On closing window, will alert if any of the listed booleans are True
def close_window(event="delete-event", button=None):

    if constants.need_reboot:
        kdialog = kano_dialog.KanoDialog("Reboot?",
                                         "Your Kano needs to reboot for changes to apply",
                                         {"REBOOT NOW": {"return_value": 1}, "LATER": {"return_value": 0}})
        response = kdialog.run()
        if response == 1:
            os.system("sudo reboot")

    Gtk.main_quit()
