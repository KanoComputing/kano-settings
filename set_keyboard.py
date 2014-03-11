#!/usr/bin/env python3

# set_keyboard.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Pango
#import kano_settings.keyboard_layouts as keyboard_layouts
#import kano_settings.keyboard_config as keyboard_config


import kano_settings.keyboard_layouts as keyboard_layouts
import kano_settings.keyboard_config as keyboard_config
import kano_settings.config_file as config_file

win = None  # TODO: Is it needed?
selected_country = None
selected_variant = "Generic"
variants_combo = None
country_combo = None
button = None


def activate(_win, box, apply_changes_button):
    global win, variants_combo, button, country_combo

    win = _win

    title = Gtk.Label("TITLE")
    title.modify_font(Pango.FontDescription("Bariol 16"))
    description = Gtk.Label("Description of project")
    description.modify_font(Pango.FontDescription("Bariol 14"))

    title_style = title.get_style_context()
    title_style.add_class('title')

    description_style = description.get_style_context()
    description_style.add_class('description')

    title_container = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing=0)
    title_container.add(title)
    title_container.set_size_request(200, 100)
    title_container.pack_start(description, True, True, 10)
    info_style = title_container.get_style_context()
    info_style.add_class('title_container')

    # Title
    title.set_text("Change your keyboard settings")

    # Description
    description.set_text("Which country do you live?")
    
    # Contains all the settings
    settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    settings_box.set_size_request(200, 250)
    box.add(settings_box)

    settings_box.pack_start(title_container, False, False, 0)

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

    # Create Variants Combo box
    variants_combo = Gtk.ComboBoxText.new()
    variants_combo.connect("changed", on_variants_changed)

    # Needs to contain dropdownlists and have a background image of a keyboard
    keyboard_image = Gtk.Image()
    keyboard_image.set_from_file("media/Graphics/Intro-illustration.png")

    dropdown_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    dropdown_box.pack_start(country_combo, False, False, 10)
    dropdown_box.pack_start(variants_combo, False, False, 10)
    dropdown_box.set_size_request(20, 20)

    settings_box.pack_start(dropdown_box, False, False, 30)

    box.pack_start(apply_changes_button, False, False, 0)

    # Refresh window
    win.show_all()

    # Set up in file in .kano-settings  
    try:
        country = int(config_file.read_from_file("Keyboard-country"))
        variant = int(config_file.read_from_file("Keyboard-variant"))
        country_combo.set_active(country)
        variants_combo.set_active(variant)

    except:
        print("Exception in keyboard activate")
        usa_index = countries.index("USA")
        country_combo.set_active(usa_index)
        variants_combo.set_active(0)

    variants_combo.get_child().modify_font(Pango.FontDescription("Bariol 13"))
    country_combo.get_child().modify_font(Pango.FontDescription("Bariol 13"))   

def apply_changes(button):
    global win, selected_country

    # print("Set the keyboard layout to %s, with variant" % selected_country, selected_variant)
    keyboard_config.set_keyboard(selected_country, selected_variant)
    button.hide()
    
    # Refresh window
    win.show_all()

    # Update .kano-settings with new current_country and current_variant   
    
    selected_country_index = country_combo.get_active()
    selected_variants_index = variants_combo.get_active()

    config_file.replace_setting("Keyboard-country", str(selected_country_index))
    config_file.replace_setting("Keyboard-variant", str(selected_variants_index))
    config_file.replace_setting("Keyboard-country-human", str(selected_country))
    config_file.replace_setting("Keyboard-variant-human", str(selected_variant))   


def on_country_changed(combo):
    global win, selected_country, variants_combo, button, country_combo

    tree_iter = combo.get_active_iter()
    if tree_iter is not None:
        model = combo.get_model()
        country = model[tree_iter][0]
    #button.show()
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
           
    #button.show()
    # Refresh window
    win.show_all()
