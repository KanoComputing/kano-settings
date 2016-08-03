#/usr/bin/python

# test.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Runs all the unit tests
#


import sys
import os
import unittest

sys.path.insert(1, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


SUITE = unittest.TestSuite()
TESTS = [
    'tests.i18n.test_locale',
    'tests.boot_config.boot_config_parser',
    'tests.boot_config.boot_config_line',
    'tests.boot_config.test_config'
]

for test in TESTS:
    SUITE.addTest(unittest.defaultTestLoader.loadTestsFromName(test))
unittest.TextTestRunner(verbosity=2).run(SUITE)
