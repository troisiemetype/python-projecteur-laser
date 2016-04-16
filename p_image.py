from PIL import Image
from math import *

#needed for creating the Gdk image file
import array

#also needed for creating the Gdk image file
from gi.repository import GdkPixbuf
from gi.repository import Gdk

#needed for introducing pauses in the program
from time import sleep

class ImageObject():
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
        self.width,self.height = self.im.size
        self.ratio = float(self.width/self.height)
        self.thumb = self.im
        self.thumb.thumbnail((450, int(450/self.ratio)))
        self.pix_qty =  self.width * self.height
        self.pix_id = 0
        self.cur_row = 0
        self.cur_col = 0
        return True
    
    #this function "closes" the file that were open.
    #It simply clears all the attributes of self, except the cfg file
    def close_file(self):
        for item in self.__dict__:
            print(item)
            if item != 'cfg':
                item = None
                print('cleared')
            
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
        #calculate the max width and height (given by the projector max angle
        #and the distance to support)
        #h_angle & v_angle in degrees, length in mm
        #2 * distance * tan(angle balayage)
        max_width = int(2 * self.cfg.distance * tan(radians(self.cfg.h_angle)))
        max_height = int(2 * self.cfg.distance * tan(radians(self.cfg.v_angle)))
        
        #sets the max angle increment (half of 16 bits)
        angle_value_max = 2**15
        #sets the angle value
        #angle = atan(support width * tan(angle balayage)/max width)
        angle_width = atan((self.cfg.support_width *\
                                  tan(radians(self.cfg.h_angle)))/max_width)
        angle_height = atan((self.cfg.support_height *\
                                   tan(radians(self.cfg.v_angle)))/max_height)
        #calculate the angle ratio between the current value and the max value
        angle_ratio_width = degrees(angle_width) / self.cfg.v_angle
        angle_ratio_height = degrees(angle_height) / self.cfg.h_angle
        
        #calculate the final angle value, using the max value and the ratio
        angle_width_max = angle_value_max * angle_ratio_width
        angle_height_max = angle_value_max * angle_ratio_height
        
        self.send_calibration()
        
    #this prepares the coordinates for the calibration movement
    def send_calibration(self):
        i = 0
        while self.calibration == 1:
            print(i)
            i += 1
    
    #This computes a pixel of the picture, and append the value in a file
    #the GUI calls the function recursively till all pixels have benn computed
    def compute_image(self):
        
        if self.cur_col > self.width:
            self.cur_col = 0
            self.cur_row += 1
            
        if self.cur_row > self.height:
            self.cur_row = 0
        
        if self.pix_id > self.pix_qty:
            self.pix_id = 0
            return 1
        self.cur_col += 1
        self.pix_id += 1
        return self.pix_id / self.pix_qty
        