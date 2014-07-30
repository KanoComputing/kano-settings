#!/usr/bin/env python

# set_keyboard.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, GObject
GObject.threads_init()
import threading
import kano_settings.keyboard.keyboard_layouts as keyboard_layouts
import kano_settings.keyboard.keyboard_config as keyboard_config
from kano_settings.templates import Template
import kano_settings.constants as constants
from .config_file import get_setting, set_setting
from kano.gtk3.buttons import OrangeButton
from kano.utils import detect_kano_keyboard
from kano.logging import logger

selected_country = None
selected_variant = None


class WorkerThread(threading.Thread):
    def __init__(self, callback):
        threading.Thread.__init__(self)
        self.callback = callback

    def run(self):
        # Apply the keyboard changes
        keyboard_config.set_keyboard(selected_country, selected_variant)

        # The callback runs a GUI task, so wrap it!
        GObject.idle_add(self.callback)


def choose_keyboard_screen(win):
    # Check for kano-keyboard
    kano_keyboard = detect_kano_keyboard()
    if kano_keyboard:
        SetKanoKeyboard(win)

    else:
        SetKeyboard(win)


class SetKanoKeyboard(Template):
    def __init__(self, win):
        Template.__init__(self, "Keyboard", "Kano keyboard detected", "BACK")
        self.win = win
        self.win.set_main_widget(self)
        self.top_bar.enable_prev()

        # height is 106px
        img = Gtk.Image()
        img.set_from_file(constants.media + "/Graphics/keyboard.png")

        # Link to advance options
        self.to_advance_button = OrangeButton("Layout options")
        self.to_advance_button.connect("button_press_event", self.to_advance)

        self.kano_button.connect("button-release-event", self.win.go_to_home)
        self.top_bar.set_prev_callback(self.win.go_to_home)

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
    selected_country_index = 21
    selected_variant_index = 0
    selected_continent_hr = "America"
    selected_country_hr = "USA"
    selected_variant_hr = "generic"
    variants_combo = None
    continents = ['Africa', 'America', 'Asia', 'Australia', 'Europe', 'Others']
    kano_keyboard = True

    def __init__(self, win):

        Template.__init__(self, "Keyboard", "Where do you live? So I can set your keyboard", "APPLY CHANGES")

        self.win = win
        self.win.set_main_widget(self)
        self.read_config()

        kano_keyboard = detect_kano_keyboard()
        self.top_bar.enable_prev()

        if kano_keyboard:
            self.kano_button.connect("button-release-event", self.go_to_kano_screen)
            self.top_bar.set_prev_callback(self.go_to_kano_screen)
        else:
            self.kano_button.connect("button-release-event", self.win.go_to_home)
            self.top_bar.set_prev_callback(self.win.go_to_home)

        self.kano_button.connect("button-release-event", self.apply_changes)

        # change text on button
        self.kano_button.set_label("APPLY CHANGES")

        # Make sure continue button is enabled
        self.kano_button.set_sensitive(False)

        # Create Continents Combo box
        self.continents_combo = Gtk.ComboBoxText.new()
        for c in self.continents:
            self.continents_combo.append_text(c)
        self.continents_combo.connect("changed", self.on_continent_changed)

        # Create Countries Combo box
        self.countries_combo = Gtk.ComboBoxText.new()
        self.countries_combo.connect("changed", self.on_country_changed)
        self.countries_combo.props.valign = Gtk.Align.CENTER

        # Create Advance mode checkbox
        advance_button = Gtk.CheckButton("Advanced options")
        advance_button.set_can_focus(False)
        advance_button.props.valign = Gtk.Align.CENTER
        advance_button.connect("clicked", self.on_advance_mode)
        advance_button.set_active(False)

        # Create Variants Combo box
        self.variants_combo = Gtk.ComboBoxText.new()
        self.variants_combo.connect("changed", self.on_variants_changed)
        self.variants_combo.props.valign = Gtk.Align.CENTER

        # Set up default values in dropdown lists
        self.set_defaults("continent")
        self.set_defaults("country")
        self.set_defaults("variant")

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

    def go_to_kano_screen(self, widget, event):
        self.win.clear_win()
        SetKanoKeyboard(self.win)

    def refresh_window(self):
        self.win.show_all()
        self.variants_combo.hide()

    def apply_changes(self, button, event):

        # Apply changes
        thread = WorkerThread(self.work_finished_cb)
        thread.start()

        # Save the changes in the config
        self.update_config()

        # Refresh window
        #self.win.go_to_home()
        self.win.show_all()

    def read_config(self):
        self.selected_continent_index = get_setting("Keyboard-continent-index")
        self.selected_country_index = get_setting("Keyboard-country-index")
        self.selected_variant_index = get_setting("Keyboard-variant-index")
        self.selected_continent_hr = get_setting("Keyboard-continent-human")
        self.selected_country_hr = get_setting("Keyboard-country-human")
        self.selected_variant_hr = get_setting("Keyboard-variant-human")

    def update_config(self):
        logger.info('set_keyboard.update_config {} {} {} {} {} {}'.format(
            self.selected_continent_index,
            self.selected_country_index,
            self.selected_variant_index,
            self.selected_continent_hr,
            self.selected_country_hr,
            self.selected_variant_hr
        ))

        # Add new configurations to config file.
        set_setting("Keyboard-continent-index", self.selected_continent_index)
        set_setting("Keyboard-country-index", self.selected_country_index)
        set_setting("Keyboard-variant-index", self.selected_variant_index)
        set_setting("Keyboard-continent-human", self.selected_continent_hr)
        set_setting("Keyboard-country-human", self.selected_country_hr)
        set_setting("Keyboard-variant-human", self.selected_variant_hr)

    # setting = "variant", "continent" or "country"
    def set_defaults(self, setting):

        # Set the default info on the dropdown lists
        # "Keyboard-continent":continents_combo, "Keyboard-country", "Keyboard-variant"]:

        active_item = get_setting("Keyboard-" + setting + "-index")

        if setting == "continent":
            self.continents_combo.set_active(int(active_item))
        elif setting == "country":
            self.countries_combo.set_active(int(active_item))
        elif setting == "variant":
            self.variants_combo.set_active(int(active_item))
        else:
            logger.error("Bad argument in set_defaults - should be 'continent', 'country' or 'variant'")
            return

    def set_variants_to_generic(self):
        self.variants_combo.set_active(0)

    def on_continent_changed(self, combo):

        continent = self.selected_continent_hr
        tree_iter = combo.get_active_iter()

        if tree_iter is not None:
            model = combo.get_model()
            continent = model[tree_iter][0]

        self.selected_continent_hr = str(continent)
        self.selected_continent_index = str(combo.get_active())

        self.kano_button.set_sensitive(False)

        self.fill_countries_combo(self.selected_continent_hr)

    def on_country_changed(self, combo):
        global selected_country

        country = None
        tree_iter = combo.get_active_iter()

        if tree_iter is not None:
            model = combo.get_model()
            country = model[tree_iter][0]

        if not country:
            return

        # Remove entries from variants combo box
        self.variants_combo.remove_all()
        self.selected_country_hr = str(country)
        self.selected_country_index = combo.get_active()

        # Refresh variants combo box
        selected_country = keyboard_config.find_country_code(country, self.selected_layout)
        variants = keyboard_config.find_keyboard_variants(selected_country)
        self.variants_combo.append_text("generic")
        if variants is not None:
            for v in variants:
                self.variants_combo.append_text(v[0])

        self.set_variants_to_generic()

    def on_variants_changed(self, combo):
        global selected_variant

        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            variant = model[tree_iter][0]
            self.kano_button.set_sensitive(True)
            if variant == "generic":
                selected_variant = self.selected_variant_hr = str(variant)
                self.selected_variant_index = 0
                return
            # Select the variant code
            variants = keyboard_config.find_keyboard_variants(selected_country)
            if variants is not None:
                for v in variants:
                    if v[0] == variant:
                        selected_variant = v[1]
                        self.selected_variant_index = combo.get_active()
                        self.selected_variant_hr = str(variant)

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

        if continent == 'africa':
            self.selected_layout = keyboard_layouts.layouts_africa
        elif continent == 'america':
            self.selected_layout = keyboard_layouts.layouts_america
        elif continent == 'asia':
            self.selected_layout = keyboard_layouts.layouts_asia
        elif continent == 'australia':
            self.selected_layout = keyboard_layouts.layouts_australia
        elif continent == 'europe':
            self.selected_layout = keyboard_layouts.layouts_europe
        elif continent == 'others':
            self.selected_layout = keyboard_layouts.layouts_others

        self.selected_continent_hr = continent

        # Remove entries from countries and variants combo box
        self.countries_combo.remove_all()
        self.variants_combo.remove_all()

        sorted_countries = sorted(self.selected_layout)

        # Refresh countries combo box
        for country in sorted_countries:
            self.countries_combo.append_text(country)
