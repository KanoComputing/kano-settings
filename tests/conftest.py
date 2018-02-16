# conftest.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The pytest conftest file.
#
# It imports all the fixtures used in this test suite
# and it contains various utility functions.


import os
import shutil
import unittest
import importlib
from contextlib import contextmanager

import kano.utils.hardware as hw

from tests.fixtures.alsa_config import *
from tests.fixtures.edid_data import *


REASON_NOT_IMPLEMENTED = '' \
    'Test case is not yet implemented, but a note of the requirement was made.'

REASON_REQUIRES_KANO_OS = '' \
    'Function makes system wide changes in Kano OS and was designed to' \
    ' be executed in that environment, e.g. systemd, config files, etc.'


require_rpi = unittest.skipIf(
    hw.get_rpi_model().lower().startswith('error') or
    hw.get_rpi_model().lower().startswith('unknown'),
    'Test must be run on a RPi'
)


@contextmanager
def mock_file(file_path, mock_data=None):
    original_file = file_path + '.orig'

    if os.path.exists(file_path):
        shutil.move(file_path, original_file)

    if mock_data:
        with open(file_path, 'w') as mock_file_handle:
            mock_file_handle.write(mock_data)

    yield

    if os.path.exists(file_path):
        os.remove(file_path)

    if os.path.exists(original_file):
        shutil.move(original_file, file_path)


def is_kano_os():
    """
    A tongue-in-cheek detection method of Kano OS.

    Returns:
        bool - whether or not the function was executed in Kano OS.
    """
    return (
        os.path.exists('/etc/kanux_version') and
        os.path.exists('/boot/config.txt')
    )


def is_pypkg_installed(modules):
    """
    Check if Python modules are installed and can be used.

    Args:
        modules - list of python module names to check if they can be imported

    Returns:
        bool - whether or not all given modules are installed and usable
    """
    all_installed = True

    for module in modules:
        try:
            print module
            importlib.import_module(module)
        except ImportError:
            print 'Missing dependency: [{}] python module.'.format(module)
            all_installed = False

    return all_installed
