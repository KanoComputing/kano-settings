#!/usr/bin/env python

# auto_settings.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Perform all settings automatically
#

import kano_settings.set_keyboard as set_keyboard
import kano_settings.set_font as set_font
import kano_settings.set_mouse as set_mouse
import kano_settings.set_audio as set_audio
import kano_settings.set_overclock as set_overclock
from kano.logging import logger
from .config_file import get_setting


def auto_settings():
    logger.info('setting auto settings')

    # Keyboard
    continent = get_setting('Keyboard-continent-human')
    country = get_setting('Keyboard-country-human')
    variant = get_setting('Keyboard-variant-human')
    set_keyboard.auto_changes(continent, country, variant)

    # Font
    font = get_setting('Font')
    set_font.auto_changes(font)

    # Audio
    audio = get_setting('Audio')
    hdmi = (audio == 'HDMI')
    set_audio.auto_changes(hdmi)

    # Mouse
    mouse = get_setting('Mouse')
    set_mouse.auto_changes(mouse)

    # Overclocking
    overclock = get_setting('Overclocking')
    set_overclock.auto_changes(overclock)
