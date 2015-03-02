# set-kano-hdmi
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Code to configure clock settings on boot.
#
# We support moving the SD card from one chip to another, which may be
# incompatible with the current clock settings. Therefore we check if the
# clock settings are in the list for the current chip.
#
# If they are not in the list, we either restore from a backup file,
# or set to a standard value for this chip.
#
# We maintain two backup files, one for the pi1 one for the pi2.
# If we think the current setting is for the other chip, we save i

from kano_settings.system import overclock
from kano_settings.boot_config import pi2_backup_config, pi1_backup_config
from kano.utils import is_model_2_b
from kano.logging import logger


def swap_clock_configs(this_config, other_config, curr_pi2):
    #  save the pi1(2) values in case the SD card is to be used later in a pi2(1)
    overclock.backup_overclock_values(other_config)

    if this_config.exists():
        logger.info("Restoring clock settings from backup")
        overclock.restore_overclock_values(this_config)
        if overclock.match_overclock_value(curr_pi2) is None:
            logger.info("Restored clock settings, but they were broken.")
            overclock.set_default_overclock_values(curr_pi2)
    else:
        # no saved config for the new chip, set to default
        overclock.set_default_overclock_values(curr_pi2)


def check_clock_config_matches_chip():
    """  Check if the clock setting in the current config is supported on
         the chip we have booted on.
         If not, try to restore from a backup file. If that is not possible,
         set to a default appropraite to this chip.
    """
    # This will need updating if another board is made.
    curr_pi2 = is_model_2_b()

    clock_setting_match_pi2 = overclock.match_overclock_value(True)
    clock_setting_match_pi1 = overclock.match_overclock_value(False)

    if curr_pi2:
        if clock_setting_match_pi2 is not None:
            return False  # config okay for pi2, do nothing
        elif clock_setting_match_pi1 is not None:
            # we are on a pi2 but the clock values match pi1
            logger.info("No match in overclock settings: restoring pi2 default")
            swap_clock_configs(pi2_backup_config, pi1_backup_config, curr_pi2)
        else:
            logger.info("Restoring pi2 default clock settings")
            # we are on pi2 and current clock doesn't match either pi1 or pi2
            overclock.set_default_overclock_values(curr_pi2)

    else:
        # exactly as above in reverse
        if clock_setting_match_pi1 is not None:
            return False  # config okay for pi1, do nothing
        elif clock_setting_match_pi2 is not None:
            # we are on a pi1 but the clock values match pi2
            swap_clock_configs(pi1_backup_config, pi2_backup_config, curr_pi2)
        else:
            # we are on pi1 and current clock doesn't match either pi1 or pi2
            logger.info("No match in overclock settings: restoring pi1 default")
            overclock.set_default_overclock_values(curr_pi2)

    return True  # we need to reboot if we get here
