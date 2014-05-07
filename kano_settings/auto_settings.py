#!/usr/bin/env python

# auto_settings.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Perform all settings automatically
#

import kano_settings.set_keyboard as set_keyboard
import kano_settings.set_mouse as set_mouse
import kano_settings.set_audio as set_audio
import kano_settings.set_overclock as set_overclock
import kano_settings.config_file as config_file


def auto_settings():
    # Keyboard
    continent = config_file.read_from_file("Keyboard-continent-human")
    country = config_file.read_from_file("Keyboard-country-human")
    variant = config_file.read_from_file("Keyboard-variant-human")
    set_keyboard.auto_changes(continent, country, variant)

    # Audio
    audio = config_file.read_from_file("Audio")
    hdmi = (audio == 'HDMI')
    set_audio.auto_changes(hdmi)

    # Mouse
    mouse = config_file.read_from_file("Mouse")
    set_mouse.auto_changes(mouse)

    # Overclocking
    overclock = config_file.read_from_file("Overclocking")
    set_overclock.auto_changes(overclock)
