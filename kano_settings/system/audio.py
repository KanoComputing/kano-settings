#!/usr/bin/env python

# audio.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Contains the audio backend functions


from kano_settings.config_file import get_setting, set_setting, file_replace
from kano_settings.boot_config import set_config_value
from kano.utils import run_cmd
from kano.logging import logger


analogue_cmd = "amixer -c 0 cset numid=3 1"
analogue_string = ": values=1"

hdmi_cmd = "amixer -c 0 cset numid=3 2"
hdmi_string = ": values=2"

store_cmd = "service alsa-utils restart"
amixer_get_cmd = "amixer -c 0 cget numid=3"

try:
    from kano_settings.system.display import get_edid
    hdmi_supported = get_edid()['hdmi_audio']
except Exception:
    hdmi_supported = False


# set_to_HDMI = True or False
def set_to_HDMI(HDMI):
    if not hdmi_supported:
        HDMI = False

    # 1 analog
    # 2 hdmi

    # These are the changes we'll apply if they have changed from what they were
    if HDMI:
        amixer_cmd = hdmi_cmd
        set_config_value("hdmi_ignore_edid_audio", None)
        set_config_value("hdmi_drive", 2)
        config = "HDMI"
    else:
        amixer_cmd = analogue_cmd
        set_config_value("hdmi_ignore_edid_audio", 1)
        set_config_value("hdmi_drive", None)
        config = "Analogue"

    # Set audio path in amixer
    o, e, rc = run_cmd(amixer_cmd)
    if rc:
        logger.warning("error from amixer: {} {} {}".format(o, e, rc))

    # trigger alsa-utils to store the path in /var/lib/alsa/asound.state
    o, e, rc = run_cmd(store_cmd)
    if rc:
        logger.warning("error from alsa-utils: {} {} {}".format(o, e, rc))

    set_setting('Audio', config)


# Returns is_HDMI = True or False
def is_HDMI():
    # Find the audio setting
    amixer_string, e, rc = run_cmd(amixer_get_cmd)
    if rc:
        logger.warning("error from amixer: {} {} {}".format(amixer_string, e, rc))

    if amixer_string.find(analogue_string) != -1:
        # Make sure config file is up to date
        if get_setting('Audio') != 'Analogue':
            set_setting('Audio', "Analogue")
        return False

    elif amixer_string.find(hdmi_string) != -1:
        # Make sure config file is up to date
        if get_setting('Audio') != 'HDMI':
            set_setting('Audio', "HDMI")
        return True
