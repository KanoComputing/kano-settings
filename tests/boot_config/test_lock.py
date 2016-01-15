#
# test_config.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This script returns a value depending on whether the config.txt lock is available.
# 0 for no, 1 for yes

from kano_settings import boot_config
from kano.utils.file_operations import TimeoutException
import sys

boot_config.lock_timeout = 0.2
try:
    boot_config.has_config_comment("foo")
    print "Lock was unlocked"

    sys.exit(0)
except TimeoutException:
    print "Lock was locked"
    sys.exit(1)
