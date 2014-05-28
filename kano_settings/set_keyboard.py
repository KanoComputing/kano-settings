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
from kano.gtk3.heading import Heading
import kano_settings.components.fixed_size_box as fixed_size_box
from .config_file import get_setting, set_setting


win = None  # TODO: Is it needed?
update = None

selected_layout = None
selected_country = None
selected_variant = None

selected_continent_index = 1
selected_country_index = 21
selected_variant_index = 0
selected_continent_hr = "America"
selected_country_hr = "USA"
selected_variant_hr = "generic"

variants_combo = None
countries_combo = None
continents_combo = None

continents = ['Africa', 'America', 'Asia', 'Australia', 'Europe', 'Others']

DROPDOWN_CONTAINER_HEIGHT = 118


class WorkerThread(threading.Thread):
    def __init__(self, callback):
        threading.Thread.__init__(self)
        self.callback = callback

    def run(self):
        # Apply the keyboard changes
        keyboard_config.set_keyboard(selected_country, selected_variant)

        # The callback runs a GUI task, so wrap it!
        GObject.idle_add(self.callback)


def activate(_win, box, _update):
    global win, continents_combo, variants_combo, countries_combo, continents, update

    update = _update
    update.set_sensitive(False)

    read_config()

    win = _win

    # Contains all the settings
    settings = fixed_size_box.Fixed()

    # Title
    title = Heading("Keyboard", "Which country do you live in?")

    # Create Continents Combo box
    continents_combo = Gtk.ComboBoxText.new()
    for c in continents:
        continents_combo.append_text(c)
    continents_combo.connect("changed", on_continent_changed)

    # Create Countries Combo box
    countries_combo = Gtk.ComboBoxText.new()
    countries_combo.connect("changed", on_country_changed)
    countries_combo.props.valign = Gtk.Align.CENTER

    # Create Variants Combo box
    variants_combo = Gtk.ComboBoxText.new()
    variants_combo.connect("changed", on_variants_changed)
    variants_combo.props.valign = Gtk.Align.CENTER

    # Set up default values in dropdown lists
    set_defaults("continent")
    set_defaults("country")
    set_defaults("variant")

    # Ceate various dropdown boxes so we can resize the dropdown lists appropriately
    # We create two boxes side by side, and then stack the country dropdow lists in one, and one by itself in the other

    #   dropdown_box_countries     dropdown_box_keys
    # |                        |                        |
    # |-------continents-------|                        |
    # |                        |                        |
    # |                        |---------variants-------|
    # |                        |                        |
    # |-------countries -------|                        |
    # |                        |                        |

    dropdown_box_countries = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
    dropdown_box_countries.set_size_request(230, 30)
    dropdown_box_countries.props.valign = Gtk.Align.CENTER
    dropdown_box_keys = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
    dropdown_box_keys.set_size_request(230, 30)
    dropdown_box_keys.props.valign = Gtk.Align.CENTER
    dropdown_box_countries.pack_start(continents_combo, False, False, 0)
    dropdown_box_countries.pack_start(countries_combo, False, False, 0)
    dropdown_box_keys.pack_start(variants_combo, False, False, 0)
    dropdown_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
    dropdown_container.pack_start(dropdown_box_countries, False, False, 0)
    dropdown_container.pack_start(dropdown_box_keys, False, False, 0)

    valign = Gtk.Alignment(xalign=0.5, yalign=0, xscale=0, yscale=0)
    padding_above = (settings.height - DROPDOWN_CONTAINER_HEIGHT) / 2
    valign.set_padding(padding_above, 0, 0, 0)
    valign.add(dropdown_container)
    settings.box.pack_start(valign, False, False, 0)

    box.pack_start(title.container, False, False, 0)
    box.pack_start(settings.box, False, False, 0)
    box.pack_start(update.align, False, False, 0)

    # Refresh window
    win.show_all()


def apply_changes(button):
    global win, update

    # Apply changes
    thread = WorkerThread(work_finished_cb)
    thread.start()

    # Save the changes in the config
    update_config()

    # Refresh window
    win.show_all()


# This function is used by auto_settings
def auto_changes(continent, country, variant):
    variant = variant.lower()
    # Get layout
    if continent == 'africa':
        layout = keyboard_layouts.layouts_africa
    elif continent == 'america':
        layout = keyboard_layouts.layouts_america
    elif continent == 'asia':
        layout = keyboard_layouts.layouts_asia
    elif continent == 'australia':
        layout = keyboard_layouts.layouts_australia
    elif continent == 'europe':
        layout = keyboard_layouts.layouts_europe
    elif continent == 'others':
        layout = keyboard_layouts.layouts_others
    # Apply the keyboard changes
    country_code = keyboard_config.find_country_code(country, layout)
    keyboard_config.set_keyboard(country_code, variant)


