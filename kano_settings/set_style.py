#
# set_style.py
#
# Copyright (C) 2015 - 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# This page has the screensaver and wallpaper options on different tabs
#

import os
import shutil

from kano.utils import run_cmd

from gi import require_version
require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk
from kano_settings.set_wallpaper import SetWallpaper
from kano_settings.set_screensaver import SetScreensaver
from kano_settings.system.wallpaper import change_wallpaper


class SetStyle(Gtk.Notebook):

    def __init__(self, win):

        Gtk.Notebook.__init__(self)

        background = Gtk.EventBox()
        background.add(self)

        self.win = win
        self.win.set_main_widget(background)
        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.win.go_to_home)

        # Modify set_wallpaper so it doesn't add itself to the window
        wallpaper_widget = SetWallpaper(self.win)
        screensaver_widget = SetScreensaver(self.win)
        reset_widget = SetResetDesktop(self.win)

        wallpaper_label = Gtk.Label(_("BACKGROUND"))
        wallpaper_label_ebox = Gtk.EventBox()
        wallpaper_label_ebox.add(wallpaper_label)
        wallpaper_label_ebox.connect('realize', self._set_cursor_to_hand_cb)
        wallpaper_label_ebox.show_all()

        screensaver_label = Gtk.Label(_("SCREENSAVER"))
        screensaver_label_ebox = Gtk.EventBox()
        screensaver_label_ebox.add(screensaver_label)
        screensaver_label_ebox.connect('realize', self._set_cursor_to_hand_cb)
        screensaver_label_ebox.show_all()

        general_label = Gtk.Label(_("GENERAL"))
        general_label_ebox = Gtk.EventBox()
        general_label_ebox.add(general_label)
        general_label_ebox.connect('realize', self._set_cursor_to_hand_cb)
        general_label_ebox.show_all()

        # Add the screensaver and wallpaper tabs
        self.append_page(wallpaper_widget, wallpaper_label_ebox)
        self.append_page(screensaver_widget, screensaver_label_ebox)
        self.append_page(reset_widget, general_label_ebox)

        self.win.show_all()

    def _set_cursor_to_hand_cb(self, widget, data=None):
        widget.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.HAND1))


from kano.gtk3.buttons import KanoButton
from kano.gtk3.kano_dialog import KanoDialog


class SetResetDesktop(Gtk.Box):

    def __init__(self, win):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.win = win
        self.get_style_context().add_class('notebook_page')

        reset_button = KanoButton(text=_("RESET YOUR DESKTOP"), color='orange')
        reset_button.connect('button-release-event', self.reset_button_cb)
        reset_button.connect('key-release-event', self.reset_button_cb)
        reset_button.pack_and_align()
        reset_button.align.set(0.5, 0.5, 0, 0)

        self.pack_start(reset_button.align, True, True, 0)

    def reset_button_cb(self, widget, event):

        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

            kdialog = KanoDialog(
                title_text=_("This will reset your wallpaper and toolbar."),
                description_text=_("Do you want to continue?"),
                button_dict=[
                    {
                        'label': _("YES"),
                        'color': 'green',
                        'return_value': 'yes'
                    },
                    {
                        'label': _("NO"),
                        'color': 'red',
                        'return_value': 'no'
                    }
                ],
                parent_window=self.win
            )

            response = kdialog.run()

            if response == 'yes':
                self.reset_desktop()
                self.win.go_to_home()

    def restore_lxpanel_configuration(self):
        userid = os.getuid()
        groupid = os.getgid()
        original_lxpanel_path = '/etc/skel/.config/lxpanel/'
        user_lxpanel_path = os.path.join('/home/' + os.getenv('SUDO_USER'), '.config/lxpanel')

        # remove the current local copy
        shutil.rmtree(user_lxpanel_path, ignore_errors=True)

        # re-create the copy from the skeleton
        shutil.copytree(original_lxpanel_path, user_lxpanel_path, symlinks=False, ignore=None)
        for root, dirs, files in os.walk(user_lxpanel_path):
            for name in files:
                os.chown(os.path.join(root, name), userid, groupid)

        run_cmd('lxpanelctl restart')

    def restore_wallpaper(self):
        '''Restore the wallpaper to the system default.
        '''

        kdesk_path = "/usr/share/kano-desktop/kdesk/.kdeskrc"
        identifier = 'Background.File-medium: '

        # We split the default paths into the containing directory of the
        # wallpapers and the name of the file without the size.
        # This is so we can pass these parameters into the change_wallpaper
        # function, so it can decide the appropriate size to set the wallpaper.
        with open(kdesk_path) as f:
            for line in f:
                line = line.strip()

                if line.startswith(identifier):
                    line = line.replace(identifier, '').replace('-1024.png', '')
                    path = '/'.join(line.split('/')[:-1])
                    name = line.split('/')[-1]
                    change_wallpaper(path, name)

                    # finish once we change the wallpaper
                    return

    def reset_desktop(self):
        # Add functionality here
        self.restore_lxpanel_configuration()
        self.restore_wallpaper()
