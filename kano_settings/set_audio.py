#!/usr/bin/env python

# set_audio.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import re

from gi.repository import Gtk
from kano.gtk3.heading import Heading
import kano_settings.constants as constants
import kano_settings.components.fixed_size_box as fixed_size_box
from .config_file import get_setting, set_setting


HDMI = False
file_name_rc_local = "/etc/rc.local"
file_name_boot_config = "/boot/config.txt"
current_img = None
# Change this value (IMG_HEIGHT) to move the image up or down.
IMG_HEIGHT = 130


def file_replace(fname, pat, s_after):
    if not os.path.exists(fname):
        return

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
    global current_img

    title = Heading("Audio", "Get sound")

    # Settings container
    settings = fixed_size_box.Fixed()

    box.pack_start(title.container, False, False, 0)
    box.pack_start(settings.box, False, False, 0)

    # Analog radio button
    analog_button = Gtk.RadioButton.new_with_label_from_widget(None, "Speaker")
    analog_button.set_can_focus(False)

    # HDMI radio button
    hdmi_button = Gtk.RadioButton.new_from_widget(analog_button)
    hdmi_button.set_label("TV     ")
    hdmi_button.connect("toggled", on_button_toggled)
    hdmi_button.set_can_focus(False)

    # height is 106px
    current_img = Gtk.Image()
    current_img.set_from_file(constants.media + "/Graphics/Audio-jack.png")

    radio_button_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    radio_button_container.pack_start(hdmi_button, False, False, 10)
    radio_button_container.pack_start(current_img, False, False, 10)
    radio_button_container.pack_start(analog_button, False, False, 10)

    valign = Gtk.Alignment(xalign=0.5, yalign=0, xscale=0, yscale=0)
    padding_above = (settings.height - IMG_HEIGHT) / 2
    valign.set_padding(padding_above, 0, 0, 0)
    valign.add(radio_button_container)
    settings.box.pack_start(valign, False, False, 0)

    # Show the current setting by electing the appropriate radio button
    current_setting(analog_button, hdmi_button)

    # Add apply changes button under the main settings content
    box.pack_start(update.align, False, False, 0)
    update.set_sensitive(True)


def apply_changes(button):
    global HDMI, hdmi_img
    # amixer -c 0 cset numid=3 N
    # 1 analog
    # 2 hdmi

    # Uncomment/comment out the line  in /boot/config.txt
    boot_config = "#?hdmi_ignore_edid_audio=1"
    rc_local = "amixer -c 0 cset numid=3 [0-9]"
    new_rc_local = None
    new_boot_config = None
    config = ""

    # These are the changes we'll apply if they have changed from what they were
    if HDMI is True:
        new_rc_local = "amixer -c 0 cset numid=3 2"
        new_boot_config = "#hdmi_ignore_edid_audio=1"
        config = "HDMI"
    else:
        new_rc_local = "amixer -c 0 cset numid=3 1"
        new_boot_config = "hdmi_ignore_edid_audio=1"
        config = "Analogue"

    # if audio settings haven't changed, don't apply new changes
    if get_setting('Audio') == config:
        return

    outcome_rc = file_replace(file_name_rc_local, rc_local, new_rc_local)
    outcome_boot = file_replace(file_name_boot_config, boot_config, new_boot_config)
    # Don't continue if we don't manage to change the audio settings in the file.
    if outcome_rc == -1 or outcome_boot == -1:
        return

    set_setting('Audio', config)
    # Tell user to reboot to see changes
    constants.need_reboot = True


# This function is used by auto_settings
def auto_changes(hdmi):
    # Uncomment/comment out the line  in /boot/config.txt
    boot_config = "#?hdmi_ignore_edid_audio=1"
    rc_local = "amixer -c 0 cset numid=3 [0-9]"
    new_rc_local = None
    new_boot_config = None

    if hdmi is True:
        new_rc_local = "amixer -c 0 cset numid=3 2"
        new_boot_config = "#hdmi_ignore_edid_audio=1"
    else:
        new_rc_local = "amixer -c 0 cset numid=3 1"
        new_boot_config = "hdmi_ignore_edid_audio=1"

    file_replace(file_name_rc_local, rc_local, new_rc_local)
    file_replace(file_name_boot_config, boot_config, new_boot_config)


def current_setting(analogue_button, hdmi_button):

    f = open(file_name_rc_local, 'r')
    file_string = str(f.read())
    analogue_string = "amixer -c 0 cset numid=3 1"
    hdmi_string = "amixer -c 0 cset numid=3 2"

    if file_string.find(analogue_string) != -1:
        analogue_button.set_active(True)

    elif file_string.find(hdmi_string) != -1:
        hdmi_button.set_active(True)


def on_button_toggled(button):
    global current_img, HDMI

    HDMI = button.get_active()

    if HDMI:
        current_img.set_from_file(constants.media + "/Graphics/Audio-HDMI.png")

    else:
        current_img.set_from_file(constants.media + "/Graphics/Audio-jack.png")