def read_config():
    global selected_continent_index, selected_country_index, selected_variant_index, selected_continent_hr, selected_country_hr, selected_variant_hr

    selected_continent_index = get_setting("Keyboard-continent-index")
    selected_country_index = get_setting("Keyboard-country-index")
    selected_variant_index = get_setting("Keyboard-variant-index")
    selected_continent_hr = get_setting("Keyboard-continent-human")
    selected_country_hr = get_setting("Keyboard-country-human")
    selected_variant_hr = get_setting("Keyboard-variant-human")


def update_config():
    # Add new configurations to config file.
    set_setting("Keyboard-continent-index", selected_continent_index)
    set_setting("Keyboard-country-index", selected_country_index)
    set_setting("Keyboard-variant-index", selected_variant_index)
    set_setting("Keyboard-continent-human", selected_continent_hr)
    set_setting("Keyboard-country-human", selected_country_hr)
    set_setting("Keyboard-variant-human", selected_variant_hr)


# setting = "variant", "continent" or "country"
def set_defaults(setting):
    global continents_combo, countries_combo, variants_combo

    # Set the default info on the dropdown lists
    # "Keyboard-continent":continents_combo, "Keyboard-country", "Keyboard-variant"]:

    active_item = get_setting("Keyboard-" + setting + "-index")

    if setting == "continent":
        continents_combo.set_active(int(active_item))
    elif setting == "country":
        countries_combo.set_active(int(active_item))
    elif setting == "variant":
        variants_combo.set_active(int(active_item))
    else:
        print("Bad argument in set_defaults - should be 'continent', 'country' or 'variant'")
        return


def on_continent_changed(combo):
    global selected_continent_hr, selected_continent_index, update

    continent = selected_continent_hr
    tree_iter = combo.get_active_iter()

    if tree_iter is not None:
        model = combo.get_model()
        continent = model[tree_iter][0]

    selected_continent_hr = str(continent)
    selected_continent_index = str(combo.get_active())

    update.set_sensitive(False)

    fill_countries_combo(selected_continent_hr)
    win.show_all()


def on_country_changed(combo):
    global win, selected_country, selected_country_index, selected_country_hr, selected_layout, variants_combo, update

    country = None
    tree_iter = combo.get_active_iter()

    if tree_iter is not None:
        model = combo.get_model()
        country = model[tree_iter][0]

    if not country:
        return

    # Remove entries from variants combo box
    variants_combo.remove_all()
    selected_country_hr = str(country)
    selected_country_index = combo.get_active()

    # Refresh variants combo box
    selected_country = keyboard_config.find_country_code(country, selected_layout)
    variants = keyboard_config.find_keyboard_variants(selected_country)
    variants_combo.append_text("generic")
    if variants is not None:
        for v in variants:
            variants_combo.append_text(v[0])

    update.set_sensitive(False)

    # Refresh window
    win.show_all()


def on_variants_changed(combo):
    global win, selected_variant, selected_variant_hr, selected_variant_index, update

    tree_iter = combo.get_active_iter()
    if tree_iter is not None:
        model = combo.get_model()
        variant = model[tree_iter][0]
        update.set_sensitive(True)
        if variant == "generic":
            selected_variant = selected_variant_hr = str(variant)
            selected_variant_index = 0
            return
        # Select the variant code
        variants = keyboard_config.find_keyboard_variants(selected_country)
        if variants is not None:
            for v in variants:
                if v[0] == variant:
                    selected_variant = v[1]
                    selected_variant_index = combo.get_active()
                    selected_variant_hr = str(variant)

    # Refresh window
    win.show_all()


def work_finished_cb():
    print("Finished updating keyboard")


def fill_countries_combo(continent):
    global win, countries_combo, variants_combo, selected_layout, selected_continent_hr

    continent = continent.lower()

    if continent == 'africa':
        selected_layout = keyboard_layouts.layouts_africa
    elif continent == 'america':
        selected_layout = keyboard_layouts.layouts_america
    elif continent == 'asia':
        selected_layout = keyboard_layouts.layouts_asia
    elif continent == 'australia':
        selected_layout = keyboard_layouts.layouts_australia
    elif continent == 'europe':
        selected_layout = keyboard_layouts.layouts_europe
    elif continent == 'others':
        selected_layout = keyboard_layouts.layouts_others

    selected_continent_hr = continent

    # Remove entries from countries and variants combo box
    countries_combo.remove_all()
    variants_combo.remove_all()

    sorted_countries = sorted(selected_layout)

    # Refresh countries combo box
    for country in sorted_countries:
        countries_combo.append_text(country)

    win.show_all()
