# screens.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Structures to hold the screens
#

from collections import OrderedDict

from kano.utils import get_user_unsudoed

import kano_settings.common as common
from kano_settings.config_file import get_setting
from kano_settings.components.menu_button import Menu_button

from kano_settings.set_keyboard import choose_keyboard_screen
from kano_settings.set_mouse import SetMouse
from kano_settings.set_notifications import SetNotifications
from kano_settings.set_font import SetFont
from kano_settings.set_audio import SetAudio
from kano_settings.set_display import SetDisplay
from kano_settings.set_wifi import SetWifi, SetProxy
from kano_settings.no_internet_screen import NoInternet
from kano_settings.set_overclock import SetOverclock
from kano_settings.set_account import SetAccount
from kano_settings.set_about import SetAbout
from kano_settings.set_advanced import SetAdvanced, SetPassword
from kano_settings.set_appearance import SetAppearance
from kano_settings.set_wallpaper import FirstBootSetWallpaper
from kano_settings.locale import LocaleConfig


class Screen(object):
    """
    NB: screen_no is here for legacy reasons - remove as soon as support is
        withdrawn.
    """

    def __init__(self, name, label, screen_widget,
                 screen_no=None, on_home_screen=True,
                 setting_param=None):
        self.name = name
        self._label = label
        self.screen_widget = screen_widget
        self.screen_no = screen_no
        self.on_home_screen = on_home_screen
        self.menu_button = None
        self._setting_param = setting_param

    def create_menu_button(self, cb):
        self.menu_button = button = Menu_button(self._label, '')
        button.button.state = self.screen_no
        button.button.connect('clicked', cb, self.name)

    def refresh_menu_button(self):
        description = ''

        if self._setting_param:
            description = get_setting(self._setting_param)
        else:
            if self.name == 'wifi':
                if common.has_internet:
                    description = 'Connected'
                else:
                    description = 'Not connected'

            elif self.name == 'account':
                description = get_user_unsudoed()

            elif self.name == 'display':
                return

        self.menu_button.description.set_text(description)


class ScreenCollection(OrderedDict):

    def __init__(self, screens):
        super(ScreenCollection, self).__init__()

        for screen in screens:
            self[screen.name] = screen

    def get_screen_from_number(self, number):
        for screen in self.itervalues():
            if screen.screen_no == number:
                return screen

    def get_screens_on_home(self):
        displayed_screens = []

        for screen in self.itervalues():
            if screen.on_home_screen:
                displayed_screens.append(screen)

        return displayed_screens


SCREENS = ScreenCollection([
    Screen('keyboard', 'Keyboard', choose_keyboard_screen, screen_no=0,
           setting_param='Keyboard-country-human'),
    Screen('mouse', 'Mouse', SetMouse, screen_no=1, setting_param='Mouse'),
    Screen('audio', 'Audio', SetAudio, screen_no=2, setting_param='Audio'),
    Screen('display', 'Display', SetDisplay, screen_no=3),
    Screen('wifi', 'WiFi', SetWifi, screen_no=4),
    Screen('overclocking', 'Overclocking', SetOverclock, screen_no=5,
           setting_param='Overclocking'),
    Screen('account', 'Account', SetAccount, screen_no=6),
    Screen('appearance', 'Appearance', SetAppearance, screen_no=7,
           setting_param='Wallpaper'),
    Screen('font', 'Font', SetFont, screen_no=8, setting_param='Font'),
    Screen('advanced', 'Advanced', SetAdvanced, screen_no=9),
    Screen('about', 'About', SetAbout, screen_no=10),
    Screen('notifications', 'Notifications', SetNotifications, screen_no=11),
    Screen('no-internet', 'No-internet', NoInternet, screen_no=12,
           on_home_screen=False),
    Screen('proxy', 'proxy', SetProxy, screen_no=13, on_home_screen=False),
    Screen('first-boot-set-wallpaper', 'first-boot-set-wallpaper',
           FirstBootSetWallpaper, screen_no=14, on_home_screen=False),
    Screen('set-parental-password', 'set-parental-password', SetPassword,
           screen_no=15, on_home_screen=False),
    # TODO: Add 'Locale' screen to home screen when translations are available.
    # TODO: Add icon for the 'Locale' screen.
    Screen('locale', 'Locale', LocaleConfig, setting_param='Locale',
           on_home_screen=False),
])
