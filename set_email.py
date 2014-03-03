#!/usr/bin/env python3

# set_email.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
from pwd import getpwnam
import os
import re

USER = os.environ['LOGNAME']
USER_ID = getpwnam(USER).pw_uid
entry = None
current_email = None


def is_email(email):
    pattern = '[\.\w]{1,}[@]\w+[.]\w+'
    if re.match(pattern, email):
        return True
    else:
        return False


def activate(_win, table, box):
    global entry, current_email

    # Get existent email
    email_path = "/home/%s/.useremail" % (USER)
    try:
        with open(email_path, 'r') as f:
            current_email = f.readline()
    except:
        pass
    print(email_path)
    print(current_email)

    # Table
    table = Gtk.Table(4, 1, True)
    box.add(table)

    # Label
    label = Gtk.Label()
    label.set_text("Email")
    label.set_justify(Gtk.Justification.LEFT)
    table.attach(label, 0, 1, 0, 1)

    # Text entry
    text = "Email"
    if current_email is not None:
        text = current_email.replace('\n', '')
    entry = Gtk.Entry()
    entry.set_text(text)
    table.attach(entry, 0, 1, 1, 2)

    # Apply button
    button = Gtk.Button("Apply changes")
    button.connect("clicked", apply_changes)
    table.attach(button, 0, 1, 3, 4)


def apply_changes(button):
    global entry, current_email

    email = entry.get_text()
    # Valudate email
    if not is_email(email):
        print("Email validation failed")
        return

    # First time user introduces the email
    if current_email is None:
        # Create user email files
        os.system("echo %s > /home/%s/.email" % (email, USER))
        os.system("chown %s:%s /home/%s/.email" % (USER_ID, USER_ID, USER))
        os.system("cp --preserve /home/%s/.email /home/%s/.useremail" % (USER, USER))
    # Email is being updated
    elif current_email != email:
        os.system("echo %s > /home/%s/.useremail" % (email, USER))
