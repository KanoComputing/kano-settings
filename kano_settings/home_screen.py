
from gi.repository import Gtk

from kano_settings.set_keyboard import choose_keyboard_screen
from kano_settings.set_mouse import SetMouse
from kano_settings.set_notifications import SetNotifications
from kano_settings.set_font import SetFont
from kano_settings.set_audio import SetAudio
from kano_settings.set_display import SetDisplay
from kano_settings.set_wifi import SetWifi
from kano_settings.no_internet_screen import NoInternet
from kano_settings.set_overclock import SetOverclock
from kano_settings.set_account import SetAccount
from kano_settings.set_about import SetAbout
from kano_settings.set_advanced import SetAdvanced
from kano_settings.set_wallpaper import SetWallpaper

import kano_settings.common as common
from kano_settings.components.menu_button import Menu_button
from kano_settings.config_file import get_setting

from kano.gtk3.scrolled_window import ScrolledWindow
from kano.utils import get_user_unsudoed


class HomeScreen(Gtk.Box):

    names = ["Keyboard", "Mouse", "Audio", "Display", "Wifi", "Overclocking", "Account", "Wallpaper", "Font",
             "Advanced", "About", "Notifications"]
    custom_info = ["Keyboard-country-human", "Mouse", "Audio", None, None, "Overclocking", None,
                   "Wallpaper", "Font"]

    def __init__(self, win, screen_number=None):
        # Check if we want to initialise another window first
        if screen_number is not None:
            self.state_to_widget(screen_number)(win)
            return

        Gtk.Box.__init__(self)

        self.win = win
        self.win.set_main_widget(self)
        self.win.top_bar.disable_prev()
        self.win.remove_prev_callback()

        self.width = 640
        self.height = 304
        self.number_of_columns = 2

        self.generate_grid()
        self.pack_start(self.scrolledwindow, True, True, 0)

        self.win.show_all()

    def generate_grid(self):
        buttons = []
        self.labels = []

        # names at top of file
        for x in range(len(self.names)):
            self.item = Menu_button(self.names[x], '')
            self.labels.append(self.item.description)
            # Update the state of the button, so we know which button has been clicked on.
            self.item.button.state = x
            self.item.button.connect("clicked", self.go_to_level)
            buttons.append(self.item.button)

        # Fill the tabs with the current information
        self.update_intro()

        # Create table
        numRows = len(self.names) / self.number_of_columns
        if len(self.names) % self.number_of_columns != 0:  # Odd number of elements
            numRows += 1
        self.table = Gtk.Table(numRows, self.number_of_columns, True, hexpand=True, vexpand=True)
        self.table.props.margin = 0

        # Attach to table
        index = 0
        row = 0
        while index < len(self.names):
            for j in range(0, self.number_of_columns):
                if index < len(self.names):
                    self.table.attach(buttons[index], j, j + 1, row, row + 1,
                                      Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND,
                                      Gtk.AttachOptions.FILL, 0, 0)
                    if row % 2:
                        buttons[index].get_style_context().add_class('appgrid_grey')
                    else:
                        buttons[index].get_style_context().add_class('appgrid_white')
                    index += 1
                else:
                    break
            row += 1

        # for scroll bar
        self.scrolledwindow = ScrolledWindow(wide_scrollbar=True, vexpand=True,
                                             hexpand=True)
        self.scrolledwindow.get_style_context().add_class("app-grid")
        self.scrolledwindow.add_with_viewport(self.table)

        # This is to update the introdction text, so that if the settings are modified and then we go back to the
    # intro screen, the latest information is shown
    def update_intro(self):
        for x in range(len(self.custom_info)):

            if self.names[x] == 'Wifi':
                text = ''
                if common.has_internet:
                    text = 'Connected'
                else:
                    text = 'Not connected'
                self.labels[x].set_text(text)

            elif self.names[x] == 'Account':
                text = get_user_unsudoed()
                self.labels[x].set_text(text)

            elif self.names[x] == 'Display':
                continue

            else:
                self.labels[x].set_text(get_setting(self.custom_info[x]))

    # When clicking next in the default intro screen - takes you to the last level you visited
    def on_next(self, widget=None, arg2=None):

        self.state_to_widget(self.win.last_level_visited)(self.win)
        self.win.last_level_visited = self.win.state
        # Do not do win.show_all() as will stop the combotextbox in set_keyboard being hidden properly

    # On clicking a level button on default intro screen
    def go_to_level(self, widget):

        # Update current state
        self.win.state = widget.state
        # Record this level so we can go back to it
        self.win.last_level_visited = self.win.state

        # Call next state
        self.win.clear_win()
        self.state_to_widget(self.win.state)(self.win)

    # On clicking a level button on default intro screen
    def go_to_level_given_state(self, state):

        # Remove element in the dynamic box
        self.win.clear_win()

        # Update current state
        self.win.state = state
        # Record this level so we can go back to it
        self.win.last_level_visited = self.win.state

        # Call next state
        self.state_to_widget(self.win.state)(self.win)

        # Refresh window
        self.win.show_all()

    def state_to_widget(self, x):
        return {
            0: choose_keyboard_screen,
            1: SetMouse,
            2: SetAudio,
            3: SetDisplay,
            4: SetWifi,
            5: SetOverclock,
            6: SetAccount,
            7: SetWallpaper,
            8: SetFont,
            9: SetAdvanced,
            10: SetAbout,
            11: SetNotifications,
            12: NoInternet,
        }[x]
