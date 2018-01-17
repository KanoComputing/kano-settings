#
# kano-safeboot-mode
#
# Copyright (C) 2014-2015, 2017-2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Configure HDMI settings on boot, if Ctrl-Alt hotkey is pressed, then switch
# to safe mode. Also calls code to set clock config, to avoid need to an extra
# reboot.
#
# Passing "--led" will blink the board LED to notify the user to press the
# hotkey.
#


import os
import sys

from kano.utils.shell import run_cmd
from kano.utils.user import enforce_root
from kano.logging import logger
from kano_settings.boot_config import enforce_pi, is_safe_boot, \
    safe_mode_backup_config, end_config_transaction
from kano_settings.system.display import set_safeboot_mode


TOKEN_PATH = '/var/cache/kano-settings'
TOKEN_NAME = 'safeboot_token'
TOKEN_FILENAME = os.path.join(TOKEN_PATH, TOKEN_NAME)
SAFEBOOT_SOUND = "/usr/share/kano-settings/media/sounds/kano_safeboot.wav"


def safe_boot_requested(led=False):
    """ Test whether the CTRL+ALT keys were pressed. """

    if led:
        # Start a board LED blink in the background for a few seconds
        # so the user knows it's time to press Ctrl-Alt
        _, _, _ = run_cmd("/usr/bin/kano-led &")

    _, _, rv = run_cmd("kano-keys-pressed -r 5 -d 10")
    return rv == 10


def set_safeboot_token():
    try:
        # Make a token which indicates that we are in safe mode because a key
        # was pressed
        if not os.path.exists(TOKEN_PATH):
            os.makedirs(TOKEN_PATH)

        with open(TOKEN_FILENAME, 'a'):
            os.utime(TOKEN_FILENAME, None)
    except Exception:
        # No errors in this function should prevent the main point of this
        # script
        pass


def is_token_set():
    return os.path.exists(TOKEN_FILENAME)


def remove_token():
    os.unlink(TOKEN_FILENAME)


def main():
    logger.force_log_level('info')

    # main program execution starts here
    enforce_pi()
    enforce_root('Need to be root!')

    # Do not blink the LED by default
    blink_led = len(sys.argv) > 1 and sys.argv[1] == '--led'

    # Reconfigure and reboot if the user requested safe mode
    # Or if the cable appears not to have been plugged in.
    if safe_boot_requested(led=blink_led) and not is_safe_boot():
        logger.warn("Safe boot requested")

        # Backup the config file
        safe_mode_backup_config()

        set_safeboot_mode()

        end_config_transaction()

        # Set the token
        set_safeboot_token()
        try:
            from kano.utils.audio import play_sound
            play_sound(SAFEBOOT_SOUND)
        except Exception:
            pass  # ignore failures in sound

        # Trigger a reboot
        logger.sync()
        run_cmd('kano-checked-reboot safeboot systemctl reboot --force')
        return 0

    if is_token_set():
        remove_token()
        run_cmd("kano-capture-logs &")
