
from gi.repository import GdkPixbuf
import kano_settings.constants as constants

# To make an image using the pixbuf icon, use the command below:
# image.set_from_pixbuf(self.pixbuf)
        
class Icons():

    def __init__(self, icon_number):
        # Create main window
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(constants.files + "media/Icons/systemsetup-icons.png", 192, 24)
        self.subpixel = self.pixbuf.new_subpixbuf(24*icon_number, 0, 24, 24).add_alpha(True, 255, 255, 255)