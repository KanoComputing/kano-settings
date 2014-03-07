#!/usr/bin/env python3

# set_audio.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Pango
import os
import re

HDMI = False
reboot = False
file_name = "/etc/rc.local"

def file_replace(fname, pat, s_after):
    # first, see if the pattern is even in the file.
    with open(fname) as f:
        if not any(re.search(pat, line) for line in f):
            return  # pattern does not occur in file so we are done.

    # pattern is in the file, so perform replace operation.
    with open(fname) as f:
        out_fname = fname + ".tmp"
        out = open(out_fname, "w")
        for line in f:
            out.write(re.sub(pat, s_after, line))
        out.close()
        os.rename(out_fname, fname)


def activate(_win, box, apply_changes):

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

    # Settings container
    settings_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    settings_container.set_size_request(500, 250)
    box.add(settings_container)

    settings_container.pack_start(title_container, False, False, 0)

    # Title
    title.set_text("Audio settings")

    # Description
    description.set_text("Can you hear me?")

    # Analog radio button
    analog_button = Gtk.RadioButton.new_with_label_from_widget(None, "Analog")
    # HDMI radio button
    hdmi_button = Gtk.RadioButton.new_from_widget(analog_button)
    hdmi_button.set_label("HDMI")
    hdmi_button.connect("toggled", on_button_toggled)

    img = Gtk.Image()
    img.set_from_file("media/Graphics/Audio-jack.png")

    radio_button_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    radio_button_container.pack_start(hdmi_button, False, False, 10)
    radio_button_container.pack_start(img, False, False, 10)
    radio_button_container.pack_start(analog_button, False, False, 10)

    settings_container.pack_start(radio_button_container, False, False, 0)

    # Show the current setting by electing the appropriate radio button
    current_setting(analog_button, hdmi_button)

    # Add apply changes button under the main settings content
    box.pack_start(apply_changes, False, False, 0)


def apply_changes(button):
    global HDMI, reboot
    # amixer -c 0 cset numid=3 N
    # 1 analog
    # 2 hdmi

    pattern = "amixer -c 0 cset numid=3 [0-9]"
    new_line = None
    if HDMI is True:
        new_line = "amixer -c 0 cset numid=3 2"
    else:
        new_line = "amixer -c 0 cset numid=3 1"

    file_replace(file_name, pattern, new_line)
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
    global HDMI

    HDMI = button.get_active()
