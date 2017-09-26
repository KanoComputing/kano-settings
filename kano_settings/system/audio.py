#!/usr/bin/env python

# audio.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Contains the audio backend functions


from kano.utils.shell import run_cmd, run_bg
from kano.logging import logger

from kano_peripherals.wrappers.detection import is_pi_hat_plugged

from kano_settings.config_file import get_setting, set_setting
from kano_settings.boot_config import set_config_value, end_config_transaction

from kano_settings.paths import ASOUND_CONF_PATH


amixer_control = "name='PCM Playback Route'"

analogue_value = 1
hdmi_value = 2
hdmi_string = ": values={}".format(hdmi_value)

store_cmd = "service alsa-store restart"
#amixer_set_cmd = "amixer -c 0 cset {control} {{value}}".format(
#    control=amixer_control)
amixer_get_cmd = "amixer -c 0 cget {control}".format(control=amixer_control)

analogue_cmd = "amixer -c 0 cset numid=3 1"
hdmi_cmd = "amixer -c 0 cset numid=3 2"

# This value comes from the asound.conf in kano-desktop, but because the file is
# not in this repo, the value is duplicated..
DEFAULT_ALSA_CONFIG_MAX_DB = 4.0

DEFAULT_CKC_V1_MAX_DB = -11.9


def is_hdmi_audio_supported():
    '''
    Returns True if the display is HDMI and has audio support
    '''
    if is_hdmi_audio_supported.hdmi_supported is not None:
        return is_hdmi_audio_supported.hdmi_supported
    try:
        from kano_settings.system.display import get_edid
        is_hdmi_audio_supported.hdmi_supported = get_edid()['hdmi_audio']
    except Exception:
        is_hdmi_audio_supported.hdmi_supported = False

    return is_hdmi_audio_supported.hdmi_supported

# local static variable to avoid calling tvservice more than once
is_hdmi_audio_supported.hdmi_supported = None


def is_analogue_audio_supported():
    """
    Check the system to see if audio through the jack is available.

    Unfortunately, the hardware for the PiHat on CK2 Lite requires disabling audio
    through the jack. This is the only instance we need to prevent jack audio.

    Returns:
        True if audio can be set to play through jack, False otherwise
    """
    return (not is_pi_hat_plugged(retry_count=0))


def set_to_HDMI(HDMI, force=False):
    '''
    Set audio output to HDMI if supported by the display,
    otherwise set it to Analogue output.

    Returns 'HDMI' or 'Analogue', whichever was applied.
    '''

    if not is_hdmi_audio_supported() and not force:
        HDMI = False

    # 1 analog
    # 2 hdmi

    # These are the changes we'll apply if they have changed from what they were
    if HDMI:
        amixer_cmd = hdmi_cmd
        set_config_value('hdmi_ignore_edid_audio', None)
        set_config_value('hdmi_drive', 2)
        config = _("HDMI")
    else:
        amixer_cmd = analogue_cmd
        set_config_value('hdmi_ignore_edid_audio', 1)
        set_config_value('hdmi_drive', None)
        config = _("Analogue")

    end_config_transaction()

    # Set audio path in amixer
    o, e, rc = run_cmd(amixer_cmd)
    if rc:
        logger.warn("error from amixer: {} {} {}".format(o, e, rc))

    # trigger alsa-store to store the path in /var/lib/alsa/asound.state
    o, e, rc = run_cmd(store_cmd)
    if rc:
        logger.warn("error from alsa-store: {} {} {}".format(o, e, rc))

    set_setting('Audio', config)
    return config


# Returns is_HDMI = True or False
def is_HDMI():
    # Find the audio setting
    amixer_string, e, rc = run_cmd(amixer_get_cmd)
    if rc:
        logger.warn("error from amixer: {} {} {}".format(amixer_string, e, rc))

    if amixer_string.find(hdmi_string) != -1:
        # Make sure config file is up to date
        if get_setting('Audio') != _("HDMI"):
            set_setting('Audio', _("HDMI"))
        return True

    # Default to Analogue
    else:
        # Make sure config file is up to date
        if get_setting('Audio') != _("Analogue"):
            set_setting('Audio', _("Analogue"))
        return False


def set_alsa_config_max_dB(decibel):
    """
    Set the maximum volume (gain) ALSA can output.

    The function changes the system config file for ALSA in order
    to do the change. Requires sudo.

    NB: Ideally, there would be a lib to change different options
        so there's no generalisation done here.

    Args:
        decibel - float number for the value of max_dB to set

    Returns:
        bool whether or not any changes were made to the config file
    """
    changes = False

    with open(ASOUND_CONF_PATH, 'r') as asound_conf:
        asound_conf_lines = asound_conf.readlines()

    for index, line in enumerate(asound_conf_lines):

        # Check if the setting is already the one we need.
        if line.strip().startswith('max_dB'):
            if line.strip() != 'max_dB {0:0.1f}'.format(decibel):

                asound_conf_lines[index] = '{0} {1:0.1f}\n'.format(
                    # Grab the line with the required indent, e.g. '    max_dB'
                    line.rstrip().rsplit(' ', 1)[0],
                    decibel
                )
                changes = True
                break

    if not changes:
        return False

    with open(ASOUND_CONF_PATH, 'w') as asound_conf:
        asound_conf.write(''.join(asound_conf_lines))

    return True


def get_alsa_config_max_dB():
    """
    Get the maximum volume (gain) ALSA can currently output.

    Returns:
        float - value for the max_dB option in decibels
    """
    max_dB = None

    with open(ASOUND_CONF_PATH, 'r') as asound_conf:
        asound_conf_lines = asound_conf.readlines()

    for line in asound_conf_lines:
        if 'max_dB' in line:
            max_dB = line.split()[1]
            break

    return float(max_dB) if max_dB is not None else max_dB


def restart_alsa(background=True):
    """
    Restart ALSA service.

    This is helpful when changes have been made to the ALSA config and need to
    be applied without a system reboot.

    NOTE: Applications already running would most likely need to
          restart for the changes to be noticeable.

    Args:
        background - bool whether the operation should be done in another process

    Returns:
        bool whether or not the operation was successful (for background, always True)
    """
    cmd = '/etc/init.d/alsa-utils restart'

    if background:
        run_bg(cmd)
        return True
    else:
        dummy, dummy, rc = run_cmd(cmd)
        return rc == 0
