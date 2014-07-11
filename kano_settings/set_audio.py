#!/usr/bin/env python

# set_audio.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
from kano.gtk3.heading import Heading
import kano_settings.constants as constants
import kano_settings.components.fixed_size_box as fixed_size_box
from kano.logging import logger
from .config_file import get_setting, set_setting, file_replace


HDMI = False
rc_local_path = "/etc/rc.audio"
config_txt_path = "/boot/config.txt"
current_img = None
# Change this value (IMG_HEIGHT) to move the image up or down.
IMG_HEIGHT = 130


def activate(_win, box, button):
    global current_img

    title = Heading("Audio", "Get sound")

    # Settings container
    settings = fixed_size_box.Fixed()

    box.pack_start(title.container, False, False, 0)
    box.pack_start(settings.box, False, False, 0)

    # Analog radio button
    analog_button = Gtk.RadioButton.new_with_label_from_widget(None, "Speaker")

    # HDMI radio button
    hdmi_button = Gtk.RadioButton.new_from_widget(analog_button)
    hdmi_button.set_label("TV     ")
    hdmi_button.connect("toggled", on_button_toggled)

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
    box.pack_start(button.align, False, False, 0)
    button.set_sensitive(True)

    _win.show_all()


def apply_changes(button):
    global HDMI, hdmi_img
    # amixer -c 0 cset numid=3 N
    # 1 analog
    # 2 hdmi

    # Uncomment/comment out the line  in /boot/config.txt
    amixer_from = "amixer -c 0 cset numid=3 [0-9]"
    edid_from = "#?hdmi_ignore_edid_audio=1"
    drive_from = "#?hdmi_drive=2"

    # These are the changes we'll apply if they have changed from what they were
    if HDMI is True:
        amixer_to = "amixer -c 0 cset numid=3 2"
        edid_to = "#hdmi_ignore_edid_audio=1"
        drive_to = "hdmi_drive=2"
        config = "HDMI"
    else:
        amixer_to = "amixer -c 0 cset numid=3 1"
        edid_to = "hdmi_ignore_edid_audio=1"
        drive_to = "#hdmi_drive=2"
        config = "Analogue"

    # if audio settings haven't changed, don't apply new changes
    if get_setting('Audio') == config:
        logger.debug("set_audio / apply_changes: audio settings haven't changed, don't apply new changes")
        return

    amixer_rc = file_replace(rc_local_path, amixer_from, amixer_to)
    edid_rc = file_replace(config_txt_path, edid_from, edid_to)
    drive_rc = file_replace(config_txt_path, drive_from, drive_to)

    # Don't continue if we don't manage to change the audio settings in the file.
    if amixer_rc == -1 or edid_rc == -1 or drive_rc == -1:
        logger.debug("set_audio / apply_changes: we couldn't manage to change all files")
        return

    set_setting('Audio', config)
    # Tell user to reboot to see changes
    constants.need_reboot = True


# This function is used by auto_settings
def auto_changes(hdmi):
    logger.info('set_audio/auto_changes: hdmi:{}'.format(hdmi))

    # Uncomment/comment out the line  in /boot/config.txt
    edid_from = "#?hdmi_ignore_edid_audio=1"
    amixer_from = "amixer -c 0 cset numid=3 [0-9]"
    amixer_to = None
    edid_to = None

    if hdmi is True:
        amixer_to = "amixer -c 0 cset numid=3 2"
        edid_to = "#hdmi_ignore_edid_audio=1"
    else:
        amixer_to = "amixer -c 0 cset numid=3 1"
        edid_to = "hdmi_ignore_edid_audio=1"

    file_replace(rc_local_path, amixer_from, amixer_to)
    file_replace(config_txt_path, edid_from, edid_to)


def current_setting(analogue_button, hdmi_button):

    f = open(rc_local_path, 'r')
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
