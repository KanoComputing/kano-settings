
from gi.repository import Gtk, GdkPixbuf
import os

from kano.paths import common_images_dir


def tick_icon():
    '''This should return a tick image.  We use this to show which
    WiFi network is already selected
    '''

    width = 24
    height = 24

    icons_path = os.path.join(common_images_dir, 'icons.png')

    tick_pixbuf = GdkPixbuf.Pixbuf.new_from_file(icons_path)

    tick_pixbuf = tick_pixbuf.new_subpixbuf(5 * 24, 0, width, height)
    tick_image = Gtk.Image()
    tick_image.set_from_pixbuf(tick_pixbuf)

    return tick_image
