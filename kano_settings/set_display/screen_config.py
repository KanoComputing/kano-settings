#!/usr/bin/env python

# screen-config.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Change screen resolution and other settings
#

import os
import sys
import re
import subprocess
from kano_settings.boot_config import set_config_option


# Group must be either 'DMT' or 'CEA'
def get_supported_modes(group):
    modes = {}

    if not os.path.exists('/opt/vc/bin/tvservice'):
        return modes

    cea_modes = subprocess.check_output(["/opt/vc/bin/tvservice", "-m", group.upper()])
    cea_modes = cea_modes.decode()
    cea_modes = cea_modes.split("\n")[1:]
    mode_line_re = r'mode (\d+): (\d+x\d+) @ (\d+Hz) (\d+:\d+)'
    for line in cea_modes:
        mode_line_match = re.search(mode_line_re, line)
        if mode_line_match:
            number = mode_line_match.group(1)
            res = mode_line_match.group(2)
            freq = mode_line_match.group(3)
            aspect = mode_line_match.group(4)
            modes[int(number)] = [res, freq, aspect]

    return modes


def list_supported_modes():
    cea_modes = get_supported_modes("CEA")
    dmt_modes = get_supported_modes("DMT")
    modes = []

    for key in sorted(cea_modes):
        values = cea_modes[key]
        string = "cea:%d  %s  %s  %s" % (key, values[0], values[1], values[2])
        modes.append(string)

    for key in sorted(dmt_modes):
        values = dmt_modes[key]
        string = "dmt:%d  %s  %s  %s" % (key, values[0], values[1], values[2])
        modes.append(string)

    return modes


def set_hdmi_mode(mode):
    if mode == "auto":
        set_config_option("hdmi_group", None)
        set_config_option("hdmi_mode", None)
        return 0

    group, number = mode.split(":")
    group = group.lower()
    number = int(number)

    if group == "cea":
        set_config_option("hdmi_group", 1)
    elif group == "dmt":
        set_config_option("hdmi_group", 2)
    else:
        sys.stderr.write("ERROR: Unknown group '%s'.\n" % group)
        return 1

    set_config_option("hdmi_mode", number)
    return 0
