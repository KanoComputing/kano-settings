
from gi.repository import Gtk, Pango    
import kano_settings.constants as constants   

class Menu_button():

    def __init__(self, name, description=""):

        # Contains the info about the level and the image
        self.container = Gtk.Table(2, 2, False)
        self.container.set_size_request(90,20)

        # Info about the different settings
        self.title = Gtk.Label(name)
        self.title.get_style_context().add_class("intro_label")

        #info = config_file.read_from_file(custom_info[x])

        # Replace some of the info displayed with whitespace so it fits
        if description != None:
            if len(description) >= 12:
                description = description[0:12] + '...'

        self.description = Gtk.Label(description)
        self.description.modify_font(Pango.FontDescription("Bariol 13"))
        self.description.get_style_context().add_class("custom_label")
        
        self.button = Gtk.Button()
        self.button.set_can_focus(False)
        self.img = Gtk.Image()
        self.img.set_from_file(constants.files + "media/Icons/Icon-" + name + ".png")

        self.container.attach(self.title, 1, 2, 0, 1)
        self.container.attach(self.description, 1, 2, 1, 2)
        self.container.attach(self.img, 0, 1, 0, 2)

        self.button.add(self.container)
        self.button.set_size_request(200, 100)