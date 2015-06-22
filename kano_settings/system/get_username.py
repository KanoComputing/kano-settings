#!/usr/bin/env python

# get_username.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License:   http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Get the name of the first user if they exist

import pwd
import grp

pwd_field_id = {
    'pw_name': 0,
    'pw_passwd': 1,
    'pw_uid': 2,
    'pw_gid': 3,
    'pw_gecos': 4,
    'pw_dir': 5,
    'pw_shell': 6
}

grp_field_id = {
    'gr_name': 0,
    'gr_passwd': 1,
    'gr_gid': 2,
    'gr_mem': 3
    }

def get_real_users():
    try:
        users = grp.getgrnam('kanousers')[grp_field_id['gr_mem']]
        user_data = [pwd.getpwnam(u) for u in users]
        return user_data
    except:
        return None

def get_first_username():
    real_users = get_real_users()
    if real_users:
        real_users.sort(key=lambda x: x[pwd_field_id['pw_uid']])
        if len(real_users) > 0:
            return real_users[0][pwd_field_id['pw_name']]

    return None
