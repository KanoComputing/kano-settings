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
from kano_settings.system.audio import set_to_HDMI, is_HDMI, is_hdmi_audio_supported, \
    is_analogue_audio_supported


class SetAudio(Template):
    HDMI = False

    def __init__(self, win):
        Template.__init__(
            self,
            _("Audio"),
            _("Get sound from your speaker or your TV"),
            _("APPLY CHANGES")
        )

        self.win = win
        self.win.set_main_widget(self)

        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.win.go_to_home)

        self.kano_button.connect('button-release-event', self.apply_changes)
        self.kano_button.connect('key-release-event', self.apply_changes)

        # Analog radio button
        self.analog_button = Gtk.RadioButton.new_with_label_from_widget(None, _("Speaker"))
        # TODO: This message should come from is_analogue_audio_supported() and in
        # turn from whomever disabled it. This is the only case we have for now.
        self.disabled_analogue_label = Gtk.Label(_(
            "To play sound through a\n"
            "speaker, remove your kit's light\n"
            "hat and re-open this menu"
        ))

        # HDMI radio button

        self.hdmi_button = Gtk.RadioButton.new_from_widget(self.analog_button)
        self.hdmi_button.set_label(_("TV     "))
        self.hdmi_button.connect('toggled', self.on_button_toggled)
        hdmi_button_align = Gtk.Alignment(xalign=1, xscale=0, yalign=0, yscale=0)
        hdmi_button_align.add(self.hdmi_button)
        # TODO: This message should come from is_hdmi_audio_supported() and in
        # turn from whomever disabled it. This is the only case we have for now.
        self.disabled_hdmi_label = Gtk.Label(_(
            "To play sound through HDMI,\n"
            "connect to a screen with\n"
            "speakers"
        ))
        disabled_hdmi_label_align = Gtk.Alignment(xalign=1, xscale=0, yalign=0, yscale=0)
        disabled_hdmi_label_align.add(self.disabled_hdmi_label)

        # height is 106px
        self.current_img = Gtk.Image()
        self.current_img.set_from_file(common.media + "/Graphics/Audio-jack.png")

        self.hdmi_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.hdmi_box.pack_start(Gtk.Label(_("\n\n")), False, False, 10)
        self.hdmi_box.pack_start(hdmi_button_align, False, False, 10)
        self.hdmi_box.pack_start(disabled_hdmi_label_align, False, False, 10)

        self.analogue_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.analogue_box.pack_start(Gtk.Label(_("\n\n")), False, False, 10)
        self.analogue_box.pack_start(self.analog_button, False, False, 10)
        self.analogue_box.pack_start(self.disabled_analogue_label, False, False, 10)

        self.horizontal_box = Gtk.Box()
        self.horizontal_box.pack_start(self.hdmi_box, False, False, 10)
        self.horizontal_box.pack_start(self.current_img, False, False, 10)
        self.horizontal_box.pack_start(self.analogue_box, False, False, 10)

        self.box.add(self.horizontal_box)
        self.align.set_padding(0, 0, 25, 0)

        # Show the current setting by electing the appropriate radio button
        self.current_setting()

        self.win.show_all()

    def apply_changes(self, widget, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

            if (get_setting('Audio') == _('HDMI') and self.HDMI is True) or \
               (get_setting('Audio') == _('Analogue') and self.HDMI is False):

                logger.debug("set_audio / apply_changes: audio settings haven't changed, don't apply new changes")
                self.win.go_to_home()
                return

            set_to_HDMI(self.HDMI)

            # Tell user to reboot to see changes
            common.need_reboot = True
            self.win.go_to_home()

    def current_setting(self):
        hdmi_supported = is_hdmi_audio_supported()
        analogue_supported = is_analogue_audio_supported()
        hdmi_selected = is_HDMI()

        if not hdmi_supported:
            self.disabled_hdmi_label.get_style_context().add_class('normal_label')

        if not analogue_supported:
            self.disabled_analogue_label.get_style_context().add_class('normal_label')

        # Disable radio buttons based on available features.
        self.hdmi_button.set_sensitive(hdmi_supported)
        self.analog_button.set_sensitive(analogue_supported)

        # Tick the radio button based on what is set on the system.
        self.hdmi_button.set_active(hdmi_selected)
        self.analog_button.set_active(not hdmi_selected)

    def on_button_toggled(self, button):
        self.HDMI = button.get_active()

        if self.HDMI:
            self.current_img.set_from_file(common.media + "/Graphics/Audio-HDMI.png")
        else:
            self.current_img.set_from_file(common.media + "/Graphics/Audio-jack.png")
