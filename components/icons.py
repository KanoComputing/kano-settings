
from gi.repository import GdkPixbuf


class Icons():

    def __init__(self, icon_number):
        # Create main window
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size("/usr/lib/python3/dist-packages/kano_settings/media/Icons/systemsetup-icons.png", 192, 24)
        #self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size("media/Icons/systemsetup-icons.png", 192, 24)
        self.subpixel = self.pixbuf.new_subpixbuf(24*icon_number, 0, 24, 24).add_alpha(True, 255, 255, 255)
        # To make an image using the pixbuf icon, use the command below:
        # image.set_from_pixbuf(self.pixbuf)