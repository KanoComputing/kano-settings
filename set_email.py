#!/usr/bin/env python3

# set_email.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Pango, GdkPixbuf
from pwd import getpwnam
import os
import re
import kano_settings.config_file as config_file
#import config_file

entry1 = None
entry2 = None
USER = None
USER_ID = None
current_email = None
success_icon = None
tick = None
cross = None
win = None



def is_email(email):
    pattern = '[\.\w]{1,}[@]\w+[.]\w+'
    if re.match(pattern, email):
        return True
    else:
        return False

    

def activate(_win, box, apply_changes):
    global current_email, USER, USER_ID, tick, cross, success_icon, entry1, entry2

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

     # Heading

    title = Gtk.Label()
    title.modify_font(Pango.FontDescription("Bariol 16"))
    description = Gtk.Label()
    description.modify_font(Pango.FontDescription("Bariol 14"))

    title_style = title.get_style_context()
    title_style.add_class('title')

    description_style = description.get_style_context()
    description_style.add_class('description')

    title_container = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing=0)
    title_container.add(title)
    title_container.set_size_request(300, 100)
    title_container.pack_start(description, True, True, 10)
    info_style = title_container.get_style_context()
    info_style.add_class('title_container')

    # Title
    title.set_text("Change your email")

    # Description
    description.set_text("Change the email address")

    # Settings container
    settings_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    settings_container.set_size_request(400, 250)
    settings_container.pack_start(title_container, False, False, 0)

    # Text entry
    text = "Email"

    email_entry = Gtk.Table(2, 2, False)
    success_icon = Gtk.Image()
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size("/usr/lib/python3/dist-packages/kano_settings/media/Icons/systemsetup-icons.png", 192, 24)
    tick = pixbuf.new_subpixbuf(120, 0, 24, 24).add_alpha(True,255,255,255)
    # To change image to tick:
    # success_icon.set_from_pixbuf(cross)

    cross = pixbuf.new_subpixbuf(144, 0, 24, 24).add_alpha(True,255,255,255)
    # To change image to cross:
    # success_icon.set_from_pixbuf(cross)

    entry1 = Gtk.Entry()
    entry1.modify_font(Pango.FontDescription("Bariol 13"))
    entry1.set_size_request(300, 50)
    entry2 = Gtk.Entry()
    entry2.modify_font(Pango.FontDescription("Bariol 13"))
    entry2.set_sensitive(False)
    entry2.set_size_request(300, 50)

    if current_email is not None:
        text = current_email.replace('\n', '')

    entry1.set_text(text)
    check_email(entry1, 1)

    email_entry.attach(entry1, 0, 1, 0, 1, Gtk.AttachOptions.FILL, Gtk.AttachOptions.EXPAND, 10)
    email_entry.attach(entry2, 0, 1, 1, 2,Gtk.AttachOptions.FILL, Gtk.AttachOptions.EXPAND, 10)
    email_entry.attach(success_icon, 1, 2, 0, 1)

    settings_container.pack_start(email_entry, False, False, 0)
    box.pack_start(settings_container, False, False, 0)
    box.pack_start(apply_changes, False, False, 0)

    entry1.connect('key_press_event', check_email)


def check_email(entry, event):
    global success_icon, entry2

    email = entry.get_text()
    # Validate email
    if not is_email(email):
        print("Email validation failed")
        success_icon.set_from_pixbuf(cross)
        entry2.set_sensitive(False)

    else:
        success_icon.set_from_pixbuf(tick)
        entry2.set_sensitive(True)


def apply_changes(button):
    global entry1, entry2, current_email

    email1 = entry1.get_text()
    email2 = entry2.get_text()

    if email1 != email2:
        # Bring in message dialog box
        dialog = Gtk.MessageDialog(win, 0, Gtk.MessageType.ERROR,
            Gtk.ButtonsType.CANCEL, "Your emails don't match!")
        dialog.format_secondary_text(
            "Please re-enter")
        response = dialog.run()
        dialog.destroy()
        return -1

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
