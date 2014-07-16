#!/usr/bin/env python

# set_font.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from gi.repository import Gtk
from kano.gtk3.heading import Heading
from kano.utils import get_user_unsudoed
import kano_settings.components.fixed_size_box as fixed_size_box
from kano.logging import logger
from .config_file import get_setting, set_setting, file_replace

selected_button = 0
initial_button = 0

SIZE_SMALL = 10
SIZE_NORMAL = 14
SIZE_BIG = 18

username = get_user_unsudoed()
config_file = os.path.join('/home', username, '.config/lxsession/LXDE/desktop.conf')


def activate(_win, box, button):
    global selected_button, initial_button

    title = Heading("Font", "Pick text size")
    box.pack_start(title.container, False, False, 0)

    # Settings container
    settings = fixed_size_box.Fixed()

    box.pack_start(settings.box, False, False, 0)

    # Slow radio button
    slow_button = Gtk.RadioButton.new_with_label_from_widget(None, "Small")
    slow_button.connect("toggled", on_button_toggled)
    slow_button.set_can_focus(True)
    slow_button.get_style_context().add_class("bold_toggle")
    slow_info = Gtk.Label("IDEAL FOR SMALL SCREENS")
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
    fast_button.set_label("Big")
    fast_button.connect("toggled", on_button_toggled)
    fast_button.set_can_focus(False)
    fast_button.get_style_context().add_class("bold_toggle")
    fast_info = Gtk.Label("BETTER FOR BIG SCREENS")
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

    #  Mode   size
    # Small    SIZE_SMALL
    # Normal   SIZE_NORMAL
    # Big      SIZE_BIG

    # Mode has no changed
    if initial_button == selected_button:
        return

    config = "Small"
    # Slow configuration
    if selected_button == 0:
        config = "Small"
    # Modest configuration
    elif selected_button == 1:
        config = "Normal"
    # Medium configuration
    elif selected_button == 2:
        config = "Big"

    # Update config
    set_setting("Font", config)


def change_font_size():

    font = "sGtk/FontName=Bariol "
    font_pattern = font + "[0-9][0-9]"

    # Small configuration
    if selected_button == 0:
        font += str(SIZE_SMALL)
    # Normal configuration
    elif selected_button == 1:
        font += str(SIZE_NORMAL)
    # Big configurations
    elif selected_button == 2:
        font += str(SIZE_BIG)

    logger.debug('set_font / change_font_size: selected_button:{}'.format(selected_button))

    # Apply changes
    file_replace(config_file, font_pattern, font)
    # Reload lxsession
    os.system("lxsession -r")


def current_setting():
    global initial_button

    font = get_setting("Font")
    if font == "Small":
        initial_button = 0
    elif font == "Normal":
        initial_button = 1
    elif font == "Big":
        initial_button = 2


def on_button_toggled(button):
    global selected_button

    if button.get_active():
        label = button.get_label()
        if label == "Small":
            selected_button = 0
        elif label == "Normal":
            selected_button = 1
        elif label == "Big":
            selected_button = 2
        # Apply changes so speed can be tested
        change_font_size()
