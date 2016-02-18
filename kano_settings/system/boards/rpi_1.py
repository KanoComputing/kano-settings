#
# rpi_1.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Board specific settings for Raspberry Pi 1 (A/A+/B/B+)
# TODO: Should this support the Compute Module and RPi Zero also or should
#       another module be created which just links back to these settings?
#

DEFAULT_CONFIG = {
    'Keyboard-continent-index': 1,
    'Keyboard-country-index': 21,
    'Keyboard-variant-index': 0,
    'Keyboard-continent-human': 'america',
    'Keyboard-country-human': 'United States',
    'Keyboard-variant-human': 'Generic',
    'Audio': 'Analogue',
    'Wifi': '',
    'Wifi-connection-attempted': False,
    'Overclocking': 'High',
    'Mouse': 'Normal',
    'Font': 'Normal',
    'Wallpaper': 'kanux-background',
    'Parental-level': 0,
    'Locale': 'en_US',
    'LED-Speaker-anim': False,
    'Use_GLX': False
}

CLOCKING = {
    'modes': ['None', 'Modest', 'Medium', 'High', 'Turbo'],
    'default': 'High',
    'warning': ['Turbo'],
    'values': {
        'None': {
            'arm_freq': 700,
            'core_freq': 250,
            'sdram_freq': 400,
            'over_voltage': 0
        },
        'Modest': {
            'arm_freq':  800,
            'core_freq':  250,
            'sdram_freq':  400,
            'over_voltage':  0
        },
        'Medium': {
            'arm_freq': 900,
            'core_freq': 250,
            'sdram_freq': 450,
            'over_voltage': 2
        },
        'High': {
            'arm_freq': 950,
            'core_freq': 250,
            'sdram_freq': 450,
            'over_voltage': 6,
        },
        'Turbo': {
            'arm_freq': 1000,
            'core_freq': 500,
            'sdram_freq': 600,
            'over_voltage': 6,
        }
    }
}
