#!/usr/bin/env python3

# set_keyboard.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
import keyboard_layouts
import keyboard_config
import os
import config_file
import re

win = None  # TODO: Is it needed?
selected_country = None
selected_variant = "Generic"
variants_combo = None
country_combo = None
button = None
USER = os.environ['LOGNAME']
settings_path = "/home/%s/.kano-settings" % (USER) 


def activate(_win, table, box, title, description):
    global win, variants_combo, button, country_combo

    win = _win

    # Title
    title.set_text("Change your keyboard settings")

    # Description
    description.set_text("Which country do you live?")
    
    # Table
    table = Gtk.Table(4, 1, True)
    box.add(table)

    # Create Country Combo box
    country_store = Gtk.ListStore(str)
    
    # Sort the countries into alphabetical order
    countries = sorted(keyboard_layouts.layouts)

    for country in countries:
        country_store.append([country])

    country_combo = Gtk.ComboBox.new_with_model(country_store);

    # What happens when dropdown list is changed
    country_combo.connect("changed", on_country_changed)
    renderer_text = Gtk.CellRendererText()
    country_combo.pack_start(renderer_text, True)
    country_combo.add_attribute(renderer_text, "text", 0)
    table.attach(country_combo, 0, 1, 1, 2)

    # Create Variants Combo box
    variants_combo = Gtk.ComboBoxText.new()
    variants_combo.connect("changed", on_variants_changed)
    table.attach(variants_combo, 0, 1, 2, 3)

    # Refresh window
    win.show_all()

    # Set up in file in .kano-settings  
    try:
        f = open(settings_path, 'r+')
        # Format, "keyboard:country,second_choice"
        file_content = str(f.read())
        file_index = file_content.index('Keyboard:') + len("Keyboard:")
        file_index2 = file_content[file_index:].index(',') # Return first comma after Keyboard
        file_index3 = file_content[file_index:].index('\n') # Get selected variant of that country
        country_substring = file_content[file_index: file_index + file_index2]
        variant_substring = file_content[file_index + file_index2 + 1: file_index + file_index3]
        country_combo.set_active(int(country_substring))
        variants_combo.set_active(int(variant_substring))

    except:
        f = open(settings_path, "w+")
        usa_index = countries.index('USA')
        country_combo.set_active(usa_index)
        variants_combo.set_active(0)
        f.write("Keyboard:" + str(usa_index) + "," + str(0) + "\n")
        
    f.close()


def apply_changes(button):
    global win, selected_country

    # print("Set the keyboard layout to %s, with variant" % selected_country, selected_variant)
    keyboard_config.set_keyboard(selected_country, selected_variant)
    button.hide()
    
    # Refresh window
    win.show_all()

    # Update .kano-settings with new current_country and current_variant   
    try:
        f = open(settings_path, 'r+')
        file_content = str(f.read())
        f.close()

        file_index = file_content.index('Keyboard:')
        file_index3 = file_content[file_index:].index('\n') # Get selected variant of that country
        old_string = file_content[file_index: file_index3]

        selected_country_index = country_combo.get_active()
        selected_variants_index = variants_combo.get_active()
        new_string = "Keyboard:" + str(selected_country_index) + "," + str(selected_variants_index)

        config_file.file_replace(settings_path, old_string, new_string)

    except:
        # Fail silently
        return 


def on_country_changed(combo):
    global win, selected_country, variants_combo, button, country_combo

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
    global win, selected_variant, button, variant_combo

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