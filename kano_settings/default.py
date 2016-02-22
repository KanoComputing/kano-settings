#!/usr/bin/env python

# default.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Function to restore factory default config.

from kano_settings.system.audio import set_to_HDMI
from kano_settings.boot_config import set_config_value, set_config_comment
from kano_settings.boot_config import end_config_transaction
from kano_settings.system.overclock import set_default_overclock_values
from kano_settings.system.keyboard_config import set_keyboard


def set_default_config():
    # restore factory defaults

    # setting the audio to analogue
    set_to_HDMI(False)

    set_config_value('hdmi_ignore_edid_audio', 1)
    set_config_value('hdmi_drive', None)

    # resetting HDMI settings
    set_config_value('disable_overscan', 1)
    set_config_value('overscan_left', 0)
    set_config_value('overscan_right', 0)
    set_config_value('overscan_top', 0)
    set_config_value('overscan_bottom', 0)
    set_config_value('hdmi_pixel_encoding', 2)
    set_config_value('hdmi_group', None)
    set_config_value('hdmi_mode', None)
    set_config_value('display_rotate', 0)
    set_config_comment('kano_screen_used', 'xxx')

    # resetting overclocking settings
    set_default_overclock_values()

    # set the keyboard to default
    set_keyboard('en_US', 'generic')

    end_config_transaction()
