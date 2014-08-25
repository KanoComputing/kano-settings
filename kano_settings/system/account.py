#!/usr/bin/env python

# account.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Contains the account screen backend functions

import os
import pam
from kano.utils import get_user_unsudoed, run_cmd
from kano_settings.data import get_data


# Needs sudo permission
def delete_user():
    os.system('kano-init deleteuser %s' % (get_user_unsudoed()))


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
    out, e, cmdvalue = run_cmd("echo $SUDO_USER:%s | chpasswd" % (new_password))
    return cmdvalue


# Returns a title, description and whether the process was successful or not
def verify_and_change_password(old_password, new_password1, new_password2):
    data = get_data("SET_PASSWORD")
    success = False

    password_verified = verify_current_password(old_password)

    if not password_verified:
        title = "Could not change password"
        description = "Your old password is incorrect!"

    # If the two new passwords match
    elif new_password1 == new_password2:
        cmdvalue = change_password(new_password1)

        # if password is not changed
        if cmdvalue != 0:
            title = data["PASSWORD_ERROR_TITLE"]
            description = data["PASSWORD_ERROR_1"]
        else:
            title = data["PASSWORD_SUCCESS_TITLE"]
            description = data["PASSWORD_SUCCESS_DESCRIPTION"]
            success = True
    else:
        title = data["PASSWORD_ERROR_TITLE"]
        description = data["PASSWORD_ERROR_2"]

    return (title, description, success)
