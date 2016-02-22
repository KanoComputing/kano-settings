#
# __init__.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Module for board specific settings
#

import importlib
import re
import pkgutil

from kano.logging import logger
from kano.utils.hardware import RPI_1_CPU_PROFILE, get_board_property, \
    get_rpi_model


__author__ = 'Kano Computing Ltd.'
__email__ = 'dev@kano.me'


def get_board_props(board_name=None):
    if not board_name:
        board_name = get_rpi_model()

    cpu_profile = get_board_property(board_name, 'cpu_profile')

    if not cpu_profile:
        cpu_profile = RPI_1_CPU_PROFILE

    board_module = re.sub(r'[-/ ]', '_', cpu_profile).lower()

    try:
        board = importlib.import_module(
            '{}.{}'.format(__name__, board_module)
        )
    except ImportError:
        logger.error('Board not found')
        return None

    required_props = ['CLOCKING', 'DEFAULT_CONFIG']

    for prop in required_props:
        if not hasattr(board, prop):
            logger.error('No {} data in board config'
                         .format(prop.replace('_', ' ').lower()))
            return None

    # TODO: Validate board info

    return board
