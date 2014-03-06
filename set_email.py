#!/usr/bin/env python3

# set_email.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Pango
from pwd import getpwnam
import os
import re
import dialog_box

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


def activate(_win, table, box, title, description):
    global entry, current_email

    # Get existent email
    email_path = "/home/%s/.useremail" % (USER)
    try:
        with open(email_path, 'r') as f:
            current_email = f.readline()
    except:
        pass

    # Title
    title.set_text("Change your email")

    #description
    description.set_text("Change the email address")

    # Table
    table = Gtk.Table(4, 1, True)
    box.add(table)

    # Text entry
    text = "Email"

    entry1 = Gtk.Entry()
    entry1.modify_font(Pango.FontDescription("Bariol 13"))
    entry2 = Gtk.Entry()
    entry2.modify_font(Pango.FontDescription("Bariol 13"))
    entry2.set_sensitive(False)

    if current_email is not None:
        text = current_email.replace('\n', '')
        entry2.set_sensitive(True)

    entry1.set_text(text)
    
    table.attach(entry1, 0, 1, 0, 1)
    table.attach(entry2, 0, 1, 1, 2)


def apply_changes(button):
    global entry, current_email

    email = entry.get_text()
    # Valudate email
    if not is_email(email):
        #print("Email validation failed")

        # Bring in message dialog box
        dialog = Gtk.Dialog()
        bad_email_alert = dialog_box.DialogWindow(dialog, "The email you entered is invalid.  Please enter a different one.")
        response = bad_email_alert.run()

        if response == Gtk.ResponseType.OK:
            bad_email_alert.destroy() 
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
