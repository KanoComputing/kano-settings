
from gi.repository import Gtk, Pango

class Heading():
    def __init__(self, title, description):

        self.title = Gtk.Label(title)
        self.title.modify_font(Pango.FontDescription("Bariol 16"))
        self.description = Gtk.Label(description)
        self.description.modify_font(Pango.FontDescription("Bariol 14"))

        self.title_style = self.title.get_style_context()
        self.title_style.add_class('title')

        self.description_style = self.description.get_style_context()
        self.description_style.add_class('description')

        # Table
        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.container.set_size_request(300, 150)
        self.container.pack_start(self.title, False, False, 0)
        self.container.pack_start(self.description, False, False, 10)