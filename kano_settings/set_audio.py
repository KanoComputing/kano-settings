#!/usr/bin/env python

# set_audio.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Gdk
import kano_settings.common as common
from kano_settings.templates import Template
from kano.logging import logger
from kano_settings.config_file import get_setting
from kano_settings.system.audio import set_to_HDMI, is_HDMI, hdmi_supported


class SetAudio(Template):
    HDMI = False

    def __init__(self, win):
        Template.__init__(
            self,
            "Audio",
            "Get sound from your speaker or your TV",
            "APPLY CHANGES"
        )

        self.win = win
        self.win.set_main_widget(self)

        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.win.go_to_home)

        self.kano_button.connect("button-release-event", self.apply_changes)
        self.kano_button.connect("key-release-event", self.apply_changes)

        # Analog radio button
        self.analog_button = Gtk.RadioButton.new_with_label_from_widget(None, "Speaker")

        # HDMI radio button
        self.hdmi_button = Gtk.RadioButton.new_from_widget(self.analog_button)
        self.hdmi_button.set_label("TV     ")
        self.hdmi_button.connect("toggled", self.on_button_toggled)

        # height is 106px
        self.current_img = Gtk.Image()
        self.current_img.set_from_file(common.media + "/Graphics/Audio-jack.png")

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
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

            if (get_setting('Audio') == 'HDMI' and self.HDMI is True) or \
               (get_setting('Audio') == 'Analogue' and self.HDMI is False):

                logger.debug("set_audio / apply_changes: audio settings haven't changed, don't apply new changes")
                self.win.go_to_home()
                return

            set_to_HDMI(self.HDMI)

            # Tell user to reboot to see changes
            common.need_reboot = True
            self.win.go_to_home()

    def current_setting(self):
        if not hdmi_supported:
            self.hdmi_button.set_active(False)
            self.hdmi_button.set_sensitive(False)
            self.analog_button.set_active(True)
        else:
            hdmi = is_HDMI()
            self.hdmi_button.set_active(hdmi)
            self.analog_button.set_active(not hdmi)

    def on_button_toggled(self, button):
        self.HDMI = button.get_active()

        if self.HDMI:
            self.current_img.set_from_file(common.media + "/Graphics/Audio-HDMI.png")
        else:
            self.current_img.set_from_file(common.media + "/Graphics/Audio-jack.png")
