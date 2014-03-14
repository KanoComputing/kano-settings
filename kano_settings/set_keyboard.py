#!/usr/bin/env python3

# set_keyboard.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Pango
import kano_settings.keyboard.keyboard_layouts as keyboard_layouts
import kano_settings.keyboard.keyboard_config as keyboard_config
import kano_settings.config_file as config_file
import kano_settings.components.heading as heading

win = None  # TODO: Is it needed?
selected_layout = None
selected_continent = "america"
selected_country = 108
selected_variant = 0
selected_continent_hr = "America"
selected_country_hr = "USA"
selected_variant_hr = "Generic"
variants_combo = None
countries_combo = None
button = None

continents = ['africa', 'america', 'asia', 'australia', 'europe', 'others']


def activate(_win, box, update):
    global win, variants_combo, countries_combo, continents, button

    win = _win
    button = update.button

    # Contains all the settings
    settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    box.add(settings_box)

    # Title
    title = heading.Heading("Change your keyboard settings", "Which country do you live in?")
    settings_box.pack_start(title.container, False, False, 0)

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

    dropdown_box_countries = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    dropdown_box_countries.set_size_request(230, 30)
    dropdown_box_keys = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    dropdown_box_keys.set_size_request(230, 30)
    dropdown_box_countries.pack_start(continents_combo, False, False, 10)
    dropdown_box_countries.pack_start(countries_combo, False, False, 10)
    dropdown_box_keys.pack_start(variants_combo, False, False, 10)
    dropdown_container = Gtk.Box()
    dropdown_container.pack_start(dropdown_box_countries, False, False, 10)
    dropdown_container.pack_start(dropdown_box_keys, False, False, 10)

    on_continent_changed(continents_combo)
    on_country_changed(countries_combo)
    on_variants_changed(variants_combo)

    update_config()

    settings_box.pack_start(dropdown_container, False, False, 30)
    box.pack_start(update.box, False, False, 0)

    # Refresh window
    win.show_all()

    continents_combo.get_child().modify_font(Pango.FontDescription("Bariol 13"))
    variants_combo.get_child().modify_font(Pango.FontDescription("Bariol 13"))
    countries_combo.get_child().modify_font(Pango.FontDescription("Bariol 13"))


def apply_changes(button):
    global win, selected_country, selected_variant

    # print("Set the keyboard layout to %s, with variant" % selected_country, selected_variant)
    keyboard_config.set_keyboard(selected_country, selected_variant)
    button.hide()
    # Refresh window
    win.show_all()


def update_config():
    # Add new configurations to config file.
    config_file.replace_setting("Keyboard-continent", str(selected_continent))
    config_file.replace_setting("Keyboard-country", str(selected_country))
    config_file.replace_setting("Keyboard-variant", str(selected_variant))
    config_file.replace_setting("Keyboard-continent-human", str(selected_continent_hr))
    config_file.replace_setting("Keyboard-country-human", str(selected_country_hr))
    config_file.replace_setting("Keyboard-variant-human", str(selected_variant_hr))


def on_continent_changed(combo):
    global selected_continent_hr, selected_continent

    continent = selected_continent

    tree_iter = combo.get_active_iter()
    if tree_iter is not None:
        model = combo.get_model()
        continent = model[tree_iter][0]

    selected_continent_hr = str(continent)
    selected_continent = str(continent)

    fill_countries_combo(selected_continent)


def on_country_changed(combo):
    global win, selected_country, selected_country_hr, selected_layout, variants_combo, button

    country = ""
    tree_iter = combo.get_active_iter()
    if tree_iter is not None:
        model = combo.get_model()
        country = model[tree_iter][0]
    if country is None:
        return

    # Remove entries from variants combo box
    variants_combo.remove_all()
    selected_country_hr = str(country)

    # Refresh variants combo box
    selected_country = keyboard_config.find_country_code(country, selected_layout)
    variants = keyboard_config.find_keyboard_variants(selected_country)
    variants_combo.append_text("Generic")
    if variants is not None:
        for v in variants:
            variants_combo.append_text(v[0])

    # Refresh window
    win.show_all()


def on_variants_changed(combo):
    global win, selected_variant, button, selected_variants_hr

    tree_iter = combo.get_active_iter()
    if tree_iter is not None:
        model = combo.get_model()
        variant = model[tree_iter][0]
        # Select the variant code
        variants = keyboard_config.find_keyboard_variants(selected_country)
        if variants is not None:
            for v in variants:
                if v[0] == variant:
                    selected_variant = v[1]
                    selected_variants_hr = str(variant)


    button.show()

    # Refresh window
    win.show_all()


def fill_countries_combo(continent):
    global countries_combo, variants_combo, selected_layout, selected_continent_hr

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

    # Refresh countries combo box
    for country in selected_layout:
        countries_combo.append_text(country)
