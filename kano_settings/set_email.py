#!/usr/bin/env python
#
# set_email.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
from pwd import getpwnam
import os
import re
import kano_settings.config_file as config_file
import kano_settings.components.icons as icons
import kano_settings.components.heading as heading
import kano_settings.components.fixed_size_box as fixed_size_box

entry1 = None
entry2 = None
update = None
USER = None
USER_ID = None
current_email = None
success_icon = None
tick = None
cross = None
win = None
EMAIL_ENTRY_HEIGHT = 135


def is_email(email):
    pattern = '[\.\w]{1,}[@]\w+[.]\w+'
    if re.match(pattern, email):
        return True
    else:
        return False


def activate(_win, changeable_content, _update):
    global current_email, USER, USER_ID, tick, cross, success_icon, entry1, entry2, update

    # Init user detail
    USER = os.environ['SUDO_USER']
    USER_ID = getpwnam(USER).pw_uid

    # Get existent email
    email_path = "/home/%s/.useremail" % (USER)
    try:
        with open(email_path, 'r') as f:
            current_email = f.readline()
    except:
        pass

    title = heading.Heading("Change your email", "Stay informed about your progress")

    # Settings container
    settings = fixed_size_box.Fixed()

    update = _update

    # Text entry
    text = ""
    email_entry = Gtk.Grid(column_homogeneous=False,
                           column_spacing=22,
                           row_spacing=22)

    success_icon = Gtk.Image()
    tick = icons.Icons("tick").subpixbuf
    cross = icons.Icons("cross").subpixbuf

    entry1 = Gtk.Entry()
    entry1.set_size_request(250, 44)
    entry2 = Gtk.Entry()
    entry2.set_sensitive(False)
    entry2.set_size_request(250, 44)

    if current_email is not None:
        text = current_email.replace('\n', '')
        update_config()

    entry1.props.placeholder_text = "Email"
    entry1.set_text(text)
    check_email(entry1, 1)

    email_entry.attach(entry1, 0, 0, 1, 1)
    email_entry.attach(entry2, 0, 1, 1, 1)
    email_entry.attach(success_icon, 1, 0, 1, 1)

    valign = Gtk.Alignment(xalign=0.5, yalign=0, xscale=0, yscale=0)
    padding_above = (settings.height - EMAIL_ENTRY_HEIGHT) / 2
    valign.set_padding(padding_above, 0, 47, 0)
    valign.add(email_entry)
    settings.box.pack_start(valign, False, False, 0)

    changeable_content.pack_start(title.container, False, False, 0)
    changeable_content.pack_start(settings.box, False, False, 0)
    changeable_content.pack_start(update.box, False, False, 0)

    update.disable()

    entry1.connect('key_release_event', check_email)
    entry2.connect('key_release_event', check_match)


def read_config():
    return config_file.read_from_file("Email")


def update_config():
    # Add new configurations to config file.
    config_file.replace_setting("Email", current_email)


def check_match(entry, event):
    global entry1, entry2, update

    email1 = entry1.get_text()
    email2 = entry2.get_text()

    if email1 == email2:
        update.enable()
    else:
        update.disable()


def check_email(entry, event):
    global success_icon, entry2

    email = entry.get_text()
    # Validate email
    if not is_email(email):
        success_icon.set_from_pixbuf(cross)
        entry2.set_sensitive(False)

    else:
        success_icon.set_from_pixbuf(tick)
        entry2.set_sensitive(True)


def apply_changes(button):
    global entry1, entry2, current_email

    email1 = entry1.get_text()

    # First time user introduces the email
    if current_email is None:
        # Create user email files
        os.system("echo %s > /home/%s/.email" % (email1, USER))
        os.system("chown %s:%s /home/%s/.email" % (USER_ID, USER_ID, USER))
        os.system("cp --preserve /home/%s/.email /home/%s/.useremail" % (USER, USER))
    # Email is being updated
    elif current_email != email1:
        os.system("echo %s > /home/%s/.useremail" % (email1, USER))

    config_file.replace_setting("Email", email1)

    return 1
