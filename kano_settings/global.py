#!/usr/bin/env python

# global.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Keeps global in a central place

import os
import sys

rel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../media'))
abs_path = '/usr/share/kano-settings/media'

if os.path.exists(rel_path):
    media = rel_path
elif os.path.exists(abs_path):
    media = abs_path
else:
    sys.exit('Media folder missing!')

has_internet = False
proxy_enabled = False
need_reboot = False
