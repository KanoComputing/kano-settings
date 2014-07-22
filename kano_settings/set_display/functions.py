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
from kano_settings.boot_config import set_config_value, get_config_value
from kano.utils import run_cmd
from kano.logging import logger

tvservice_path = '/usr/bin/tvservice'


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


def set_hdmi_mode(group=None, mode=None):
    if not group or not mode:
        set_config_value("hdmi_group", None)
        set_config_value("hdmi_mode", None)
        return

    group = group.lower()
    mode = int(mode)

    if group == "cea":
        set_config_value("hdmi_group", 1)
    else:
        set_config_value("hdmi_group", 2)

    set_config_value("hdmi_mode", mode)


def get_status():
    status = dict()

    status_str, _, _ = run_cmd(tvservice_path + ' -s')
    if 'DMT' in status_str:
        status['group'] = 'DMT'
    elif 'CEA' in status_str:
        status['group'] = 'CEA'
    else:
        logger.error('status parsing error')
        sys.exit()

    status['mode'] = int(status_str.split('(')[1].split(')')[0].strip())
    status['full_range'] = 'RGB full' in status_str

    status['overscan'] = not (
        get_config_value('disable_overscan') == 1 and
        get_config_value('overscan_top') == 0 and
        get_config_value('overscan_bottom') == 0 and
        get_config_value('overscan_left') == 0 and
        get_config_value('overscan_right') == 0
    )

    res, hz = status_str.split(',')[1].split('@')
    status['resolution'] = res.strip()
    status['hz'] = float(hz.strip()[:-2])

    return status


def get_model():
    cmd = '/opt/vc/bin/tvservice -n'
    display_name, _, _ = run_cmd(cmd)
    display_name = display_name[16:].rstrip()
    return display_name


def get_overscan_status():
    out, _, _ = run_cmd('overscan')
    try:
        top, bottom, left, right = out.strip().split()
    except Exception:
        top = left = right = bottom = 0

    top = int(top)
    bottom = int(bottom)
    left = int(left)
    right = int(right)

    overscan_values = {
        'top': top,
        'bottom': bottom,
        'left': left,
        'right': right,
    }

    return overscan_values


def set_overscan_status(overscan_values):
    top = overscan_values['top']
    bottom = overscan_values['bottom']
    left = overscan_values['left']
    right = overscan_values['right']

    cmd = 'overscan {} {} {} {}'.format(top, bottom, left, right)
    run_cmd(cmd)


def write_overscan_values(overscan_values):
    set_config_value('overscan_top', overscan_values['top'])
    set_config_value('overscan_bottom', overscan_values['bottom'])
    set_config_value('overscan_left', overscan_values['left'])
    set_config_value('overscan_right', overscan_values['right'])


def read_hdmi_mode():
    group_int = get_config_value('hdmi_group')
    if group_int == 1:
        group_name = 'CEA'
    else:
        group_name = 'DMT'

    mode = int(get_config_value('hdmi_mode'))
    return group_name, mode


def find_matching_mode(modes, group, mode):
    string = '{}:{}'.format(group.lower(), mode)
    for i, m in enumerate(modes):
        if m.startswith(string):
            return i

    # 0 for auto
    return 0
