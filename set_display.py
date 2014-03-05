#!/usr/bin/env python3

# set_display.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
import screen_config

mode = 'auto'
overscan = False
reboot = False

def activate(_win, table, box):

    # Table
    table = Gtk.Table(5, 1, True)
    box.add(table)

    # Label
    label = Gtk.Label()
    label.set_text("Display")
    label.set_justify(Gtk.Justification.LEFT)
    table.attach(label, 0, 1, 0, 1)

    # HDMI mode combo box
    mode_combo = Gtk.ComboBoxText.new()
    mode_combo.connect("changed", on_mode_changed)
    # Fill list of modes
    modes = screen_config.list_supported_modes()
    mode_combo.append_text("auto")
    if modes is not None:
        for v in modes:
            mode_combo.append_text(v)
    table.attach(mode_combo, 0, 1, 1, 2)

    # Overscan-no radio button
    button1 = Gtk.RadioButton.new_with_label_from_widget(None, "Overscan no")
    table.attach(button1, 0, 1, 2, 3)
    # Overscan-yes radio button
    button2 = Gtk.RadioButton.new_from_widget(button1)
    button2.set_label("Overscan yes")
    button2.connect("toggled", on_button_toggled)
    table.attach(button2, 0, 1, 3, 4)

    # Apply button
    button = Gtk.Button("Apply changes")
    button.connect("clicked", apply_changes)
    table.attach(button, 0, 1, 4, 5)


def apply_changes(button):

    # Set HDMI mode
    # Get mode:group string
    parse_mode = mode.split(" ")[0]
    screen_config.set_hdmi_mode(parse_mode)
    # Set overscan
    if overscan is True:
        screen_config.set_config_option("disable_overscan", 0)
    else:
        screen_config.set_config_option("disable_overscan", 1)

    # Display message to tell user to reboot to see changes.
    reboot = True


def on_button_toggled(button):
    global overscan

    overscan = button.get_active()


def on_mode_changed(combo):
    global mode

    #  Get the selected mode
    tree_iter = combo.get_active_iter()
    if tree_iter is not None:
        model = combo.get_model()
        mode = model[tree_iter][0]
