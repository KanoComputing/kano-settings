#!/usr/bin/env python

# set_overclock.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
import kano_settings.config_file as config_file
import kano_settings.components.heading as heading
import kano_settings.constants as constants
import kano_settings.components.fixed_size_box as fixed_size_box
import os
import re

selected_button = 0
initial_button = 0
boot_config_file = "/boot/config.txt"


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

    title = heading.Heading("Overclocking", "Let\'s put some power here")
    box.pack_start(title.container, False, False, 0)

    # Settings container
    settings = fixed_size_box.Fixed()

    box.pack_start(settings.box, False, False, 0)

    # None radio button
    none_button = Gtk.RadioButton.new_with_label_from_widget(None, "None")
    none_button.connect("toggled", on_button_toggled)
    none_button.set_can_focus(True)

    # Modest radio button
    modest_button = Gtk.RadioButton.new_from_widget(none_button)
    modest_button.set_label("Modest")
    modest_button.connect("toggled", on_button_toggled)
    modest_button.set_can_focus(False)

    # Medium radio button
    medium_button = Gtk.RadioButton.new_from_widget(none_button)
    medium_button.set_label("Medium")
    medium_button.connect("toggled", on_button_toggled)
    medium_button.set_can_focus(False)

    # High radio button
    high_button = Gtk.RadioButton.new_from_widget(none_button)
    high_button.set_label("High")
    high_button.connect("toggled", on_button_toggled)
    high_button.set_can_focus(False)

    radio_button_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    radio_button_container.pack_start(none_button, False, False, 10)
    radio_button_container.pack_start(modest_button, False, False, 10)
    radio_button_container.pack_start(medium_button, False, False, 10)
    radio_button_container.pack_start(high_button, False, False, 10)

    valign = Gtk.Alignment(xalign=0.5, yalign=0, xscale=0, yscale=0)
    valign.add(radio_button_container)
    settings.box.pack_start(valign, False, False, 0)

    # Show the current setting by electing the appropriate radio button
    current_setting()
    selected_button = initial_button
    if initial_button == 0:
        none_button.set_active(True)
    elif initial_button == 1:
        modest_button.set_active(True)
    elif initial_button == 2:
        medium_button.set_active(True)
    elif initial_button == 3:
        high_button.set_active(True)

    # Add apply changes button under the main settings content
    box.pack_start(update.box, False, False, 0)
    update.enable()


def apply_changes(button):

    #  Mode      arm_freq    core_freq    sdram_freq   over_voltage
    # "None"   "700MHz ARM, 250MHz core, 400MHz SDRAM, 0 overvolt"
    # "Modest" "800MHz ARM, 300MHz core, 400MHz SDRAM, 0 overvolt"
    # "Medium" "900MHz ARM, 333MHz core, 450MHz SDRAM, 2 overvolt"
    # "High"   "950MHz ARM, 450MHz core, 450MHz SDRAM, 6 overvolt"

    # Mode has no changed
    if initial_button == selected_button:
        return

    config = "High"
    arm_freq = "arm_freq="
    core_freq = "core_freq="
    sdram_freq = "sdram_freq="
    over_voltage = "over_voltage="
    arm_freq_pattern = "arm_freq=[0-9][0-9][0-9]"
    core_freq_pattern = "core_freq=[0-9][0-9][0-9]"
    sdram_freq_pattern = "sdram_freq=[0-9][0-9][0-9]"
    over_voltage_pattern = "over_voltage=[0-9]"
    # None configuration
    if selected_button == 0:
        config = "None"
        arm_freq += "700"
        core_freq += "250"
        sdram_freq += "400"
        over_voltage += "0"
    # Modest configuration
    elif selected_button == 1:
        config = "Modest"
        arm_freq += "800"
        core_freq += "300"
        sdram_freq += "400"
        over_voltage += "0"
    # Medium configuration
    elif selected_button == 2:
        config = "Medium"
        arm_freq += "900"
        core_freq += "333"
        sdram_freq += "450"
        over_voltage += "2"
    # High configuration
    elif selected_button == 3:
        config = "High"
        arm_freq += "950"
        core_freq += "450"
        sdram_freq += "450"
        over_voltage += "6"

    # Apply changes
    file_replace(boot_config_file, arm_freq_pattern, arm_freq)
    file_replace(boot_config_file, core_freq_pattern, core_freq)
    file_replace(boot_config_file, sdram_freq_pattern, sdram_freq)
    file_replace(boot_config_file, over_voltage_pattern, over_voltage)

    # Update config
    config_file.replace_setting("Overclock", config)

    # Tell user to reboot to see changes
    constants.need_reboot = True


def current_setting():
    global initial_button

    f = open(boot_config_file, 'r')
    file_string = str(f.read())
    none_string = "core_freq=250"
    modest_string = "core_freq=300"
    medium_string = "core_freq=333"
    high_string = "core_freq=450"

    if file_string.find(none_string) != -1:
        initial_button = 0
    elif file_string.find(modest_string) != -1:
        initial_button = 1
    elif file_string.find(medium_string) != -1:
        initial_button = 2
    elif file_string.find(high_string) != -1:
        initial_button = 3


def on_button_toggled(button):
    global selected_button

    if button.get_active():
        label = button.get_label()
        if label == "None":
            selected_button = 0
        elif label == "Modest":
            selected_button = 1
        elif label == "Medium":
            selected_button = 2
        elif label == "High":
            selected_button = 3
