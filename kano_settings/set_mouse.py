#!/usr/bin/env python

# set_mouse.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from gi.repository import Gtk
from kano.gtk3.heading import Heading
import kano_settings.components.fixed_size_box as fixed_size_box
from kano.logging import logger
from .config_file import get_setting, set_setting

selected_button = 0
initial_button = 0


def activate(_win, box, button):
    global selected_button, initial_button

    title = Heading("Mouse", "Pick your speed")
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
    box.pack_start(button.align, False, False, 0)
    button.set_sensitive(True)

    _win.show_all()


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
    set_setting("Mouse", config)


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

    logger.debug('set_mouse / change_mouse_speed: selected_button:{}'.format(selected_button))

    # Apply changes
    os.system(command)


def current_setting():
    global initial_button

    mouse = get_setting("Mouse")
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
