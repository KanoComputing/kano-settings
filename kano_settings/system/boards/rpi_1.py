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
    'Overclocking': _("High")
}

CLOCKING = {
    'modes': [_("None"), _("Modest"), _("Medium"), _("High"), _("Turbo")],
    'default': _("High"),
    'warning': [_("Turbo")],
    'values': {
        _("None"): {
            'arm_freq': 700,
            'core_freq': 250,
            'sdram_freq': 400,
            'over_voltage': 0
        },
        _("Modest"): {
            'arm_freq':  800,
            'core_freq':  250,
            'sdram_freq':  400,
            'over_voltage':  0
        },
        _("Medium"): {
            'arm_freq': 900,
            'core_freq': 250,
            'sdram_freq': 450,
            'over_voltage': 2
        },
        _("High"): {
            'arm_freq': 950,
            'core_freq': 250,
            'sdram_freq': 450,
            'over_voltage': 6,
        },
        _("Turbo"): {
            'arm_freq': 1000,
            'core_freq': 500,
            'sdram_freq': 600,
            'over_voltage': 6,
        }
    }
}
