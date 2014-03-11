#!/usr/bin/env python3

# set_display.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Pango
import kano_settings.screen_config as screen_config

mode = 'auto'
overscan = False
reboot = False

def activate(_win, box, apply_changes_button):

    title = Gtk.Label("TITLE")
    title.modify_font(Pango.FontDescription("Bariol 16"))
    description = Gtk.Label("Description of project")
    description.modify_font(Pango.FontDescription("Bariol 14"))

    title_style = title.get_style_context()
    title_style.add_class('title')

    description_style = description.get_style_context()
    description_style.add_class('description')

    title_container = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing=0)
    title_container.add(title)
    title_container.set_size_request(300, 100)
    title_container.pack_start(description, True, True, 10)
    info_style = title_container.get_style_context()
    info_style.add_class('title_container')

    # Conatins main buttons
    settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    settings_box.set_size_request(300, 250)
    box.add(settings_box)
    settings_box.pack_start(title_container, False, False, 0)

    # Title
    title.set_text("Display - how sharp can you go?")

    # Description
    description.set_text("Make the OS look the best it can")

    horizontal_container = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, spacing=20)
    horizontal_container.set_valign(Gtk.Align.CENTER)
    settings_box.pack_start(horizontal_container, False, False, 0)
    horizontal_container.set_size_request(300, 120)

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

    # Overscan-no radio button
    button1 = Gtk.CheckButton("Overscan?")
    button1.set_can_focus(False)
    button1.modify_font(Pango.FontDescription("Bariol 14"))
    button1.props.valign = Gtk.Align.CENTER

    horizontal_container.pack_start(button1, False, False, 0)

    # Overscan-yes radio button
    #button2 = Gtk.RadioButton.new_from_widget(button1)
    #button2.set_label("Overscan yes")
    #button2.connect("toggled", on_button_toggled)
    #horizontal_container.pack_start(button2, False, False, 0)

    # Add apply changes button under the main settings content
    box.pack_start(apply_changes_button, False, False, 0)


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
