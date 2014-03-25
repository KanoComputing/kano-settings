#!/usr/bin/env python

# set_display.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Pango
import kano_settings.config_file as config_file
import kano_settings.screen.screen_config as screen_config
import kano_settings.components.heading as heading
import kano_settings.components.fixed_size_box as fixed_size_box
import kano.utils as utils

mode = 'auto'
mode_index = 0
overscan = False
reboot = False
update = None
display_name = None
CONTAINER_HEIGHT = 70


def activate(_win, box, _update):
    global update, display_name

    update = _update
    update.disable()

    read_config()

    # Get display name
    cmd = '/opt/vc/bin/tvservice -n'
    display_name, _, _ = utils.run_cmd(cmd)
    display_name = display_name[12:].rstrip()

    title = heading.Heading("Display - " + display_name, "How sharp can you go?")
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
    modes = screen_config.list_supported_modes()
    mode_combo.append_text("auto")
    if modes is not None:
        for v in modes:
            mode_combo.append_text(v)

    horizontal_container.pack_start(mode_combo, False, False, 0)
    mode_combo.props.valign = Gtk.Align.CENTER

    # Overscan check button
    check_button = Gtk.CheckButton("Overscan?")
    check_button.set_can_focus(False)
    check_button.modify_font(Pango.FontDescription("Bariol 14"))
    check_button.props.valign = Gtk.Align.CENTER
    check_button.connect("clicked", on_button_toggled)

    # Select the current setting in the dropdown list
    set_defaults("resolution", mode_combo)
    # Check overscan option appropriately
    set_defaults("overscan", combo=None, button=check_button)

    horizontal_container.pack_start(check_button, False, False, 0)

    valign = Gtk.Alignment(xalign=0.5, yalign=0, xscale=0, yscale=0)
    padding_above = (settings.height - CONTAINER_HEIGHT) / 2
    valign.set_padding(padding_above, 0, 0, 0)
    valign.add(horizontal_container)
    settings.box.pack_start(valign, False, False, 0)

    # Add apply changes button under the main settings content
    box.pack_start(update.box, False, False, 0)


def apply_changes(button):
    global reboot

    # Set HDMI mode
    # Get mode:group string
    # Of the form "auto" or "cea:1" or "dmt:1" etc.
    parse_mode = mode.split(" ")[0]

    screen_config.set_hdmi_mode(parse_mode)
    # Set overscan
    if overscan is True:
        screen_config.set_config_option("disable_overscan", 0)
    else:
        screen_config.set_config_option("disable_overscan", 1)

    update_config()
    reboot = True


def read_config():
    global mode, mode_index, overscan

    mode = config_file.read_from_file("Display-mode")
    mode_index = config_file.read_from_file("Display-mode-index")
    overscan = config_file.read_from_file("Display-overscan")


def update_config():

    # Add new configurations to config file.
    config_file.replace_setting("Display-name", display_name)
    config_file.replace_setting("Display-mode", str(mode))
    config_file.replace_setting("Display-mode-index", str(mode_index))
    config_file.replace_setting("Display-overscan", str(overscan))


# setting = "resolution" or "overscan"
def set_defaults(setting, combo=None, button=None):

    # Set the default info on the dropdown lists
    if setting == "overscan":
        # set current state of button to be active or not.
        active_item = int(config_file.read_from_file("Display-overscan"))
        button.set_active(active_item)

    elif setting == "resolution":
        # set the active dropdown item to the config.
        active_item = int(config_file.read_from_file("Display-mode-index"))
        combo.set_active(active_item)


def on_button_toggled(button):
    global overscan

    overscan = int(button.get_active())


def on_mode_changed(combo):
    global mode, mode_index, update

    #  Get the selected mode
    tree_iter = combo.get_active_iter()
    if tree_iter is not None:
        model = combo.get_model()
        mode = model[tree_iter][0]

    mode_index = combo.get_active()

    update.enable()
