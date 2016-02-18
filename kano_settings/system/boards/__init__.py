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


__author__ = 'Kano Computing Ltd.'
__email__ = 'dev@kano.me'


def get_board_props(board_name):
    # FIXME: Sort out support for boards which share names, i.e. with /+ suffix
    board_name = re.sub(r'[-/ ]', '_', board_name).lower()
    try:
        board = importlib.import_module(
            '{}.{}'.format(__name__, board_name)
        )
    except ImportError:
        logger.error('Board not found')
        return None

    if not hasattr(board, 'CLOCKING'):
        logger.error('No clocking data in board config')
        return None

    '''
    if not all([key in board.CLOCKING for key in CLOCK_KEYS]):
        logger.error('Malformed clocking data in board config')
        return None
    '''

    return board

def get_supported_boards_props():
    return {
        board_name: get_board_props(board_name)
        for dummy_importer, board_name, dummy
        in pkgutil.iter_modules([__path__])
    }
