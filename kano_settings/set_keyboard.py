#!/usr/bin/env python

# set_keyboard.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Pango
import kano_settings.keyboard.keyboard_layouts as keyboard_layouts
import kano_settings.keyboard.keyboard_config as keyboard_config
import kano_settings.components.heading as heading

win = None  # TODO: Is it needed?
selected_layout = None
selected_country = None
selected_variant = "Generic"
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
    settings_box.set_size_request(200, 50)
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

    # Create Variants Combo box
    variants_combo = Gtk.ComboBoxText.new()
    variants_combo.connect("changed", on_variants_changed)

    dropdown_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    dropdown_box.pack_start(continents_combo, False, False, 10)
    dropdown_box.pack_start(countries_combo, False, False, 10)
    dropdown_box.pack_start(variants_combo, False, False, 10)

    settings_box.pack_start(dropdown_box, False, False, 30)
    box.pack_start(update.box, False, False, 0)

    # Refresh window
    win.show_all()

    continents_combo.get_child().modify_font(Pango.FontDescription("Bariol 13"))
    variants_combo.get_child().modify_font(Pango.FontDescription("Bariol 13"))
    countries_combo.get_child().modify_font(Pango.FontDescription("Bariol 13"))


def apply_changes(button):
    global win, selected_country

    # print("Set the keyboard layout to %s, with variant" % selected_country, selected_variant)
    keyboard_config.set_keyboard(selected_country, selected_variant)
    button.hide()

    # Refresh window
    win.show_all()


def on_continent_changed(combo):

    tree_iter = combo.get_active_iter()
    if tree_iter is not None:
        model = combo.get_model()
        continent = model[tree_iter][0]

    fill_countries_combo(continent)


def on_country_changed(combo):
    global win, selected_country, selected_layout, variants_combo, button

    country = None
    tree_iter = combo.get_active_iter()
    if tree_iter is not None:
        model = combo.get_model()
        country = model[tree_iter][0]

    if not country:
        return

    # Remove entries from variants combo box
    variants_combo.remove_all()
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
    global win, selected_variant, button

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

    button.show()
    # Refresh window
    win.show_all()


def fill_countries_combo(continent):
    global countries_combo, variants_combo, selected_layout

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

    #selected_layout = sorted(countries)

    # Remove entries from countries and variants combo box
    countries_combo.remove_all()
    variants_combo.remove_all()
    # Refresh countries combo box
    for country in selected_layout:
        countries_combo.append_text(country)

