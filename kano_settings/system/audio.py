#!/usr/bin/env python

# audio.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Contains the audio backend functions


from kano_settings.config_file import get_setting, set_setting, file_replace
from kano_settings.boot_config import set_config_value


rc_local_path = "/etc/rc.audio"
analogue_string = "amixer -c 0 cset numid=3 1"
hdmi_string = "amixer -c 0 cset numid=3 2"


# set_to_HDMI = True or False
def set_to_HDMI(HDMI):
    # amixer -c 0 cset numid=3 N
    # 1 analog
    # 2 hdmi

    # Uncomment/comment out the line in /etc/rc.audio
    amixer_from = "amixer -c 0 cset numid=3 [0-9]"

    # These are the changes we'll apply if they have changed from what they were
    if HDMI:
        amixer_to = "amixer -c 0 cset numid=3 2"
        set_config_value("hdmi_ignore_edid_audio", None)
        set_config_value("hdmi_drive", 2)
        config = "HDMI"
    else:
        amixer_to = "amixer -c 0 cset numid=3 1"
        set_config_value("hdmi_ignore_edid_audio", 1)
        set_config_value("hdmi_drive", None)
        config = "Analogue"

    file_replace(rc_local_path, amixer_from, amixer_to)
    set_setting('Audio', config)


# Returns is_HDMI = True or False
def is_HDMI():
    f = open(rc_local_path, 'r')
    file_string = str(f.read())

    if file_string.find(analogue_string) != -1:
        # Make sure config file is up to date
        if get_setting('Audio') != 'Analogue':
            set_setting('Audio', "Analogue")
        return False

    elif file_string.find(hdmi_string) != -1:
        # Make sure config file is up to date
        if get_setting('Audio') != 'HDMI':
            set_setting('Audio', "HDMI")
        return True
