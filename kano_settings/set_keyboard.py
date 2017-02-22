#!/usr/bin/env python

# set_keyboard.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import threading
from gi.repository import Gtk, GObject

import kano_settings.system.keyboard_layouts as keyboard_layouts
import kano_settings.system.keyboard_config as keyboard_config
import kano_settings.common as common
from kano_settings.templates import Template
from kano_settings.config_file import get_setting
from kano.gtk3.buttons import OrangeButton
from kano.gtk3.kano_combobox import KanoComboBox
from kano.utils import detect_kano_keyboard
from kano.logging import logger


def choose_keyboard_screen(win):
    # Check for kano-keyboard
    kano_keyboard = detect_kano_keyboard()
    if kano_keyboard:
        SetKanoKeyboard(win)

    else:
        SetKeyboard(win)


class SetKanoKeyboard(Template):
    def __init__(self, win):
        Template.__init__(
            self,
            _("Keyboard"),
            _("Kano keyboard detected"),
            _("APPLY CHANGES")
        )

        self.win = win
        self.win.set_main_widget(self)
        self.win.top_bar.enable_prev()

        # height is 106px
        img = Gtk.Image()
        img.set_from_file(common.media + "/Graphics/keyboard.png")

        # Link to advance options
        self.to_advance_button = OrangeButton(_("Layout options"))
        self.to_advance_button.connect('button_press_event', self.to_advance)

        self.kano_button.connect('button-release-event', self.win.go_to_home)
        self.win.change_prev_callback(self.win.go_to_home)

        self.box.pack_start(img, False, False, 0)
        self.box.pack_start(self.to_advance_button, False, False, 0)

        # Refresh window
        self.win.show_all()

    def to_advance(self, widget, event):

        self.win.clear_win()
        SetKeyboard(self.win)


