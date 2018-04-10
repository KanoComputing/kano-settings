#
# set_audio.py
#
# Copyright (C) 2014 - 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The Audio menu in Kano Settings.
#

from gi import require_version
require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk

from kano.logging import logger
from kano_peripherals.wrappers.detection import is_ck2_pro, get_ck2_pro_version

from kano_peripherals.wrappers.detection import CKC_V_1_1_0

import kano_settings.common as common
from kano_settings.templates import Template
from kano_settings.config_file import get_setting
from kano_settings.system.audio import set_to_HDMI, is_HDMI, is_hdmi_audio_supported, \
    is_analogue_audio_supported, get_alsa_config_max_dB, set_alsa_config_max_dB

from kano_settings.system.audio import DEFAULT_ALSA_CONFIG_MAX_DB, DEFAULT_CKC_V1_MAX_DB


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

        audio_overdrive_box = Gtk.Box()
        audio_overdrive_box.set_halign(Gtk.Align.CENTER)
        self.audio_overdrive_checkbutton = Gtk.CheckButton()
        self.audio_overdrive_checkbutton.set_label(_("Boost Volume"))
        self.audio_overdrive_checkbutton.get_style_context().add_class('bold_toggle')
        audio_overdrive_desc_label = Gtk.Label(_("Make your kit even louder"))
        audio_overdrive_desc_label.get_style_context().add_class('normal_label')
        audio_overdrive_box.pack_start(self.audio_overdrive_checkbutton, False, False, 10)
        audio_overdrive_box.pack_start(audio_overdrive_desc_label, False, False, 0)

        self.vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.vertical_box.pack_start(self.horizontal_box, False, False, 0)
        if self._show_audio_overdrive():
            self.vertical_box.pack_start(audio_overdrive_box, False, False, 10)

        self.box.add(self.vertical_box)
        self.align.set_padding(0, 0, 25, 0)

        # Show the current setting by electing the appropriate radio button
        self.current_setting()

        self.win.show_all()

    def apply_changes(self, widget, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

            audio_overdrive_changes = self._compare_and_set_audio_overdrive()
            common.need_reboot = audio_overdrive_changes

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

        # Set the initial tick state of for the audio overdrive button.
        self.initial_audio_overdrive = self._is_audio_overdrive()
        self.audio_overdrive_checkbutton.set_active(self.initial_audio_overdrive)

    def on_button_toggled(self, button):
        self.HDMI = button.get_active()

        if self.HDMI:
            self.current_img.set_from_file(common.media + "/Graphics/Audio-HDMI.png")
        else:
            self.current_img.set_from_file(common.media + "/Graphics/Audio-jack.png")

    def _is_audio_overdrive(self):
        """
        Check whether the Audio Overdrive option is enabled.

        Returns:
            bool - whether or not the ALSA maximum volume is set to the default maximum
        """
        return (get_alsa_config_max_dB() == DEFAULT_ALSA_CONFIG_MAX_DB)

    def _compare_and_set_audio_overdrive(self):
        """
        Sets the audio overdrive option if there was a change in the
        checkbutton state.

        Returns:
            bool - whether or not there were any changes made
        """
        if self.audio_overdrive_checkbutton.get_active() != self.initial_audio_overdrive:
            if self.audio_overdrive_checkbutton.get_active():
                max_dB = DEFAULT_ALSA_CONFIG_MAX_DB
            else:
                max_dB = DEFAULT_CKC_V1_MAX_DB
            set_alsa_config_max_dB(max_dB)
            return True

        return False

    def _show_audio_overdrive(self):
        """
        Check whether the audio overdrive option should be shown or not.

        This option is essentially for the CKCv1 to mitigate the speaker hardware.

        Return:
            bool - whether or not the option is to be shown
        """
        is_ckc = is_ck2_pro(retry_count=0)
        ckc_version = get_ck2_pro_version()

        return (is_ckc and ckc_version and ckc_version < CKC_V_1_1_0)
