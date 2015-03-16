#!/usr/bin/env python

# overclock.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Backend overclock functions
#

from kano_settings.boot_config import set_config_value, get_config_value
from kano.logging import logger
from kano_settings.config_file import set_setting


CLOCK_RPI1 = False
CLOCK_RPI2 = True

CLOCK_KEYS = ['arm_freq', 'core_freq','sdram_freq', 'over_voltage']

CLOCK_MODES = {

    CLOCK_RPI1: {
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
    },

    CLOCK_RPI2: {
        'modes': ['Standard', 'Overclocked'],
        'default': 'Standard',
        'warning': ['Overclocked'],
        'values': {
            'Standard': {
                'arm_freq': 900,
                'core_freq': 250,
                'sdram_freq': 450,
                'over_voltage': 0
            },
            # from https://github.com/asb/raspi-config/blob/4ee1fde44ee544a7eade9ecf94141eb40aabab60/raspi-config#L288
            'Overclocked': {
                'arm_freq': 1000,
                'core_freq': 500,
                'sdram_freq': 500,
                'over_voltage': 2
            }
        }
    }

}


def values_equal(v1, v2):
    return all([v1[x] == v2[x] for x in CLOCK_KEYS])


def match_overclock_value(is_pi2):
    """ which overlock gui setting matches our current set of values?"""
    curr = {}
    for key in CLOCK_KEYS:
        curr[key] = get_config_value(key)

    for row in CLOCK_MODES[is_pi2]['values']:
        if values_equal(CLOCK_MODES[is_pi2]['values'][row], curr):
            return row
    return None


def backup_overclock_values(backup_config):
    backup_config.ensure_exists()
    for key in CLOCK_KEYS:
        backup_config.set_value(key, get_config_value(key))


def restore_overclock_values(backup_config):
    for key in CLOCK_KEYS:
        set_config_value(key, backup_config.get_value(key))


def change_overclock_value(config, is_pi2):
    try:
        values = CLOCK_MODES[is_pi2]['values'][config]
    except KeyError:
        logger.error(
            'kano-settings: set_overclock: SetOverclock: set_overclock(): '
            'was called with an invalid overclock setting={}'
            .format(config)
        )
        return

    logger.info(
        'set_overclock / apply_changes: '
        'config:{} arm_freq:{arm_freq} '
        'core_freq:{core_freq} '
        'sdram_freq:{sdram_freq} '
        'over_voltage:{over_voltage}'
        .format(config, **values)
    )

    # Apply changes
    for val in values:
        set_config_value(val, values[val])

    # Update config
    set_setting("Overclocking", config)


def set_default_overclock_values(is_pi2):
    change_overclock_value(CLOCK_MODES[is_pi2]['standard'], is_pi2)


def is_dangerous_overclock_value(config, is_pi2):
    return (config in CLOCK_MODES[is_pi2]['warning'])
