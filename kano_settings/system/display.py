#!/usr/bin/env python

# display.py
#
# Copyright (C) 2014-2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Change screen resolution and other settings.


import os
import time
import json
import shutil
import subprocess

from kano.utils import run_cmd, delete_file
from kano.logging import logger

from kano_settings.boot_config import set_config_value, get_config_value, \
    end_config_transaction
from kano_settings.config_file import get_setting, set_setting
from kano_settings.system.boot_config.boot_config_filter import Filter

from kano_settings.paths import TMP_EDID_DAT_PATH


tvservice_path = '/usr/bin/tvservice'
fbset_path = '/bin/fbset'
xrefresh_path = '/usr/bin/xrefresh'

fpturbo_conf_path = '/usr/share/X11/xorg.conf.d/99-fbturbo.conf'
fpturbo_conf_backup_path = '/var/cache/kano-settings/99-fbturbo.conf'

OPTIMAL_RESOLUTIONS = {
    '4:3': [
        {'width': 1280, 'height': 960},
        {'width': 1024, 'height': 768},
    ],
    '16:9': [
        {'width': 1366, 'height': 768},
        {'width': 1360, 'height': 768},
        {'width': 1280, 'height': 720},
    ],
    '16:10': [
        {'width': 1280, 'height': 800},
        {'width': 1440, 'height': 900},
    ],
}

SCREEN_KIT_NAMES = [
    'ADA-HDMI',
    'MST-HDMI1',
    'MST-HDMI',
]

# NOTE: There is a risk here that indexing EDIDs by model alone will eventually produce
#   conflicts. There may be different screens out there with the same model but
#   different characteristics. One solution could be to also use the md5 or the raw EDID.
EDID_OVERRIDES = {
    '32V3H-H6A': {
        'preferred_group': 'DMT',
        'preferred_mode': 16,
        'is_monitor': True
    },
    'AS4637_______': {
        'preferred_group': 'DMT',
        'preferred_mode': 16,
        'is_monitor': True
    },
    'BMD_HDMI': {
        'preferred_group': 'CEA',
        'preferred_mode': 33,
        'is_monitor': True
    },
    'MST-HDMI': {
        'preferred_group': 'DMT',
        'preferred_mode': 28,
        'is_monitor': True
    },
    'MST-HDMI1': {
        'preferred_group': 'DMT',
        'preferred_mode': 28,
        'is_monitor': True
    },
}

_g_monitor_edid_name = str()
_g_cea_modes = list()
_g_dmt_modes = list()


def get_edid_name(use_cached=True):
    global _g_monitor_edid_name

    if use_cached and _g_monitor_edid_name:
        return _g_monitor_edid_name

    cmd = '{tvservice} --name'.format(tvservice=tvservice_path)
    edid_line, dummy, rc = run_cmd(cmd)

    if rc != 0:
        logger.error('Error getting EDID name')
        return

    _g_monitor_edid_name = edid_line.strip('device_name=').strip()

    return _g_monitor_edid_name


def set_screen_value(key, value):
    monitor_edid_filter = Filter.get_edid_filter(get_edid_name())
    set_config_value(key, value, config_filter=monitor_edid_filter)


def get_screen_value(key, fallback=True):
    monitor_edid_filter = Filter.get_edid_filter(get_edid_name())
    return get_config_value(
        key, config_filter=monitor_edid_filter, fallback=fallback
    )


def switch_display_safe_mode():
    # NB this function appears to be unused

    # Finds the first available display resolution that is safe
    # and switches to this mode immediately
    safe_resolution = '1024x768'

    try:
        modes = list_supported_modes()
        for m in modes:
            resolution = m.split()[1]
            if resolution == safe_resolution:
                group = m.split()[0].split(':')[0]
                mode = m.split()[0].split(':')[1]
            logger.info(
                "Switching display to safe resolution {} (group={} mode={})"
                .format(resolution, group, mode))
            set_hdmi_mode_live(group, mode)
    except:
        logger.error("Error switching display to safe mode")


