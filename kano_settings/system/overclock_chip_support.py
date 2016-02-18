# overclock_chip_support.py
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

from kano.utils.hardware import get_rpi_model
from kano.logging import logger

from kano_settings.boot_config import BACKUP_BOOT_CONFIG_TEMPLATE, BootConfig
from kano_settings.system import overclock


def restore_config(config, model):
    if config.exists():
        logger.info(
            "Restoring clock settings for {} from backup".format(model)
        )
        overclock.restore_overclock_values(config)

        if overclock.match_overclock_value(model) is None:
            logger.info("Restored clock settings, but they were broken.")
            overclock.set_default_overclock_values(model)
    else:
        logger.info(
            "Restoring default clock settings for {}".format(model)
        )
        # no saved config for the new chip, set to default
        overclock.set_default_overclock_values(model)

def check_clock_config_matches_chip():
    """  Check if the clock setting in the current config is supported on
         the chip we have booted on.
         If not, try to restore from a backup file. If that is not possible,
         set to a default appropraite to this chip.
    """

    current_model = get_rpi_model()
    old_model = overclock.get_board_with_overclock_value()

    if current_model == old_model:
        # Config looks good
        return False

    new_config_file = BACKUP_BOOT_CONFIG_TEMPLATE.format(model=current_model)
    new_config = BootConfig(new_config_file)
    if old_model:
        logger.info("Config settings match for {} but running {}. "
                    "Backing up old settings and restoring new settings"
                    .format(old_model, current_model))

        old_config_file = BACKUP_BOOT_CONFIG_TEMPLATE.format(model=old_model)
        old_config = BootConfig(old_config_file)
        overclock.backup_overclock_values(old_config)

    restore_config(new_config, current_model)

    return True  # we need to reboot if we get here
