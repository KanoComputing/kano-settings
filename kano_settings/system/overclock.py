#!/usr/bin/env python

# overclock.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Backend overclock functions
#

from kano_settings.boot_config import set_config_value
from kano.logging import logger
from kano_settings.config_file import set_setting

#  Mode      arm_freq       core_freq      sdram_freq   over_voltage
#  None;     700 MHz ARM,  250 MHz core, 400 MHz SDRAM, 0 overvolt
#  Modest;   800 MHz ARM,  250 MHz core, 400 MHz SDRAM, 0 overvolt
#  Medium;   900 MHz ARM,  250 MHz core, 450 MHz SDRAM, 2 overvolt
#  High;     950 MHz ARM,  250 MHz core, 450 MHz SDRAM, 6 overvolt
#  Turbo;    1000 MHz ARM, 500 MHz core, 600 MHz SDRAM, 6 overvolt

rpi1_modes = ["None", "Modest", "Medium", "High", "Turbo"]
rpi1_overclock_values = {
    "None": {
        "arm_freq": 700,
        "core_freq": 250,
        "sdram_freq": 400,
        "over_voltage": 0
    },
    "Modest": {
        "arm_freq":  800,
        "core_freq":  250,
        "sdram_freq":  400,
        "over_voltage":  0
    },
    "Medium": {
        "arm_freq": 900,
        "core_freq": 250,
        "sdram_freq": 450,
        "over_voltage": 2
    },
    "High": {
        "arm_freq": 950,
        "core_freq": 250,
        "sdram_freq": 450,
        "over_voltage": 6,
    },
    "Turbo": {
        "arm_freq": 1000,
        "core_freq": 500,
        "sdram_freq": 600,
        "over_voltage": 6,
    }
}

rpi2_modes = ["Standard","Overclocked"]
rpi2_overclock_values = {
    "Standard": {
        "arm_freq": 900,
        "core_freq": 250,
        "sdram_freq": 450,
        "over_voltage": 0
    },  # from https://github.com/asb/raspi-config/blob/
        #         4ee1fde44ee544a7eade9ecf94141eb40aabab60/raspi-config#L288
    "Overclocked": {
        "arm_freq": 1000,
        "core_freq": 500,
        "sdram_freq": 500,
        "over_voltage": 2
    }
}


def change_overclock_value(config,is_pi2):
    if is_pi2:
        overclock_values = rpi2_overclock_values
    else:
        overclock_values = rpi1_overclock_values


    if config not in overclock_values:
        logger.error('kano-settings: set_overclock: SetOverclock: set_overclock(): ' +
                     'was called with an invalid self.selected_button={}'.format(config))
        return

    values=overclock_values[config]


    logger.info('set_overclock / apply_changes: config:{} arm_freq:{arm_freq} core_freq:{core_freq} sdram_freq:{sdram_freq} over_voltage:{over_voltage}'.format(
                config, **values))

    # Apply changes
    for val in values:
        set_config_value(val, values[val])

    # Update config
    set_setting("Overclocking", config)