def launch_pipe():
    overscan_pipe = "/dev/mailbox"
    # Launch pipeline
    if not os.path.exists(overscan_pipe):
        run_cmd('mknod {} c 100 0'.format(overscan_pipe))


def get_supported_modes(group, min_width=1024, min_height=720):
    """
    Get the supported modes of the screen for an HDMI group.

    Args:
        group - str 'CEA' or 'DMT' rather than 1 or 2 respectively
        min_width - int minimum width resolution of modes to be returned
        min_height - int minimum height resolution of modes to be returned

    Returns:
        supported_modes - list of dicts each describing an HDMI mode for the given group.

    Structure of a mode is: {
        'group': str ('CEA' or 'DMT'),
        'mode': int,
        'width': int,
        'height': int,
        'rate': int (refresh rate, Hz),
        'aspect_ratio': str ('4:3', '16:9', etc),
        'scan': str ('p' progressive, 'i' interlaced),
        '3d_modes': list
    }
    """
    if not os.path.isfile(tvservice_path):
        return list()

    modes = subprocess.check_output([tvservice_path, '--modes', group.upper(), '--json'])
    try:
        modes = json.loads(modes)
    except:
        import traceback
        logger.error(
            'get_supported_modes: Unexpected error caught:\n{}'
            .format(traceback.format_exc())
        )
        return list()

    supported_modes = list()

    for mode in modes:
        # Add the group to the supported mode and rename the 'code' key to 'mode'
        # to be consistent with hdmi_group and hdmi_mode options.
        mode[u'group'] = group
        mode[u'mode'] = mode['code']
        mode.pop('code')

        if mode['width'] >= min_width and mode['height'] >= min_height:
            supported_modes.append(mode)

    return supported_modes


def list_supported_modes(min_width=1024, min_height=720, use_cached=True):
    """
    Get all the HDMI modes for all HDMI groups.

    Args:
        min_width - int minimum width resolution of modes to be returned
        min_height - int minimum height resolution of modes to be returned
        use_cached - bool get the modes already in the cache rather than re-interrogating

    Returns:
        supported_modes - list of dicts each describing an HDMI mode.
                          See get_supported_modes for more info.
    """
    global _g_cea_modes, _g_dmt_modes

    if use_cached and _g_cea_modes and _g_dmt_modes:
        return _g_cea_modes + _g_dmt_modes

    _g_cea_modes = get_supported_modes('CEA', min_width=min_width, min_height=min_height)
    _g_dmt_modes = get_supported_modes('DMT', min_width=min_width, min_height=min_height)

    return _g_cea_modes + _g_dmt_modes


def set_hdmi_mode_live(group=None, mode=None, drive='HDMI'):
    success = False

    if not group or not mode:
        return success

    # ask tvservice to switch to the given mode immediately
    status_str, _, rc = run_cmd(tvservice_path + ' -e "{} {} {}"'.format(group, mode, drive))
    if rc == 0 and os.path.exists(fbset_path) and os.path.exists(xrefresh_path):
        # Refresh the Xserver screen because most probably it has become
        # black as a result of the graphic mode switch. We wait a tiny bit
        # because on some occassions it happens to early and has no
        # effect (leaves the screen black).
        time.sleep(2)
        _, _, _ = run_cmd('{} -depth 8 ; {} -depth 16'.format(fbset_path, fbset_path))
        _, _, _ = run_cmd(xrefresh_path)
        success = True

    return success


def set_hdmi_mode(group=None, mode=None):
    """
    Set the HDMI group and mode to select a different display setting for
    resolution, frequency, etc. (see tvservice -m CEA && tvservice -m DMT).

    Args:
        group - str representing the group, e.g. 'cea'
        mode  - str for the hdmi mode number, e.g. '28'
    """
    if not group or not mode:
        set_screen_value('hdmi_group', None)
        set_screen_value('hdmi_mode', None)
        return

    group = group.lower()
    mode = int(mode)

    if group == 'cea':
        set_screen_value('hdmi_group', 1)
    else:
        set_screen_value('hdmi_group', 2)

    set_screen_value('hdmi_mode', mode)


