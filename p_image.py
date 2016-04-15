from PIL import Image
from math import *

#needed for creating the Gdk image file
import array

#also needed for creating the Gdk image file
from gi.repository import GdkPixbuf
from gi.repository import Gdk

class ImageClass():
    #this function initiate the class
    def __init__(self):
        self.uri = None
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
        #Load the image, records its uri, get its size, create thumbnail
        self.im.load()
        self.uri = uri
        w,h = self.im.size
        self.ratio = float(w/h)
        self.thumb = self.im
        self.thumb.thumbnail((450, int(450/self.ratio)))
        return True
    
    #this function "closes" the file that were open.
    #It just clears the im and thumb images.
    def close_file(self):
        self.im = None
        self.thumb = None
    #defines the function that get values from the cfg file
    def set_cfg(self, cfg):
        self.cfg = cfg
        
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
    
    #This function calculates the calibrating rectangle.
    #It's called each time the calibrate toggle button is set on.
    def calibrate(self):
        #sets the max angle increment (half of 16 bits)
        angle_increment = 2**15
        
        #sets the min and max values on both axes, in millimeters,
        #according to values given in support entry area.
        self.calibrate_width_min = - self.cfg.support_width/2
        self.calibrate_width_max = self.cfg.support_width/2
        self.calibrate_height_min = - self.cfg.support_height/2
        self.calibrate_height_max = self.cfg.support_height/2
        
        #Calculates the max possible size, according to distance given
        width_max = int(self.cfg.distance * tan(radians(self.cfg.h_angle/2)))
        height_max = int(self.cfg.distance * tan(radians(self.cfg.v_angle/2)))
        
        #Calculates the ratio between the size of the support and the max possible size
        ratio_width = self.calibrate_width_max/width_max
        ratio_height = self.calibrate_height_max/height_max
        
        #angle increment / width
        cmd_width = angle_increment / width_max
        cmd_height = angle_increment / height_max
        
        #transforms the self.calibrate_values into angle increments
        self.calibrate_width_min *= cmd_width * ratio_width
        self.calibrate_width_max *= cmd_width * ratio_width
        self.calibrate_height_min *= cmd_height * ratio_height
        self.calibrate_height_max *= cmd_height * ratio_height
        print (self.calibrate_height_max)
        
        
        
        
        
        
        
