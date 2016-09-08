#!/usr/bin/env python

# keyboard_config.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This script is an interactive selection of the keyboard,
# based on country name and local keyboard variant.
#

from kano.logging import logger
from kano.utils.shell import run_cmd
from kano.utils.file_operations import sed

import kano_settings.system.keyboard_layouts as keyboard_layouts
import kano_settings.system.locale as locale
from kano_settings.config_file import get_setting, set_setting

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
    except Exception:
        # It means this country code does not have keyboard variants
        return None


# Find macintosh index within the variants combobox 
def find_macintosh_index(country_name, layout):
    country_code = find_country_code(country_name, layout)
    variants = find_keyboard_variants(country_code)

    if variants:
        for i in range(len(variants)):
            if variants[i] == ("Macintosh", "mac"):
                # This is due to the adding of generic at the start of the array
                return i + 1
    else:
        return None


def is_changed(country_code, variant):
    continent = get_setting('Keyboard-continent-human')
    country = get_setting('Keyboard-country-human')

    stored_variant = get_setting('Keyboard-variant-human').lower()
    stored_layout = keyboard_layouts.layouts[continent][country].lower()

    if variant == 'generic':
        variant = ''

    return (country_code != stored_layout or variant != stored_variant)


def update_settings_keyboard_conf(continent_index, country_index, variant_index,
                                  continent, country, variant):
    logger.info('set_keyboard.update_config {} {} {} {} {} {}'.format(
        continent_index,
        country_index,
        variant_index,
        continent,
        country,
        variant
    ))

    # Add new configurations to config file.
    set_setting("Keyboard-continent-index", continent_index)
    set_setting("Keyboard-country-index", country_index)
    set_setting("Keyboard-variant-index", variant_index)
    set_setting("Keyboard-continent-human", continent)
    set_setting("Keyboard-country-human", country)
    set_setting("Keyboard-variant-human", variant)


def set_keyboard_config(country_code, variant):
    sed('^XKBLAYOUT=.*$',
        'XKBLAYOUT="{}"'.format(country_code),
        keyboard_conffile,
        True)
    sed('^XKBVARIANT=.*$',
        'XKBVARIANT="{}"'.format(variant),
        keyboard_conffile,
        True)


def save_keyboard_settings(locale_code, variant):
    continent, country = locale.locale_to_layout_keys(locale_code)
    continent_idx, country_idx = locale.layout_keys_to_indexes(
        continent, country
    )

    country_code = keyboard_layouts.layouts.get(continent, {}).get(country, '')
    variants = find_keyboard_variants(country_code) or []

    found = False
    idx = 0

    for idx, (variant_desc, variant_id) in enumerate(variants):
        if variant_desc == variant or variant_id == variant:
            found = True
            break

    variant_idx = idx if found else 0

    update_settings_keyboard_conf(
        continent_idx,
        country_idx,
        variant_idx,
        continent,
        country,
        variant
    )


def set_keyboard(locale_code, variant, save=False):
    if variant == 'generic':
        variant = ''

    # Notify and apply changes to the XServer
    run_cmd("setxkbmap {} {}".format(locale_code, variant))
    set_keyboard_config(locale.split_locale(locale_code)[0], variant)
    run_cmd("ACTIVE_CONSOLE=guess /bin/setupcon -k </dev/tty1")

    if save:
        save_keyboard_settings(locale_code, variant)


def set_saved_keyboard():
    continent = get_setting('Keyboard-continent-human')
    country = get_setting('Keyboard-country-human')
    variant = get_setting('Keyboard-variant-human')

    try:
        layout = keyboard_layouts.layouts[continent][country]
    except KeyError:
        return

    if variant != 'generic':
        for (variant_human, variant_code) in keyboard_layouts.variants[layout]:
            if variant_human == variant:
                variant = variant_code

    set_keyboard(layout, variant)
