        
from gi.repository import Gtk, Pango
import components.icons as icons

TOP_BAR_HEIGHT = 50
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 380

class Top_bar():

    def __init__(self):

        # This is to give the correct colour of the top bar as Event Boxes are the only containers that we can colour
        # This contains everything, but can't pack directly into as is only a simple container 
        self.background = Gtk.EventBox()
        self.background.set_size_request(WINDOW_WIDTH, TOP_BAR_HEIGHT)
        self.background.style = self.background.get_style_context()
        self.background.style.add_class('top_bar_container')

        # Container of all the elements
        self.container = Gtk.Box()
        self.container.set_homogeneous(False)

        # Main title of the window bar.
        self.header = Gtk.Label("Kano Settings")
        self.header.props.halign = Gtk.Align.CENTER
        self.header.modify_font(Pango.FontDescription("Bariol 13"))
        self.header.get_style_context().add_class("header")

        # Icons of the buttons
        self.prev_arrow = Gtk.Image()
        self.prev_arrow.set_from_pixbuf(icons.Icons(2).subpixel)
        self.next_arrow = Gtk.Image()
        self.next_arrow.set_from_pixbuf(icons.Icons(3).subpixel)
        self.cross = Gtk.Image()
        self.cross.set_from_pixbuf(icons.Icons(6).subpixel)

        # Prev Button
        self.prev_button = Gtk.Button()
        self.prev_button.set_image(self.prev_arrow)
        self.prev_button.set_size_request(TOP_BAR_HEIGHT, TOP_BAR_HEIGHT)
        self.prev_button.set_can_focus(False)

        # Next button
        self.next_button = Gtk.Button()
        self.next_button.set_image(self.next_arrow)
        self.next_button.set_size_request(TOP_BAR_HEIGHT, TOP_BAR_HEIGHT)
        self.next_button.set_can_focus(False)

        # Close button
        self.close_button = Gtk.Button()
        self.close_button.set_size_request(TOP_BAR_HEIGHT, TOP_BAR_HEIGHT)
        self.close_button.connect("clicked", Gtk.main_quit)
        self.close_button.set_can_focus(False)

        self.container.add(self.prev_button)
        self.container.pack_start(self.next_button, False, False, 0)
        self.container.pack_start(self.header, True, True, 0)
        self.container.pack_end(self.close_button, False, False, 0)
        self.background.add(self.container)