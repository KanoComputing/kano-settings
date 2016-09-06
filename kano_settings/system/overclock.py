#!/usr/bin/env python

# overclock.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Backend overclock functions
#

from kano.logging import logger
from kano.utils.hardware import BOARD_PROPERTIES, get_board_property

from kano_settings.boot_config import set_config_value, get_config_value
from kano_settings.config_file import set_setting
from kano_settings.system.boards import get_board_props


CLOCK_KEYS = [
    'arm_freq',
    'core_freq',
    'sdram_freq',
    'over_voltage'
]


def values_equal(v1, v2):
    return all([v1[x] == v2[x] for x in CLOCK_KEYS])


def match_overclock_value(board_name):
    """ which overlock gui setting matches our current set of values?"""
    curr = {}
    for key in CLOCK_KEYS:
        curr[key] = get_config_value(key)

    board = get_board_props(board_name)

    if not board:
        logger.error("Could not get overclocking settings for board")
        return

    values = board.CLOCKING['values']

    for row in values:
        if values_equal(values[row], curr):
            return row
    return None

def get_matching_board_profile():
    curr = {}
    for key in CLOCK_KEYS:
        curr[key] = get_config_value(key)

    def does_board_match(board):
        values = board.CLOCKING['values']

        for oc_setting in values.itervalues():
            if values_equal(oc_setting, curr):
                return True

        return False

    for board_key in BOARD_PROPERTIES.iterkeys():
        board_props = get_board_props(board_key)

        if does_board_match(board_props):
            logger.debug("Matched the board {} with the current settings"
                         .format(board_key))
            return get_board_property(board_key, 'cpu_profile')

    return False


def backup_overclock_values(backup_config):
    backup_config.ensure_exists()
    for key in CLOCK_KEYS:
        backup_config.set_value(key, get_config_value(key))


def restore_overclock_values(backup_config):
    for key in CLOCK_KEYS:
        set_config_value(key, backup_config.get_value(key))


def change_overclock_value(config, board_name=None):
    board = get_board_props(board_name=board_name)

    if not board:
        logger.error("Could not get overclocking settings for board")
        return

    try:
        values = board.CLOCKING['values'][config]
    except KeyError:
        logger.error(
            "kano-settings: set_overclock: SetOverclock: set_overclock(): " \
            "was called with an invalid overclock setting={}"
            .format(config)
        )
        return

    logger.info(
        "set_overclock / apply_changes: " \
        "config:{} arm_freq:{arm_freq} " \
        "core_freq:{core_freq} " \
        "sdram_freq:{sdram_freq} " \
        "over_voltage:{over_voltage}"
        .format(config, **values)
    )

    # Apply changes
    for val in values:
        set_config_value(val, values[val])

    # Update config
    set_setting('Overclocking', config)


def set_default_overclock_values(board_name=None):
    board = get_board_props(board_name=board_name)

    if not board:
        logger.error("Could not get overclocking settings for board")
        return

    change_overclock_value(board.CLOCKING['default'], board_name)


def is_dangerous_overclock_value(config, board_name=None):
    board = get_board_props(board_name=board_name)

    if not board:
        logger.error("Could not get overclocking settings for board")
        return

    return config in board.CLOCKING['warning']