def set_flip(display_rotate=None):
    """
    Flip screen 180.
    """
    if display_rotate:
        set_screen_value('display_rotate', 2)
    else:
        set_screen_value('display_rotate', 0)


def set_safeboot_mode():
    logger.warn("Safe boot requested")

    set_screen_value('hdmi_force_hotplug', 1)
    set_screen_value('config_hdmi_boost', 4)

    set_screen_value('hdmi_group', 2)
    set_screen_value('hdmi_mode', 16)

    set_screen_value('disable_overscan', 1)
    set_screen_value('overscan_left', 0)
    set_screen_value('overscan_right', 0)
    set_screen_value('overscan_top', 0)
    set_screen_value('overscan_bottom', 0)


def get_status():
    status = dict()

    cmd = '{tvservice} --status'.format(tvservice=tvservice_path)
    status_str, _, _ = run_cmd(cmd)
    if 'DMT' in status_str:
        status['group'] = 'DMT'
    elif 'CEA' in status_str:
        status['group'] = 'CEA'
    else:
        logger.error("status parsing error")
        return

    status['mode'] = int(status_str.split('(')[1].split(')')[0].strip())
    status['full_range'] = 'RGB full' in status_str

    status['overscan'] = not (
        get_screen_value('disable_overscan') == 1 and
        get_screen_value('overscan_top') == 0 and
        get_screen_value('overscan_bottom') == 0 and
        get_screen_value('overscan_left') == 0 and
        get_screen_value('overscan_right') == 0
    )

    res, hz = status_str.split(',')[1].split('@')
    status['resolution'] = res.strip()
    status['hz'] = float(hz.strip()[:-2])

    return status


def is_mode_fallback():
    """ Is this the fallback mode which we get when the cable is unplugged?
    """
    status = get_status()
    res = status['resolution']
    parts = res.split('x')
    if len(parts) != 2:
        logger.error("Error parsing resolution")
        return None
    try:
        (w, h) = map(int, parts)
    except:
        logger.error("Error parsing resolution")
        return None

    return w == 640 and h == 480


def is_screen_kit(use_cached=False):
    """
    Returns True if the screen is a Kano Screen Kit.
    """
    return get_edid_name(use_cached=use_cached) in SCREEN_KIT_NAMES


def get_model():
    """
    Get the display device model name

    NOTE: DO NOT USE THIS FUNCTION. USE get_edid_name INSTEAD.

    TODO: The implementation of this function should be that of get_edid_name
          and it's signature is much more intelligible than get_edid_name
    """
    cmd = '{tvservice} --name'.format(tvservice=tvservice_path)
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


def read_overscan_values():
    values = {
        'top': get_screen_value('overscan_top'),
        'bottom': get_screen_value('overscan_bottom'),
        'left': get_screen_value('overscan_left'),
        'right': get_screen_value('overscan_right')
    }
    return values


def write_overscan_values(overscan_values):
    set_screen_value('overscan_top', overscan_values['top'])
    set_screen_value('overscan_bottom', overscan_values['bottom'])
    set_screen_value('overscan_left', overscan_values['left'])
    set_screen_value('overscan_right', overscan_values['right'])
    end_config_transaction()


def is_overscan():
    # This completes a transaction to avoid kano-video holding the lock
    top = get_screen_value('overscan_top')
    bottom = get_screen_value('overscan_bottom')
    left = get_screen_value('overscan_left')
    right = get_screen_value('overscan_right')
    end_config_transaction()
    return (top or bottom or left or right)


def read_hdmi_mode():
    group_int = get_screen_value('hdmi_group')
    if group_int == 1:
        group_name = 'CEA'
    else:
        group_name = 'DMT'

    mode = int(get_screen_value('hdmi_mode'))
    return group_name, mode


