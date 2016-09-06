#
# rpi_2.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Board specific settings for Raspberry Pi 2
#

DEFAULT_CONFIG = {
    'Overclocking': _("Standard")
}

CLOCKING = {
    'modes': [_("Standard"), _("Overclocked")],
    'default': _("Standard"),
    'warning': [_("Overclocked")],
    'values': {
        _("Standard"): {
            'arm_freq': 900,
            'core_freq': 250,
            'sdram_freq': 450,
            'over_voltage': 0
        },
        # from https://github.com/asb/raspi-config/blob/4ee1fde44ee544a7eade9ecf94141eb40aabab60/raspi-config#L288
        _("Overclocked"): {
            'arm_freq': 1000,
            'core_freq': 500,
            'sdram_freq': 500,
            'over_voltage': 2
        }
    }
}
