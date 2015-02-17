#!/usr/bin/env python

# parental_config.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk

from kano import logging
from kano_settings import common
from kano_settings.templates import Template, EditableList
from kano.gtk3.buttons import OrangeButton
from kano.gtk3.kano_dialog import KanoDialog

from kano_settings.data import get_data
from kano_settings.config_file import get_setting, set_setting
from system.advanced import write_whitelisted_sites, write_blacklisted_sites, \
    read_listed_sites, set_parental_level, authenticate_parental_password


class ParentalConfig(Template):

    LANGUAGE = get_data('PARENTAL_CONFIG')

    def __init__(self, win):

        title = self.LANGUAGE['TITLE']
        description = self.LANGUAGE['DESCRIPTION']
        kano_label = self.LANGUAGE['KANO_BUTTON']

        Template.__init__(self, title, description, kano_label)

        self.parental_level = Gtk.VScale(
           adjustment= Gtk.Adjustment(value=0, lower=0, upper=2,
                                      step_incr=1, page_incr=0, page_size=0))
        self.parental_level.set_draw_value(False)
        self.parental_level.set_round_digits(0)
        self.parental_level.set_inverted(True)
        self.parental_level.set_value(get_setting('Parental-level'))
        self.parental_level.connect('value-changed', self._value_change_handler)

        self._parental_labels = [
            (Gtk.Label(self.LANGUAGE['LOW']),
             Gtk.Label(self.LANGUAGE['LOW_DESC'])),
            (Gtk.Label(self.LANGUAGE['MEDIUM']),
             Gtk.Label(self.LANGUAGE['MEDIUM_DESC'])),
            (Gtk.Label(self.LANGUAGE['HIGH']),
             Gtk.Label(self.LANGUAGE['HIGH_DESC']))
        ]

        self._value_change_handler(self.parental_level)

        parental_level_grid = Gtk.Grid()
        parental_level_grid.attach(self.parental_level, 0, 0, 1, 6)
        parental_level_grid.attach(self._parental_labels[2][0], 1, 0, 1, 1)
        parental_level_grid.attach(self._parental_labels[2][1], 1, 1, 1, 1)
        parental_level_grid.attach(self._parental_labels[1][0], 1, 2, 1, 1)
        parental_level_grid.attach(self._parental_labels[1][1], 1, 3, 1, 1)
        parental_level_grid.attach(self._parental_labels[0][0], 1, 4, 1, 1)
        parental_level_grid.attach(self._parental_labels[0][1], 1, 5, 1, 1)

        blacklist_button = OrangeButton("Configure allowed/blocked")
        blacklist_button.connect("button-press-event",
                                 self.go_to_blacklist)

        self.box.set_spacing(20)
        self.box.pack_start(parental_level_grid, False, False, 0)
        self.box.pack_start(blacklist_button, False, False, 0)

        self.win = win

        self.win.set_main_widget(self)

        self.win.change_prev_callback(self.win.go_to_home)
        self.win.top_bar.enable_prev()

        self.kano_button.connect('button-release-event', self.apply_changes)
        self.kano_button.connect('key-release-event', self.apply_changes)
        self.win.show_all()

    def apply_changes(self, button, event):
        pw_dialog = ParentalPasswordDialog()
        if not pw_dialog.verify():
            return

        level = self.parental_level.get_value()
        set_parental_level(level)
        set_setting('Parental-level', level)
        common.need_reboot = True

        self.win.go_to_home()

    def go_to_blacklist(self, button, event):
        self.win.clear_win()
        AllowedSites(self.win)

    def _value_change_handler(self, gtk_range):
        for level, (title, desc) in enumerate(self._parental_labels):
            style = title.get_style_context()
            if gtk_range.get_value() == level:
                style.add_class('parental_activated')
            else:
                style.remove_class('parental_activated')
                style.add_class('normal_label')


class SiteList(EditableList):

    def __init__(self, size_x=250, size_y=25):
        EditableList.__init__(self, size_x=size_x, size_y=size_y)

    @staticmethod
    def _sanitise_site(site):
        return site.replace(' ', '').lstrip('www.')

    def _item_edited_handler(self, cellrenderertext, path, new_text):
        site = self._sanitise_site(new_text)
        EditableList._item_edited_handler(self, cellrenderertext, path, site)


class AllowedSites(Template):

    LANGUAGE = get_data('PARENTAL_BLACKLIST')

    def __init__(self, win):
        title = self.LANGUAGE['TITLE']
        description = self.LANGUAGE['DESCRIPTION']
        kano_label = self.LANGUAGE['KANO_BUTTON']

        self.win = win

        Template.__init__(self, title, description, kano_label)

        blacklist, whitelist = read_listed_sites()

        self.blacklist = SiteList(size_x=250, size_y=25)
        self.whitelist = SiteList(size_x=250, size_y=25)

        if whitelist:
            for site in whitelist:
                self.whitelist.edit_list_store.append([site])

        if blacklist:
            for site in blacklist:
                self.blacklist.edit_list_store.append([site])

        grid = Gtk.Grid()
        grid.set_column_spacing(40)

        grid.attach(
            Gtk.Label(self.LANGUAGE['BLACKLIST']), 0, 0, 1, 1)
        grid.attach(self.blacklist, 0, 1, 1, 1)
        grid.attach(
            Gtk.Label(self.LANGUAGE['WHITELIST']), 1, 0, 1, 1)
        grid.attach(self.whitelist, 1, 1, 1, 1)
        self.box.pack_start(grid, False, False, 0)

        self.box.pack_start(Gtk.Label(''), False, False, 0)

        self.win.set_main_widget(self)

        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.go_to_parental_config)

        self.kano_button.connect('button-release-event', self.apply_changes)
        self.kano_button.connect('key-release-event', self.apply_changes)
        self.win.show_all()

        self.win.show_all()

    def apply_changes(self, button, event):
        pw_dialog = ParentalPasswordDialog()
        if not pw_dialog.verify():
            return

        whitelist = [row[0] for row in self.whitelist.edit_list_store]
        blacklist = [row[0] for row in self.blacklist.edit_list_store]

        write_whitelisted_sites(whitelist)
        write_blacklisted_sites(blacklist)

        set_parental_level(get_setting('Parental-level'))
        common.need_reboot = True

        self.win.go_to_home()

    def go_to_parental_config(self, button=None, event=None):
        self.win.clear_win()
        ParentalConfig(self.win)


class ParentalPasswordDialog(KanoDialog):

    def __init__(self):
        entry = Gtk.Entry()
        entry.set_visibility(False)
        KanoDialog.__init__(
            self,
            title_text='Parental Authentication',
            description_text='Enter your parental password:',
            widget=entry,
            has_entry=True,
            global_style=True,
            parent_window=None
        )

    def verify(self):
        pw = self.run()

        if authenticate_parental_password(pw):
            return True

        fail = KanoDialog(
            title_text='Try again?',
            description_text='The password was incorrect. Not applying changes',
            parent_window=self
        )
        fail.run()

        return False
