#!/usr/bin/env python

# set_overclock.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
import kano_settings.config_file as config_file
import kano_settings.components.heading as heading
import kano_settings.components.fixed_size_box as fixed_size_box
import os
import re

selected_button = 0
initial_button = 0


def file_replace(fname, pat, s_after):
    # first, see if the pattern is even in the file.
    with open(fname) as f:
        if not any(re.search(pat, line) for line in f):
            return -1  # pattern does not occur in file so we are done.

    # pattern is in the file, so perform replace operation.
    with open(fname) as f:
        out_fname = fname + ".tmp"
        out = open(out_fname, "w")
        for line in f:
            out.write(re.sub(pat, s_after, line))
        out.close()
        os.rename(out_fname, fname)


def activate(_win, box, update):
    global selected_button, initial_button

    title = heading.Heading("Mouse", "Pick your speed")
    box.pack_start(title.container, False, False, 0)

    # Settings container
    settings = fixed_size_box.Fixed()

    box.pack_start(settings.box, False, False, 0)

    # Slow radio button
    slow_button = Gtk.RadioButton.new_with_label_from_widget(None, "Slow")
    slow_button.connect("toggled", on_button_toggled)
    slow_button.set_can_focus(True)
    slow_button.get_style_context().add_class("bold_toggle")
    slow_info = Gtk.Label("REQUIRES LESS MOVE PRECISION")
    slow_info.get_style_context().add_class("normal_label")

    slow_box = Gtk.Box()
    slow_box.pack_start(slow_button, False, False, 0)
    slow_box.pack_start(slow_info, False, False, 0)

    # Normal radio button
    normal_button = Gtk.RadioButton.new_from_widget(slow_button)
    normal_button.set_label("Normal")
    normal_button.connect("toggled", on_button_toggled)
    normal_button.set_can_focus(False)
    normal_button.get_style_context().add_class("bold_toggle")
    normal_info = Gtk.Label("THE DEFAULT SETTING")
    normal_info.get_style_context().add_class("normal_label")

    normal_box = Gtk.Box()
    normal_box.pack_start(normal_button, False, False, 0)
    normal_box.pack_start(normal_info, False, False, 0)

    # Fast radio button
    fast_button = Gtk.RadioButton.new_from_widget(slow_button)
    fast_button.set_label("Fast")
    fast_button.connect("toggled", on_button_toggled)
    fast_button.set_can_focus(False)
    fast_button.get_style_context().add_class("bold_toggle")
    fast_info = Gtk.Label("BETTER FOR WIDE SCREENS")
    fast_info.get_style_context().add_class("normal_label")

    fast_box = Gtk.Box()
    fast_box.pack_start(fast_button, False, False, 0)
    fast_box.pack_start(fast_info, False, False, 0)

    radio_button_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    radio_button_container.pack_start(slow_box, False, False, 5)
    radio_button_container.pack_start(normal_box, False, False, 5)
    radio_button_container.pack_start(fast_box, False, False, 5)

    valign = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
    valign.set_padding(20, 0, 0, 0)
    valign.add(radio_button_container)
    settings.box.pack_start(valign, False, False, 0)

    # Show the current setting by electing the appropriate radio button
    current_setting()
    selected_button = initial_button
    if initial_button == 0:
        slow_button.set_active(True)
    elif initial_button == 1:
        normal_button.set_active(True)
    elif initial_button == 2:
        fast_button.set_active(True)

    # Add apply changes button under the main settings content
    box.pack_start(update.box, False, False, 0)
    update.enable()


def apply_changes(button):

    #  Mode   speed
    # Slow     1
    # Normal  default
    # High     10

    # Mode has no changed
    if initial_button == selected_button:
        return

    config = "Slow"
    # Slow configuration
    if selected_button == 0:
        config = "Slow"
    # Modest configuration
    elif selected_button == 1:
        config = "Normal"
    # Medium configuration
    elif selected_button == 2:
        config = "Fast"

    # Update config
    config_file.replace_setting("Mouse", config)


def change_mouse_speed():

    command = "xset m "
    # Slow configuration
    if selected_button == 0:
        command += "1"
    # Modest configuration
    elif selected_button == 1:
        command += "default"
    # Medium configuration
    elif selected_button == 2:
        command += "10"

    # Apply changes
    os.system(command)


def current_setting():
    global initial_button

    mouse = config_file.read_from_file("Mouse")
    if mouse == "Slow":
        initial_button = 0
    elif mouse == "Normal":
        initial_button = 1
    elif mouse == "Fast":
        initial_button = 2


def on_button_toggled(button):
    global selected_button

    if button.get_active():
        label = button.get_label()
        if label == "Slow":
            selected_button = 0
        elif label == "Normal":
            selected_button = 1
        elif label == "Fast":
            selected_button = 2
        # Apply changes so speed can be tested
        change_mouse_speed()
