#!/usr/bin/env python

# keyboard_config.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This script is an interactive selection of the keyboard, based on country name and local keyboard variant.
#

import os
import json
import kano_settings.keyboard.keyboard_layouts as keyboard_layouts
from kano_settings.config_file import get_setting

# GLOBAL variables
keyboard_conffile = '/etc/default/keyboard'


# Given a country name return the keyboard layout code
def find_country_code(country_name, layout):
    for l in layout:
        if l.upper() == country_name.upper():
            return layout[l]
    return None


# Return list of keyboard variants for a given country
def find_keyboard_variants(country_code):
    try:
        return sorted(keyboard_layouts.variants[country_code])
    except:
        # It means this country code does not have keyboard variants
        return None

def is_changed(country_code, variant):
    continent = get_setting('Keyboard-continent-human')
    country = get_setting('Keyboard-country-human')

    stored_variant = get_setting('Keyboard-variant-human').lower()
    stored_layout = keyboard_layouts.layouts[continent][country].lower()

    if variant == 'generic':
        variant = ''

    return (country_code != stored_layout or variant != stored_variant)


def set_keyboard(country_code, variant):
    if variant == 'generic':
        variant = ''

    # Make new settings take effect now
    os.system("setupcon -k 2>/dev/null || true")
    os.system('setupcon -k --save-only || true')

    # Notify and apply changes to the XServer
    os.system("setxkbmap {} {} > /dev/null 2>&1".format(country_code, variant))


def set_saved_keyboard():
    continent = get_setting('Keyboard-continent-human')
    country = get_setting('Keyboard-country-human')
    variant = get_setting('Keyboard-variant-human')

    layout = keyboard_layouts.layouts[continent][country]

    if variant != 'generic':
        for (variant_human, variant_code) in keyboard_layouts.variants[layout]:
            if variant_human == variant:
                variant = variant_code

    set_keyboard(layout, variant)