class SetKeyboard(Template):
    selected_layout = None
    selected_continent_index = 1
    selected_country = None
    selected_country_index = 21
    selected_variant = None
    selected_variant_index = 0
    selected_continent_hr = 'America'
    selected_country_hr = 'USA'
    selected_variant_hr = 'generic'
    variants_combo = None
    continents = keyboard_layouts.get_continents()
    kano_keyboard = True

    def __init__(self, win):
        Template.__init__(
            self,
            _("Keyboard"),
            _("Where do you live? So I can set your keyboard."),
            _("APPLY CHANGES")
        )

        self.win = win
        self.win.set_main_widget(self)
        self.read_config()

        kano_keyboard = detect_kano_keyboard()
        self.win.top_bar.enable_prev()

        if kano_keyboard:
            self.win.change_prev_callback(self.go_to_kano_screen)
        else:
            self.win.change_prev_callback(self.win.go_to_home)

        self.kano_button.connect('button-release-event', self.apply_changes)

        # Make sure continue button is enabled
        self.kano_button.set_sensitive(False)

        # Create Continents Combo box
        self.continents_combo = KanoComboBox(max_display_items=7)
        for c in self.continents:
            self.continents_combo.append(c)
        self.continents_combo.connect('changed', self.on_continent_changed)

        # Create Countries Combo box
        self.countries_combo = KanoComboBox(max_display_items=7)
        self.countries_combo.connect('changed', self.on_country_changed)
        self.countries_combo.props.valign = Gtk.Align.CENTER

        # Create Advance mode checkbox
        advance_button = Gtk.CheckButton(_("Advanced options"))
        advance_button.set_can_focus(False)
        advance_button.props.valign = Gtk.Align.CENTER
        advance_button.connect('clicked', self.on_advance_mode)
        advance_button.set_active(False)

        # Create Variants Combo box
        self.variants_combo = KanoComboBox(max_display_items=7)
        self.variants_combo.connect('changed', self.on_variants_changed)
        self.variants_combo.props.valign = Gtk.Align.CENTER

        # Set up default values in dropdown lists
        self.set_defaults('continent')
        self.fill_countries_combo(self.continents_combo.get_selected_item_text())
        self.set_defaults('country')
        self.on_country_changed(self.countries_combo)
        self.set_defaults('variant')

        # Ceate various dropdown boxes so we can resize the dropdown lists appropriately
        # We create two boxes side by side, and then stack the country dropdow lists in one, and one by itself in the other

        #   dropdown_box_countries     dropdown_box_keys
        # |                        |                        |
        # |-------continents-------|   Advance option       |
        # |                        |                        |
        # |                        |                        |
        # |-------countries -------|--------variants--------|
        # |                        |                        |

        dropdown_box_countries = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        dropdown_box_countries.set_size_request(230, 30)
        dropdown_box_countries.props.valign = Gtk.Align.CENTER
        dropdown_box_keys = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        dropdown_box_keys.set_size_request(230, 30)
        dropdown_box_countries.pack_start(self.continents_combo, False, False, 0)
        dropdown_box_countries.pack_start(self.countries_combo, False, False, 0)
        dropdown_box_keys.pack_start(advance_button, False, False, 0)
        dropdown_box_keys.pack_start(self.variants_combo, False, False, 0)
        dropdown_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        dropdown_container.pack_start(dropdown_box_countries, False, False, 0)
        dropdown_container.pack_start(dropdown_box_keys, False, False, 0)

        self.box.pack_start(dropdown_container, False, False, 0)

        # show all elements except the advanced mode
        self.refresh_window()

    def go_to_kano_screen(self, widget=None, event=None):
        self.win.clear_win()
        SetKanoKeyboard(self.win)

    def refresh_window(self):
        self.win.show_all()
        self.variants_combo.hide()

    def apply_changes(self, button, event):

        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == 65293:

            def lengthy_process():
                if keyboard_config.is_changed(self.selected_country, self.selected_variant):
                    # Apply the keyboard changes
                    keyboard_config.set_keyboard(self.selected_country, self.selected_variant)

                    # A reboot is needed to apply the new keyboard to QT5 apps
                    common.need_reboot = True
                    
                # The callback runs a GUI task, so wrap it!
                GObject.idle_add(self.work_finished_cb)

            # Save the changes in the config file
            self.update_config()

            # An then apply the new saved changes
            thread = threading.Thread(target=lengthy_process)
            thread.start()

            kano_keyboard = detect_kano_keyboard()

            # Go back a screen
            if kano_keyboard:
                self.go_to_kano_screen()
            else:
                self.win.go_to_home()

            self.win.show_all()

    def read_config(self):
        self.selected_continent_index = get_setting('Keyboard-continent-index')
        self.selected_country_index = get_setting('Keyboard-country-index')
        self.selected_variant_index = get_setting('Keyboard-variant-index')
        self.selected_continent_hr = get_setting('Keyboard-continent-human')
        self.selected_country_hr = get_setting('Keyboard-country-human')
        self.selected_variant_hr = get_setting('Keyboard-variant-human')

    def update_config(self):
        keyboard_config.update_settings_keyboard_conf(
            self.selected_continent_index,
            self.selected_country_index,
            self.selected_variant_index,
            self.selected_continent_hr,
            self.selected_country_hr,
            self.selected_variant_hr
        )

    # setting = "variant", "continent" or "country"
    def set_defaults(self, setting):

        # Set the default info on the dropdown lists
        # 'Keyboard-continent':continents_combo, 'Keyboard-country', 'Keyboard-variant']:

        active_item = get_setting('Keyboard-' + setting + '-index')

        if setting == 'continent':
            self.continents_combo.set_selected_item_index(int(active_item))
        elif setting == 'country':
            self.countries_combo.set_selected_item_index(int(active_item))
        elif setting == 'variant':
            self.variants_combo.set_selected_item_index(int(active_item))
        else:
            logger.error("Bad argument in set_defaults - should be 'continent', 'country' or 'variant'")
            return

    def set_variants_to_generic(self):
        self.variants_combo.set_selected_item_index(0)

    def set_variants_to_mac_layout(self):

        # If the country is the United States, select the generic setting
        if self.selected_country_hr.upper() == 'UNITED STATES':
            self.set_variants_to_generic()
            return

        # Otherwise, try and find a Macintosh variant
        layout = keyboard_layouts.layouts[self.selected_continent_hr]
        index = keyboard_config.find_macintosh_index(self.selected_country_hr, layout)

        # If the macintosh variant exists, set it
        if index:
            self.variants_combo.set_selected_item_index(index)

        # if not found, select generic
        else:
            self.set_variants_to_generic()

    def on_continent_changed(self, combo):

        # making sure the continent has been set
        continent_text = combo.get_selected_item_text()
        continent_index = combo.get_selected_item_index()
        if not continent_text or continent_index == -1:
            return

        self.selected_continent_hr = continent_text
        self.selected_continent_index = continent_index

        self.kano_button.set_sensitive(False)
        self.fill_countries_combo(self.selected_continent_hr)

        # Use the first country as the default value for country combo
        self.countries_combo.set_selected_item_index(0)
        self.on_country_changed(self.countries_combo)

    def on_country_changed(self, combo):

        # making sure the country has been set
        country_text = combo.get_selected_item_text()
        country_index = combo.get_selected_item_index()
        if not country_text or country_index == -1:
            return

        # Remove entries from variants combo box
        self.variants_combo.remove_all()
        self.selected_country_hr = country_text
        self.selected_country_index = country_index

        # Refresh variants combo box
        self.selected_country = keyboard_config.find_country_code(country_text, self.selected_layout)
        variants = keyboard_config.find_keyboard_variants(self.selected_country)
        self.variants_combo.append('generic')
        if variants is not None:
            for v in variants:
                self.variants_combo.append(v[0])

        # if kano keyboard is connected, change to Mac layout
        kano_keyboard = detect_kano_keyboard()

        if kano_keyboard:
            self.set_variants_to_mac_layout()
        else:
            self.set_variants_to_generic()
        self.on_variants_changed(self.variants_combo)

    def on_variants_changed(self, combo):

        # making sure the variant has been set
        variant_text = combo.get_selected_item_text()
        variant_index = combo.get_selected_item_index()
        if not variant_text or variant_index == -1:
            return

        self.kano_button.set_sensitive(True)

        if variant_text == 'generic':
            self.selected_variant = self.selected_variant_hr = variant_text
            self.selected_variant_index = 0
            return
        # Select the variant code
        variants = keyboard_config.find_keyboard_variants(self.selected_country)
        if variants is not None:
            for v in variants:
                if v[0] == variant_text:
                    self.selected_variant = v[1]
                    self.selected_variant_index = variant_index
                    self.selected_variant_hr = variant_text

    def on_advance_mode(self, button):
        if int(button.get_active()):
            self.variants_combo.show()
        else:
            self.variants_combo.hide()

    def work_finished_cb(self):
        # Finished updating keyboard
        pass

    def fill_countries_combo(self, continent):
        continent = continent.lower()

        self.selected_layout = keyboard_layouts.get_countries_for_continent(
            continent
        )

        self.selected_continent_hr = continent

        # Remove entries from countries and variants combo box
        self.countries_combo.remove_all()
        self.variants_combo.remove_all()

        # Get a sorted list of the countries from the dict layout
        sorted_countries = keyboard_layouts.sorted_countries(
            self.selected_layout
        )

        # Refresh countries combo box
        for country in sorted_countries:
            self.countries_combo.append(country)
