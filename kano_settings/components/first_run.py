#!/usr/bin/env python

# first_run.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the flow of the projects on the first run of Kano-settings

from gi.repository import Gtk
import kano_settings.set_intro as set_intro
import kano_settings.set_email as set_email
import kano_settings.set_keyboard as set_keyboard
import kano_settings.set_audio as set_audio
import kano_settings.set_display as set_display
import kano_settings.set_wifi as set_wifi
import kano_settings.config_file as config_file

win = None
MAX_STATE = 6


class First_Run():
    def __init__(self, _win):
        global win

        win = _win
        self.state = 0

        # Updates the current level and goes to the next (when clicking Next -> button in first run through levels).
    def update_and_next(self, widget):
        returnValue = self.state_to_widget(self.state).apply_changes(widget)
        if returnValue == -1:
            return

        self.on_next(widget)

    # When clicking previous arrow on first run through
    def on_prev(self, widget):
        global win

         # Update current state
        self.state = (self.state - 1)
        # Check we're in a valid state
        if self.state == -1:
            self.state = 0
            return

        # Remove element in the dynamic box
        for i in win.changable_content.get_children():
            win.changable_content.remove(i)

        # Call next state
        self.state_to_widget(self.state).activate(win, win.changable_content, win.apply_changes.button)

        # Change label on Apply Changes button
        if self.state == MAX_STATE - 1:
            win.apply_changes.text.set_text("Finish!")
        elif self.state > 0:
            win.apply_changes.text.set_text("Next")
        else:
            win.apply_changes.text.set_text("Get started")
        # Refresh window
        win.show_all()

    # When clicking next arrow button on first run through
    def on_next(self, widget):
        global grid, box, state, win

        # Update current state
        self.state = (self.state + 1)
        # If we've clicked on the finished
        if self.state == MAX_STATE:
            # Write to config file to say we've completed the level.
            config_file.replace_setting("Completed", "1")
            # Finished, so close window
            close_window()
            return

        # Remove element in the dynamic box
        for i in win.changable_content.get_children():
            win.changable_content.remove(i)

        # Call next state
        self.state_to_widget(self.state).activate(win, win.changable_content, win.apply_changes.button)

        # Change label on Apply Changes button
        if self.state == MAX_STATE - 1:
            win.apply_changes.text.set_text("Finish!")
        elif self.state > 0:
            win.apply_changes.text.set_text("Next")
        else:
            win.apply_changes.text.set_text("Get started")
        # Refresh window
        win.show_all()

    def state_to_widget(self, x):
        return {
            0: set_intro,
            1: set_email,
            2: set_keyboard,
            3: set_audio,
            4: set_wifi,
            5: set_display,
        }[x]


# On closing window, will alert if any of the listed booleans are True
def close_window(event="delete-event", button=win):

    if set_audio.reboot or set_display.reboot:
        #Bring in message dialog box
        dialog = Gtk.MessageDialog(
            button, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "So you know...")
        dialog.format_secondary_text("..you will need to reboot to see all your changes")
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