def find_matching_mode(modes, group, mode):
    """ Get the index of the mode in the list from the HDMI group and HDMI mode. """

    for index, current_mode in enumerate(modes):
        if current_mode['mode'] == mode and current_mode['group'] == group:
            return index + 1

    # 0 for auto
    return 0


def read_edid():
    delete_file(TMP_EDID_DAT_PATH)

    cmd = '{tvservice} --dumpedid {edid_dat} && edidparser {edid_dat}'.format(
        tvservice=tvservice_path, edid_dat=TMP_EDID_DAT_PATH
    )
    edid_txt, _, rc = run_cmd(cmd)
    edid_txt = edid_txt.splitlines()

    if rc != 0:
        logger.error("error getting edid dat")
        return

    delete_file(TMP_EDID_DAT_PATH)
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
            # Some displays return garbage, on old firmwares it can also be random.
            model = l.split('monitor name is')[1].strip()
            edid['model'] = model.decode('ascii', 'ignore')

        # preferred
        elif 'found preferred' in l:
            if 'DMT' in l:
                edid['preferred_group'] = 'DMT'
            elif 'CEA' in l:
                edid['preferred_group'] = 'CEA'
            else:
                logger.error("parsing error")
                return

            res, mode = l.split(':')[2].split('@')
            edid['preferred_res'] = res.strip()
            parts = edid['preferred_res'].strip('p').split('x')
            edid['preferred_width'] = int(parts[0])
            edid['preferred_height'] = int(parts[1])
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


def get_gfx_driver():
    return get_setting('Use_GLX')


def set_gfx_driver(enabled):
    if enabled:
        set_config_value('dtoverlay', 'vc4-kms-v3d')
        try:
            try:
                os.makedirs(os.path.dirname(fpturbo_conf_backup_path))
            except OSError as e:
                if e.strerror == "File exists":
                    pass
                else:
                    raise
            shutil.copyfile(fpturbo_conf_path, fpturbo_conf_backup_path)
            os.remove(fpturbo_conf_path)
        except Exception as e:
            logger.error("Error restoring fpturbo_config", exception=e)

    else:
        set_config_value('dtoverlay', None)
        if not os.path.exists(fpturbo_conf_path):
            try:
                shutil.copyfile(fpturbo_conf_backup_path, fpturbo_conf_path)
            except Exception as e:
                logger.error("Error restoring fpturbo_config", exception=e)
    end_config_transaction()
    set_setting('Use_GLX', enabled)


def override_models(edid, model):
    """
    Correct the EDID data for a given model.

    EDID data is notorious for being inconsistent. Given a dataset of corrections,
    this function corrects data in the EDID for a given model.

    Args:
        edid - dict as returned by the function get_edid(); will be changed inplace
        model - str as return by the function get_edid_name()
    """
    if model not in EDID_OVERRIDES:
        return

    # Set the configured options for the model to the EDID of the given screen.
    for option, value in EDID_OVERRIDES[model].iteritems():
        edid[option] = value


def compare_and_set_full_range(edid, status, model, dry_run=False, force=False):
    """
    Returns True if full range is changed

    TODO: What is this for?
    """
    if status['full_range'] == edid['target_full_range'] and not force:
        logger.debug('Config full range change not needed.')
        return False

    hdmi_pixel_encoding = 2 if edid['target_full_range'] else 0

    logger.info(
        'Config full range change needed. Setting hdmi_pixel_encoding to {}'
        .format(hdmi_pixel_encoding)
    )
    if dry_run and not force:
        return True

    set_config_value(
        'hdmi_pixel_encoding',
        hdmi_pixel_encoding,
        config_filter=Filter.get_edid_filter(model)
    )
    return True


