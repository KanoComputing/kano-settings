#!/usr/bin/env python3

# set_keyboard.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
import keyboard_layouts
import keyboard_config

win = None  # TODO: Is it needed?
selected_country = None
selected_variant = "Generic"
variants_combo = None
button = None


def activate(_win, table, box):
    global win, variants_combo, button

    win = _win

    # Table
    table = Gtk.Table(4, 1, True)
    box.add(table)

    # Label
    label = Gtk.Label()
    label.set_text("Keyboard")
    label.set_justify(Gtk.Justification.LEFT)
    table.attach(label, 0, 1, 0, 1)

    # Create Country Combo box
    country_store = Gtk.ListStore(str)
    
    # Sort the countries into alphabetical order
    countries = sorted(keyboard_layouts.layouts)

    for country in countries:
        country_store.append([country])
        print(country)
    country_combo = Gtk.ComboBox.new_with_model(country_store)
    country_combo.connect("changed", on_country_changed)
    renderer_text = Gtk.CellRendererText()
    country_combo.pack_start(renderer_text, True)
    country_combo.add_attribute(renderer_text, "text", 0)
    table.attach(country_combo, 0, 1, 1, 2)

    # Create Variants Combo box
    variants_combo = Gtk.ComboBoxText.new()
    variants_combo.connect("changed", on_variants_changed)
    table.attach(variants_combo, 0, 1, 2, 3)

    # Apply button
    button = Gtk.Button("Apply changes")
    button.connect("clicked", apply_changes)
    table.attach(button, 0, 1, 3, 4)
    button.hide()
    # Refresh window
    win.show_all()


def apply_changes(button):
    global win, selected_country

    # print("Set the keyboard layout to %s, with variant" % selected_country, selected_variant)
    keyboard_config.set_keyboard(selected_country, selected_variant)
    button.hide()
    
    # Refresh window
    win.show_all()


def on_country_changed(combo):
    global win, selected_country, variants_combo, button

    tree_iter = combo.get_active_iter()
    if tree_iter is not None:
        model = combo.get_model()
        country = model[tree_iter][0]
    button.show()
    # Remove entries from variants combo box
    variants_combo.remove_all()
    # Refresh variants combo box
    selected_country = keyboard_config.find_country_code(country)
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
    # Refresh window
    button.show()
    # Refresh window
    win.show_all()
