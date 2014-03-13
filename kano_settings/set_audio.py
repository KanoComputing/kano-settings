#!/usr/bin/env python

# set_audio.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
import kano_settings.config_file as config_file
import kano_settings.components.heading as heading
import kano_settings.constants as constants
import os
import re

HDMI = False
reboot = False
file_name = "/etc/rc.local"
#file_name = "/home/caroline/blah"
current_img = None


def file_replace(fname, pat, s_after):
    # first, see if the pattern is even in the file.
    with open(fname) as f:
        if not any(re.search(pat, line) for line in f):
            print("FAIL: set_audio.py, file_replace, pattern not found in file")
            return -1  # pattern does not occur in file so we are done.

    # pattern is in the file, so perform replace operation.
    with open(fname) as f:
        out_fname = fname + ".tmp"
        out = open(out_fname, "w")
        for line in f:
            out.write(re.sub(pat, s_after, line))
        out.close()
        os.rename(out_fname, fname)


def activate(_win, box, apply_changes_button):
    global current_img

    title = heading.Heading("Audio settings", "Can you hear me?")

    # Settings container
    settings_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    settings_container.set_size_request(300, 250)
    box.add(settings_container)

    settings_container.pack_start(title.container, False, False, 0)

    # Analog radio button
    analog_button = Gtk.RadioButton.new_with_label_from_widget(None, "Analog")
    analog_button.set_can_focus(False)
    # HDMI radio button
    hdmi_button = Gtk.RadioButton.new_from_widget(analog_button)
    hdmi_button.set_label("HDMI")
    hdmi_button.connect("toggled", on_button_toggled)
    hdmi_button.set_can_focus(False)

    current_img = Gtk.Image()
    current_img.set_from_file(constants.files + "media/Graphics/Audio-jack.png")
    #current_img.set_from_file("media/Graphics/Audio-jack")
    radio_button_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    radio_button_container.pack_start(hdmi_button, False, False, 10)
    radio_button_container.pack_start(current_img, False, False, 10)
    radio_button_container.pack_start(analog_button, False, False, 10)

    settings_container.pack_start(radio_button_container, False, False, 0)

    # Show the current setting by electing the appropriate radio button
    current_setting(analog_button, hdmi_button)

    # Add apply changes button under the main settings content
    box.pack_start(apply_changes_button, False, False, 0)


def apply_changes(button):
    global HDMI, reboot, hdmi_img, analogue_img
    # amixer -c 0 cset numid=3 N
    # 1 analog
    # 2 hdmi

    pattern = "amixer -c 0 cset numid=3 [0-9]"
    new_line = None
    if HDMI is True:
        new_line = "amixer -c 0 cset numid=3 2"
        config = "HDMI"
    else:
        new_line = "amixer -c 0 cset numid=3 1"
        config = "Analogue"

    outcome = file_replace(file_name, pattern, new_line)
    # Don't continue if we don't manage to change the audio settings in the file.
    if outcome == -1:
        return

    config_file.replace_setting("Audio", config)
    # Tell user to reboot to see changes
    reboot = True


def current_setting(analogue_button, hdmi_button):

    f = open(file_name, 'r')
    file_string = str(f.read())
    analogue_string = "amixer -c 0 cset numid=3 1"
    hdmi_string = "amixer -c 0 cset numid=3 2"

    if file_string.find(analogue_string) != -1:
        analogue_button.set_active(True)

    elif file_string.find(hdmi_string) != -1:
        hdmi_button.set_active(True)


    # Default, first button is active


def on_button_toggled(button):
    global current_img, HDMI

    HDMI = button.get_active()

    if HDMI:
        current_img.set_from_file(constants.files + "media/Graphics/Audio-HDMI.png")

    else:
        current_img.set_from_file(constants.files + "media/Graphics/Audio-jack.png")
