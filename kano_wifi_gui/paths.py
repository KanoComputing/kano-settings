#!/usr/bin/env python

# paths.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Stores all the paths relevent for the WiFi GUI.
# This is useful for when you want to test your changes by editing the files in
# the home directory of Kano OS - the path will look for the local path first,
# otherwise it will use the one on the system

import os
import sys

rel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../media/kano-connect"))
abs_path = '/usr/share/kano-connect/media'

if os.path.exists(rel_path):
    media_dir = rel_path
elif os.path.exists(abs_path):
    media_dir = abs_path
else:
    sys.exit('Kano connect media folder missing!')

css_dir = os.path.join(media_dir, "CSS")
