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
import kano_settings.constants as constants
from .config_file import get_setting, set_setting
from kano.gtk3.buttons import OrangeButton
from kano_profile.apps import load_app_state_variable


win = None
button = None
box = None

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

kano_keyboard = True
IMG_HEIGHT = 100


class WorkerThread(threading.Thread):
    def __init__(self, callback):
        threading.Thread.__init__(self)
        self.callback = callback

    def run(self):
        # Apply the keyboard changes
        keyboard_config.set_keyboard(selected_country, selected_variant)

        # The callback runs a GUI task, so wrap it!
        GObject.idle_add(self.callback)


def activate(_win, _box, _button):
    global win, button, kano_keyboard

    win = _win
    box = _box
    button = _button

    read_config()

    # Check for kano-keyboard
    if kano_keyboard:
        kano_keyboard_ui(box, button)
    else:
        other_keyboard_ui(box, button)


def kano_keyboard_ui(box, button):

    # Settings container
    settings = fixed_size_box.Fixed()

    # Make sure continue button is enabled
    button.set_sensitive(True)
    if load_app_state_variable('kano-settings', 'completed') == 1:
        button.set_label("BACK")

    # Title
    title = Heading("Keyboard", "Kano keyboard detected!")

    # height is 106px
    img = Gtk.Image()
    img.set_from_file(constants.media + "/Graphics/keyboard.png")

    # Link to advance options
    to_advance_button = OrangeButton("Layout options")
    to_advance_button.connect("button_press_event", to_advance, box, button)

    container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    container.pack_start(img, False, False, 10)
    container.pack_start(to_advance_button, False, False, 10)

    valign = Gtk.Alignment(xalign=0.5, yalign=0, xscale=0, yscale=0)
    valign.add(container)
    settings.box.pack_start(valign, False, False, 0)

    box.pack_start(title.container, False, False, 0)
    box.pack_start(settings.box, False, False, 0)
    box.pack_start(button.align, False, False, 0)

    # Refresh window
    win.show_all()


def other_keyboard_ui(box, button):
    global continents_combo, variants_combo, countries_combo

    # change text on button
    button.set_label("APPLY CHANGES")

    # Contains all the settings
    settings = fixed_size_box.Fixed()

    # Make sure continue button is enabled
    button.set_sensitive(False)

    # Title
    title = Heading("Keyboard", "Where do you live? So I can set your keyboard")

    # Create Continents Combo box
    continents_combo = Gtk.ComboBoxText.new()
    for c in continents:
        continents_combo.append_text(c)
    continents_combo.connect("changed", on_continent_changed)

    # Create Countries Combo box
    countries_combo = Gtk.ComboBoxText.new()
    countries_combo.connect("changed", on_country_changed)
    countries_combo.props.valign = Gtk.Align.CENTER

    # Create Advance mode checkbox
    advance_button = Gtk.CheckButton("Advanced options")
    advance_button.set_can_focus(False)
    advance_button.props.valign = Gtk.Align.CENTER
    advance_button.connect("clicked", on_advance_mode)
    advance_button.set_active(False)

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
    dropdown_box_countries.pack_start(continents_combo, False, False, 0)
    dropdown_box_countries.pack_start(countries_combo, False, False, 0)
    dropdown_box_keys.pack_start(advance_button, False, False, 0)
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
    box.pack_start(button.align, False, False, 0)

    # show all elements except the advanced mode
    refresh_window()


def refresh_window():
    global win, variants_combo
    win.show_all()
    variants_combo.hide()


def apply_changes(button):
    global win, variants_combo

    if not kano_keyboard:
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


def set_variants_to_generic():
    global variants_combo
    variants_combo.set_active(0)


def on_continent_changed(combo):
    global selected_continent_hr, selected_continent_index, button

    continent = selected_continent_hr
    tree_iter = combo.get_active_iter()

    if tree_iter is not None:
        model = combo.get_model()
        continent = model[tree_iter][0]

    selected_continent_hr = str(continent)
    selected_continent_index = str(combo.get_active())

    button.set_sensitive(False)

    fill_countries_combo(selected_continent_hr)


def on_country_changed(combo):
    global win, selected_country, selected_country_index, selected_country_hr, selected_layout, variants_combo, button

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

    set_variants_to_generic()


def on_variants_changed(combo):
    global win, selected_variant, selected_variant_hr, selected_variant_index, button

    tree_iter = combo.get_active_iter()
    if tree_iter is not None:
        model = combo.get_model()
        variant = model[tree_iter][0]
        button.set_sensitive(True)
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


def on_advance_mode(button):
    if int(button.get_active()):
        variants_combo.show()
    else:
        variants_combo.hide()


def to_advance(arg1=None, arg2=None, box=None, button=None):

    # Remove children
    for i in box.get_children():
        box.remove(i)

    other_keyboard_ui(box, button)


def work_finished_cb():
    # Finished updating keyboard
    pass


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
