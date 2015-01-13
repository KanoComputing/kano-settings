#!/usr/bin/env python

# display.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Change screen resolution and other settings
#

import os
import re
import subprocess
import time
from kano_settings.boot_config import set_config_value, get_config_value
from kano.utils import run_cmd, delete_file
from kano.logging import logger

tvservice_path = '/usr/bin/tvservice'
fbset_path = '/bin/fbset'
xrefresh_path = '/usr/bin/xrefresh'


def switch_display_safe_mode():
   # Finds the first available display resolution that is safe
   # and switches to this mode immediately
   safe_resolution='1024x768'

   try:
      modes=list_supported_modes()
      for m in modes:
         resolution=m.split()[1]
         if resolution == safe_resolution:
            group=m.split()[0].split(':')[0]
            mode=m.split()[0].split(':')[1]
            logger.info ('Switching display to safe resolution %s (group=%s mode=%s)' % (resolution, group, mode))
            set_hdmi_mode_live(group, mode)
   except:
      logger.error ('Error switching display to safe mode')


def launch_pipe():
    overscan_pipe = "/dev/mailbox"
    # Launch pipeline
    if not os.path.exists(overscan_pipe):
        run_cmd('mknod {} c 100 0'.format(overscan_pipe))


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

def set_hdmi_mode_live(group=None, mode=None, drive='HDMI'):
    success = False

    if not group or not mode:
        return success

    # ask tvservice to switch to the given mode immediately
    status_str, _, rc = run_cmd(tvservice_path + ' -e "%s %s %s"' % (group, mode, drive))
    if rc == 0 and os.path.exists(fbset_path) and os.path.exists(xrefresh_path):
        # refresh the Xserver screen because most probably it has become black as a result of the graphic mode switch.
        # we wait a tiny bit because on some occassions it happens to early and has no effect (leaves the screen black).
        time.sleep(2)
        _, _, _ = run_cmd('%s -depth 8 ; %s -depth 16' % (fbset_path, fbset_path))
        _, _, _ = run_cmd(xrefresh_path)
        success = True

    return success

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
        return

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


def is_overscan():
    top = get_config_value('overscan_top')
    bottom = get_config_value('overscan_bottom')
    left = get_config_value('overscan_left')
    right = get_config_value('overscan_right')
    return (top or bottom or left or right)


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
            return i + 1

    # 0 for auto
    return 0


def read_edid():
    edid_dat_path = '/tmp/edid.dat'

    delete_file(edid_dat_path)
    edid_txt, _, rc = run_cmd('tvservice -d {0} && edidparser {0}'.format(edid_dat_path))
    edid_txt = edid_txt.splitlines()
    if rc != 0:
        logger.error('error getting edid dat')
        return
    delete_file(edid_dat_path)
    return edid_txt


def parse_edid(edid_txt):
    edid = dict()

    # parsing edid
    found = False
    edid['dmt_found'] = False
    edid['hdmi_audio'] = True

    for l in edid_txt:

        # screen size
        if 'screen size' in l:
            edid['screen_size'] = int(l.split('screen size')[1].split('x')[0].strip())

        # model name
        elif 'monitor name is' in l:
            edid['model'] = l.split('monitor name is')[1].strip()

        # preferred
        elif 'found preferred' in l:
            if 'DMT' in l:
                edid['preferred_group'] = 'DMT'
            elif 'CEA' in l:
                edid['preferred_group'] = 'CEA'
            else:
                logger.error('parsing error')
                return

            res, mode = l.split(':')[2].split('@')
            edid['preferred_res'] = res.strip()
            hz, mode = mode.split(' Hz (')
            edid['preferred_hz'] = float(hz.strip())
            edid['preferred_mode'] = int(mode[:-1])

        # moving support
        elif 'moving support for' in l:
            found_group, found_mode = l.split(' to ')[1].split(' because sink')[0].split('mode')
            edid['found_group'] = found_group.strip()
            edid['found_mode'] = int(found_mode.strip())
            found = True

        # dmt_found
        elif 'preferred_res' in edid and edid['preferred_group'] == 'CEA' and \
             edid['preferred_res'] in l and 'remained' not in l:
            if 'DMT' not in l:
                continue

            tmp_hz = float(l.split('@')[1].split('Hz')[0].strip())
            if tmp_hz != edid['preferred_hz']:
                continue

            edid['dmt_found'] = True

        elif 'no audio support' in l:
            edid['hdmi_audio'] = False

    # setting target mode
    if found:
        edid['target_group'] = edid['found_group']
        edid['target_mode'] = edid['found_mode']
    else:
        edid['target_group'] = edid['preferred_group']
        edid['target_mode'] = edid['preferred_mode']

    # is_monitor
    if edid['target_group'] == 'DMT':
        edid['is_monitor'] = True
    elif 'TV' in edid['model']:
        edid['is_monitor'] = False
    else:
        edid['is_monitor'] = edid['dmt_found'] or edid.get('screen_size') < 60

    # always disable overscan
    edid['target_overscan'] = False

    return edid


def get_edid():
    edid_txt = read_edid()
    if not edid_txt:
        return

    return parse_edid(edid_txt)
