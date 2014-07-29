#!/usr/bin/env python

# set_audio.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
import kano_settings.constants as constants
from kano_settings.templates import Template
from kano.logging import logger
from .config_file import get_setting, set_setting, file_replace


class SetAudio(Template):
    HDMI = False
    rc_local_path = "/etc/rc.audio"
    config_txt_path = "/boot/config.txt"

    def __init__(self, win):
        Template.__init__(self, "Audio", "Get sound", "APPLY CHANGES")

        self.win = win
        self.win.set_main_widget(self)

        self.top_bar.enable_prev()
        self.top_bar.set_prev_callback(self.win.go_to_home)

        self.kano_button.connect("button-release-event", self.apply_changes)

        # Analog radio button
        self.analog_button = Gtk.RadioButton.new_with_label_from_widget(None, "Speaker")

        # HDMI radio button
        self.hdmi_button = Gtk.RadioButton.new_from_widget(self.analog_button)
        self.hdmi_button.set_label("TV     ")
        self.hdmi_button.connect("toggled", self.on_button_toggled)

        # height is 106px
        self.current_img = Gtk.Image()
        self.current_img.set_from_file(constants.media + "/Graphics/Audio-jack.png")

        self.horizontal_box = Gtk.Box()
        self.horizontal_box.pack_start(self.hdmi_button, False, False, 10)
        self.horizontal_box.pack_start(self.current_img, False, False, 10)
        self.horizontal_box.pack_start(self.analog_button, False, False, 10)

        self.box.add(self.horizontal_box)
        self.align.set_padding(0, 0, 25, 0)

        # Show the current setting by electing the appropriate radio button
        self.current_setting()

        self.win.show_all()

    def apply_changes(self, widget, event):
        # amixer -c 0 cset numid=3 N
        # 1 analog
        # 2 hdmi

        # Uncomment/comment out the line  in /boot/config.txt
        amixer_from = "amixer -c 0 cset numid=3 [0-9]"
        edid_from = "#?hdmi_ignore_edid_audio=1"
        drive_from = "#?hdmi_drive=2"

        # These are the changes we'll apply if they have changed from what they were
        if self.HDMI is True:
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

        amixer_rc = file_replace(self.rc_local_path, amixer_from, amixer_to)
        edid_rc = file_replace(self.config_txt_path, edid_from, edid_to)
        drive_rc = file_replace(self.config_txt_path, drive_from, drive_to)

        # Don't continue if we don't manage to change the audio settings in the file.
        if amixer_rc == -1 or edid_rc == -1 or drive_rc == -1:
            logger.debug("set_audio / apply_changes: we couldn't manage to change all files")
            return

        set_setting('Audio', config)
        # Tell user to reboot to see changes
        constants.need_reboot = True

    def current_setting(self):
        f = open(self.rc_local_path, 'r')
        file_string = str(f.read())
        analogue_string = "amixer -c 0 cset numid=3 1"
        hdmi_string = "amixer -c 0 cset numid=3 2"

        if file_string.find(analogue_string) != -1:
            self.analog_button.set_active(True)

        elif file_string.find(hdmi_string) != -1:
            self.hdmi_button.set_active(True)

    def on_button_toggled(self, button):
        self.HDMI = button.get_active()

        if self.HDMI:
            self.current_img.set_from_file(constants.media + "/Graphics/Audio-HDMI.png")

        else:
            self.current_img.set_from_file(constants.media + "/Graphics/Audio-jack.png")
