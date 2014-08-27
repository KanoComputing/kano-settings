#!/usr/bin/env python

# overclock.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Backend overclock functions
#

from kano_settings.boot_config import set_config_value
from kano.logging import logger
from kano_settings.config_file import set_setting


def change_overclock_value(config):

    #  Mode      arm_freq    core_freq    sdram_freq   over_voltage
    # "None"   "700MHz ARM, 250MHz core, 400MHz SDRAM, 0 overvolt"
    # "Modest" "800MHz ARM, 300MHz core, 400MHz SDRAM, 0 overvolt"
    # "Medium" "900MHz ARM, 333MHz core, 450MHz SDRAM, 2 overvolt"
    # "High"   "950MHz ARM, 450MHz core, 450MHz SDRAM, 6 overvolt"

    # None configuration
    if config is "None":
        arm_freq = 700
        core_freq = 250
        sdram_freq = 400
        over_voltage = 0
    # Modest configuration
    elif config is "Modest":
        arm_freq = 800
        core_freq = 300
        sdram_freq = 400
        over_voltage = 0
    # Medium configuration
    elif config is "Medium":
        arm_freq = 900
        core_freq = 333
        sdram_freq = 450
        over_voltage = 2
    # High configuration
    elif config is "High":
        arm_freq = 950
        core_freq = 450
        sdram_freq = 450
        over_voltage = 6
    else:
        logger.error('kano-settings: set_overclock: SetOverclock: set_overclock(): ' +
                     'was called with an invalid self.selected_button={}'.format(config))
        return

    logger.info('set_overclock / apply_changes: config:{} arm_freq:{} core_freq:{} sdram_freq:{} over_voltage:{}'.format(
                config, arm_freq, core_freq, sdram_freq, over_voltage))

    # Apply changes
    set_config_value("arm_freq", arm_freq)
    set_config_value("core_freq", core_freq)
    set_config_value("sdram_freq", sdram_freq)
    set_config_value("over_voltage", over_voltage)

     # Update config
    set_setting("Overclocking", config)
