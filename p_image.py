from PIL import Image

#needed for creating the Gdk image file
import array

#also needed for creating the Gdk image file
from gi.repository import GdkPixbuf
from gi.repository import Gdk

class ImageClass():
    #this function initiate the class
    def __init__(self):
        self.im = None
        self.thumb = None
        
    #This function deals with openning a new file
    #it tries to open the file that URI points on, gives false if it can't
    #Then computes the thumbnail so that it can be used when needed
    def open_file(self, uri):
        #try to open the file, else give an Error message
        try:
            self.im = Image.open(uri)
        except IOError:
            return False
        #display status
        #wm.status('open %s' %uri)
        #Load the image, get its size, create thumbnail
        self.im.load()
        w,h = self.im.size
        self.thumb = self.im
        self.thumb.thumbnail((450, int(450*h/w)))
        return True
    
    #this function "closes" the file that were open.
    #It just clears the im and thumb images.
    def close_file(self):
        self.im = None
        self.thumb = None
    
    #this function converts PIL images to Pixbuf format for displaying in Gtk
    def get_pixbuf(self):
        #transforms the given image into an array of pixels
        arr = array.array('B', self.im.tobytes())
        w,h = self.im.size
        #look at a an alpha mask
        if self.im.mode == 'RGBA':
            hasAlpha = True
            dist = w*4
        else:
            hasAlpha = False
            dist = w*3
        #returns the pix buf. Args:
        #array, colorspace, has alpha, bits per sample,
        #width, height, distance in bytes between row starts
        return GdkPixbuf.Pixbuf.new_from_data(arr, GdkPixbuf.Colorspace.RGB,
                                              hasAlpha, 8, w, h, dist)
