#!/usr/bin/env python
#
# password.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Controls the UI of the change password screen

from gi.repository import Gtk
from kano.gtk3.heading import Heading
import kano_settings.components.fixed_size_box as fixed_size_box
from kano.gtk3.kano_dialog import KanoDialog
from ..config_file import set_setting
import crypt
import shutil
import os

win = None
entry = None
entry1 = None
entry2 = None
parental = None


def activate(_win, _box, _button, _parental):
    global win, entry1, entry2, entry, parental

    win = _win
    settings = fixed_size_box.Fixed()
    parental = _parental

    # Entry container
    entry_container = Gtk.Grid(column_homogeneous=False,
                               column_spacing=22,
                               row_spacing=10)
    align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
    align.add(entry_container)

    if parental:
        entry1 = Gtk.Entry()
        entry1.set_size_request(300, 44)
        entry1.props.placeholder_text = "Select password"
        entry1.set_visibility(False)
        entry2 = Gtk.Entry()
        entry2.props.placeholder_text = "Confirm password"
        entry2.set_visibility(False)
        entry1.connect("key_release_event", enable_button, _button)
        entry2.connect("key_release_event", enable_button, _button)
        entry_container.attach(entry1, 0, 0, 1, 1)
        entry_container.attach(entry2, 0, 1, 1, 1)
        # Move email entries down by 25px
        align.set_padding(25, 0, 0, 0)
    else:
        entry = Gtk.Entry()
        entry.set_size_request(300, 44)
        entry.props.placeholder_text = "Confirm your password"
        entry.set_visibility(False)
        entry.connect("key_release_event", enable_button, _button)
        entry_container.attach(entry, 0, 0, 1, 1)
        # Move email entries down by 50px
        align.set_padding(50, 0, 0, 0)

    settings.box.pack_start(align, False, False, 0)
    _button.set_sensitive(False)
    title = Heading("Parental lock", "Enter password")

    _box.pack_start(title.container, False, False, 0)
    _box.pack_start(settings.box, False, False, 0)
    _box.pack_start(_button.align, False, False, 10)

    win.show_all()


def apply_changes(button=None):
    if parental:
        password1 = entry1.get_text()
        password2 = entry2.get_text()
        passed_test = (password1 == password2)
        error_heading = "Careful"
        error_description = "The passwords don't match! Try again"
    else:
        # TODO: Verify entered password is correct
        entered_password = entry.get_text()
        passed_test = True
        error_heading = "The password you entered is incorrect"
        error_description = "Have another go?"

    # If the two new passwords match
    if passed_test:
        if parental:
            # TODO: create encrypted password
            pass
        # pass setting of checkbutton to here
        update_config()
    else:
        response = create_dialog(error_heading, error_description)
        if response == -1:
            if parental:
                clear_text()
            else:
                entry.set_text("")
        return response

    return 0


def create_dialog(message1="Could not change password", message2=""):
    kdialog = KanoDialog(message1, message2, {"TRY AGAIN": {"return_value": -1}, "GO BACK": {"return_value": 0}})
    response = kdialog.run()
    return response


def clear_text():
    global entry1, entry2
    entry1.set_text("")
    entry2.set_text("")


def enable_button(widget=None, event=None, apply_changes=None):
    if parental:
        text1 = entry1.get_text()
        text2 = entry2.get_text()
        apply_changes.set_sensitive(text1 != "" and text2 != "")
    else:
        text = entry.get_text()
        apply_changes.set_sensitive(text != "")


def update_config():
    # FIXME: I am using a fake fixed password momentarily until the UI flow is complete
    if parental:
        fake_password = 'Fake123Password'
        set_setting("Parental-password", fake_password)
        set_setting("Parental-lock", crypt.crypt('True', fake_password))
        set_hosts_blacklist(enable=True)
    else:
        set_setting("Parental-password", "")
        set_setting("Parental-lock", 'False')
        set_hosts_blacklist(enable=False)


def set_hosts_blacklist(enable=True, blacklist_file='/usr/share/kano-settings/media/Parental/parental-hosts-blacklist.gz'):
    blacklisted = False
    hosts_file = '/etc/hosts'
    hosts_file_backup = '/etc/kano-hosts-parental-backup'
    bare_hosts = ['127.0.0.1 kano', '127.0.0.1 localhost']

    if enable:
        # Populate a list of hosts which should not be reached (Parental browser protection)
        if os.stat(hosts_file).st_size > 1024 * 10:
            # sanity check: this is a big file, looks like the blacklist is already in place!
            pass
        else:
            # make a copy of hosts file and APPEND it with a list of blacklisted internet hostnames.
            # tighten security to the file so regular users can't peek at these host names.
            shutil.copyfile(hosts_file, hosts_file_backup)
            os.system('zcat %s >> %s' % (blacklist_file, hosts_file))
            os.system('chmod 400 %s' % (hosts_file))
            blacklisted = True
    else:
        # Restore the original list of hosts
        try:
            os.stat(hosts_file_backup)
            shutil.copy(hosts_file_backup, hosts_file)
        except:
            # the backup is gone, recreate it simply by the bare minimum needed
            with open(hosts_file, 'wt') as hhh:
                for host in bare_hosts:
                    hhh.write(host + '\n\r')

    return blacklisted