def compare_and_set_overscan(edid, status, model, dry_run=False, force=False):
    """
    Check the overscan status and set it as required from EDID.

    Args:
        edid - dict as returned by the function get_edid()
        status - dict as returned by the function get_status()
        model - str as return by the function get_edid_name()
        dry_run - bool run the function, but do not apply any changes
        force - bool reconfigure settings even when the status says it's not needed

    Returns:
        changes - bool whether or not changes were applied
    """
    if status['overscan'] == edid['target_overscan'] and not force:
        logger.debug('Config overscan change not needed.')
        return False

    if edid['target_overscan']:
        disable_overscan = 0
        overscan_value = -48  # TODO: where does this value come from?
    else:
        disable_overscan = 1
        overscan_value = 0

    logger.info(
        'Overscan change needed. Setting disable_overscan to {} and overscan to {}'
        .format(disable_overscan, overscan_value)
    )
    if dry_run and not force:
        return True

    set_config_value(
        'disable_overscan',
        disable_overscan,
        config_filter=Filter.get_edid_filter(model)
    )
    for overscan in ['overscan_left', 'overscan_right', 'overscan_top', 'overscan_bottom']:
        set_config_value(
            overscan,
            overscan_value,
            config_filter=Filter.get_edid_filter(model)
        )
    return True


def compare_and_set_optimal_resolution(edid, status, supported_modes, dry_run=False, force=False):
    """
    Check the current resolution and set an optimal one if needed.

    Args:
        edid - dict as returned by the function get_edid()
        status - dict as returned by the function get_status()
        supported_modes - list as returned by the function list_supported_modes()
        dry_run - bool run the function, but do not apply any changes
        force - bool reconfigure settings even when the status says it's not needed

    Returns:
        changes - bool whether or not changes were applied
    """
    optimal_mode = get_optimal_resolution_mode(edid, supported_modes)

    if status['group'] == optimal_mode['group'] and \
       status['mode'] == optimal_mode['mode'] and \
       not force:
        logger.info('Resolution mode/group change not needed.')
        return False

    logger.info(
        'Resolution change needed. Setting hdmi_group to {} and hdmi_mode to {}.'
        .format(optimal_mode['group'], optimal_mode['mode'])
    )
    if dry_run and not force:
        return True

    # Apply the hdmi_group and hdmi_mode config options for this screen (with filter).
    set_hdmi_mode(optimal_mode['group'], optimal_mode['mode'])
    return True


def get_optimal_resolution_mode(edid, supported_modes):
    """
    Get the optimal resolution for the current screen.

    Using the preferred HDMI group (CEA/DMT) and the list of supported modes, it tries
    to find a lower resolution that matches the characteristics of the screen.

    Args:
        edid - dict as returned by the function get_edid()
        supported_modes - list as returned by the function list_supported_modes()

    Returns:
        mode - dict as returned by function list_supported_modes()
    """
    preferred_mode = dict()

    # Set the preferred aspect ratio for the preferred resolution.
    # The easiest conversion would be to look through supported resolutions, but it's not
    # the most comprehensive way. Hopefully, the preferred mode should be also supported.
    for mode in supported_modes:
        if mode['mode'] == edid['preferred_mode'] and \
           mode['group'] == edid['preferred_group']:

            edid['preferred_aspect_ratio'] = mode['aspect_ratio']
            preferred_mode = mode
            logger.debug('Found preferred mode {}'.format(preferred_mode))
            break

    if 'preferred_aspect_ratio' not in edid:
        return

    # Go through the optimal resolutions list for the aspect ratio...
    for resolution in OPTIMAL_RESOLUTIONS[edid['preferred_aspect_ratio']]:

        # If preferred mode has the optimal resolution, return it.
        if resolution['width'] == preferred_mode['width'] and \
           resolution['height'] == preferred_mode['height']:
            return preferred_mode

        # If the optimal mode matches the screen preferences, return it.
        for mode in supported_modes:
            if resolution['width'] == mode['width'] and \
               resolution['height'] == mode['height'] and \
               mode['group'] == edid['preferred_group'] and \
               mode['rate'] == edid['preferred_hz']:

                logger.debug('Found optimal mode {}'.format(mode))
                return mode

    # An optimal resolution was not found, returning the screen preferred mode.
    return preferred_mode
