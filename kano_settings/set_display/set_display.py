#!/usr/bin/env python

# set_display.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
from kano.gtk3.heading import Heading
import kano_settings.components.fixed_size_box as fixed_size_box
import kano_settings.constants as constants
from ..boot_config import set_config_comment
from .functions import get_model, list_supported_modes, set_hdmi_mode, read_hdmi_mode, \
    find_matching_mode

mode = 'auto'
mode_index = 0
button = None
model = None
CONTAINER_HEIGHT = 70


def activate(_win, box, _button, overscan_button):
    global button, model

    button = _button
    button.set_sensitive(False)

    # Get display name
    model = get_model()

    title = Heading("Display", model)
    box.pack_start(title.container, False, False, 0)

    # Contains main buttons
    settings = fixed_size_box.Fixed()

    box.pack_start(settings.box, False, False, 0)

    horizontal_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=40)
    horizontal_container.set_valign(Gtk.Align.CENTER)

    # HDMI mode combo box
    mode_combo = Gtk.ComboBoxText.new()
    mode_combo.connect("changed", on_mode_changed)

    # Fill list of modes
    modes = list_supported_modes()
    mode_combo.append_text("auto")
    if modes:
        for v in modes:
            mode_combo.append_text(v)

    horizontal_container.pack_start(mode_combo, False, False, 0)
    mode_combo.props.valign = Gtk.Align.CENTER

    # Select the current setting in the dropdown list
    saved_group, saved_mode = read_hdmi_mode()
    active_item = find_matching_mode(modes, saved_group, saved_mode)
    mode_combo.set_active(active_item)

    # Overscan button
    overscan_button.set_label("Overscan")
    horizontal_container.pack_end(overscan_button, False, False, 0)

    valign = Gtk.Alignment(xalign=0.5, yalign=0, xscale=0, yscale=0)
    padding_above = (settings.height - CONTAINER_HEIGHT) / 2
    valign.set_padding(padding_above, 0, 0, 0)
    valign.add(horizontal_container)
    settings.box.pack_start(valign, False, False, 0)

    # Add apply changes button under the main settings content
    box.pack_start(button.align, False, False, 0)
    _win.show_all()


def apply_changes(button):
    global model

    # Set HDMI mode
    # Get mode:group string
    # Of the form "auto" or "cea:1" or "dmt:1" etc.
    parse_mode = mode.split(" ")[0]

    set_hdmi_mode_from_str(parse_mode)
    set_config_comment('kano_screen_used', model)

    constants.need_reboot = True


def on_mode_changed(combo):
    global mode, mode_index, button

    #  Get the selected mode
    tree_iter = combo.get_active_iter()
    if tree_iter is not None:
        model = combo.get_model()
        mode = model[tree_iter][0]

    mode_index = combo.get_active()

    button.set_sensitive(True)


def set_hdmi_mode_from_str(mode):
    print mode
    if mode == "auto":
        set_hdmi_mode()
        return

    group, number = mode.split(":")
    set_hdmi_mode(group, number)


