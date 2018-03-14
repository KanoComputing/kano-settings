# account.py
#
# Copyright (C) 2014-2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Contains the account screen backend functions


import os

# When this module was transitioned from pip (0.1.4) to deb (0.4.2-13.1), the
# version in Raspbian contained an all caps name for the module.
try:
    import PAM as pam
except ImportError:
    import pam

from kano.utils import run_cmd
from kano_world.functions import has_token


class UserError(Exception):
    pass


# Needs sudo permission
def add_user():
    # Imported locally to avoid circular dependency
    try:
        from kano_init.tasks.add_user import schedule_add_user
        schedule_add_user()
    except ImportError:
        raise UserError("Unable to create the user. kano-init not found.")


# Needs sudo permission
def delete_user():
    # Imported locally to avoid circular dependency
    try:
        from kano_init.tasks.delete_user import schedule_delete_user
        schedule_delete_user()
    except ImportError:
        raise UserError("Unable to delete the user. kano-init not found.")

    # back up profile
    if has_token():
        os.system("kano-sync --sync --backup")


# Returns True if password matches system password, else returns False
def verify_current_password(password):
    # Verify the current password in the first text box
    # Get current username
    username, e, num = run_cmd("echo $SUDO_USER")

    # Remove trailing newline character
    username = username.rstrip()

    if not pam.authenticate(username, password):
        # Could not verify password
        return False

    return True


# Successfully changed password is returns 0, else is successful
def change_password(new_password):
    out, e, cmdvalue = run_cmd("echo $SUDO_USER:{} | chpasswd".format(new_password))
    return cmdvalue
