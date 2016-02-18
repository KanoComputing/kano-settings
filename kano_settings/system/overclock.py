#!/usr/bin/env python

# overclock.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Backend overclock functions
#

from kano.logging import logger
from kano_settings.boot_config import set_config_value, get_config_value
from kano_settings.config_file import set_setting
from kano_settings.system.boards import get_board_props, \
    get_supported_boards_props


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
        logger.error('Could not get overclocking settings for board')
        return

    values = board.CLOCKING['values']

    for row in values:
        if values_equal(values[row], curr):
            return row
    return None

def get_board_with_overclock_value():
    curr = {}
    for key in CLOCK_KEYS:
        curr[key] = get_config_value(key)

    def does_board_match(board):
        values = board.CLOCKING['values']

        for row in values:
            if values_equal(values[row], curr):
                return True

        return False


    boards = get_supported_boards_props()

    if not boards:
        logger.error('Could not get overclocking settings for any board')
        return

    for board_name, board_props in boards.iteritems():
        if does_board_match(board_props):
            return board_name

    return False


def backup_overclock_values(backup_config):
    backup_config.ensure_exists()
    for key in CLOCK_KEYS:
        backup_config.set_value(key, get_config_value(key))


def restore_overclock_values(backup_config):
    for key in CLOCK_KEYS:
        set_config_value(key, backup_config.get_value(key))


def change_overclock_value(config, board_name):
    board = get_board_props(board_name)

    if not board:
        logger.error('Could not get overclocking settings for board')
        return

    try:
        values = board.CLOCKING['values'][config]
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


def set_default_overclock_values(board_name):
    board = get_board_props(board_name)

    if not board:
        logger.error('Could not get overclocking settings for board')
        return

    change_overclock_value(board.CLOCKING['default'], board_name)


def is_dangerous_overclock_value(config, board_name):
    board = get_board_props(board_name)

    if not board:
        logger.error('Could not get overclocking settings for board')
        return

    return config in board.CLOCKING['warning']
