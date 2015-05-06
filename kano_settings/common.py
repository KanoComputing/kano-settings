#!/usr/bin/env python

# common.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Keeps common variables in a central place

import os
import sys

rel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../media/kano-settings'))
abs_path = '/usr/share/kano-settings/media'

if os.path.exists(rel_path):
    media = rel_path
elif os.path.exists(abs_path):
    media = abs_path
else:
    sys.exit('Media folder missing!')

css_dir = os.path.join(media, "CSS")

has_internet = False
proxy_enabled = False
need_reboot = False

# directory where the configuration files are kept
settings_dir = '/usr/share/kano-settings/config'
