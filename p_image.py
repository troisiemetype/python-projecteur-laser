from PIL import Image
from math import *
from statistics import mean

#needed for creating the Gdk image file
import array

#also needed for creating the Gdk image file
from gi.repository import GdkPixbuf
from gi.repository import Gdk

#needed to update the pprogress bar during computation
from gi.repository import Gtk

#needed for introducing pauses in the program
from time import sleep, time

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
        self.thumb = self.im.copy()
        self.thumb.thumbnail((450, int(450/self.ratio)))
        self.pix_qty =  self.width * self.height
        self.pix_id = 0
        self.cur_row = 0
        self.cur_col = 0
        self.compute_flag = 0
        self.calibration_flag = 0
        self.data_buffer = []
        self.calibration_buffer = []
        print(self.pix_qty)
        return True
    
    #this function "closes" the file that were open.
    #It simply clears all the attributes of self, except the cfg file
    def close_file(self):
        for item in self.__dict__:
            if item != 'cfg' and item != 'wm':
                item = None
            
    #defines the function that get values from the cfg file
    def set_cfg(self, cfg):
        self.cfg = cfg
        
    #this function converts PIL images to Pixbuf format for displaying in Gtk
    def get_pixbuf(self):
        #transforms the given image into an array of pixels
        arr = array.array('B', self.thumb.tobytes())
        w,h = self.thumb.size
        #look at a an alpha mask
        if self.thumb.mode == 'RGBA':
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
    
    #this functions calculates the max size, according to the distance of the support
    def update_max_size(self):
        #h_angle & v_angle in degrees, length in mm
        #2 * distance * tan(angle balayage)
        self.max_width = int(2 * self.cfg.distance * tan(radians(self.cfg.h_angle)))
        self.max_height = int(2 * self.cfg.distance * tan(radians(self.cfg.v_angle)))
        print(self.max_height, self.max_width)
        return self.max_width, self.max_height
    
    #This function transformates the size in pixels into millimeters
    def update_ratio_pix_to_mm(self):
        if self.ratio > 1:
            self.ratio_pix_mm = self.cfg.width / self.width
        else:
            self.ratio_pix_mm = self.cfg.height / self.height
        print(self.ratio_pix_mm)
    
    #This functions get the angle value from the millimeters value
    #the pos argument is the position, in mm, from center.
    #So it can hold negative values. In fact it does, half the time.
    #the angle returned is in radians
    def get_angle_value(self, pos):
        x_pos = pos[0]
        y_pos = pos[1]
        
        #sets the angle value
        #angle = atan(support width * tan(angle balayage)/max width)        
        x_angle = atan((x_pos * tan(radians(self.cfg.h_angle))) / (self.max_width / 2))
        y_angle = atan((y_pos * tan(radians(self.cfg.v_angle))) / (self.max_height / 2))
        
        print(degrees(x_angle), degrees(y_angle))
        
        return x_angle, y_angle
    
    #This function calculates the position to send to the projector, given the angle
    def get_serial_pos(self, angle):
        angle_width = angle[0]
        angle_height = angle[1]
        
        #sets the max angle increment (half of 16 bits)
        angle_value_max = 2**15
        
        #calculate the angle ratio between the current value and the max value
        angle_ratio_width = degrees(angle_width) / self.cfg.v_angle
        angle_ratio_height = degrees(angle_height) / self.cfg.h_angle
    
        #calculate the final angle value, using the max value and the ratio
        x_angle = angle_value_max * angle_ratio_width
        y_angle = angle_value_max * angle_ratio_height
        
        print(x_angle, y_angle)
        
        return x_angle, y_angle
    
    def get_laser_pos(self, value):
        #sets the max value (16 bits)
        value_max = 2**16
        
        return int(value_max - 256*(value + 1))
    
    #This function calculates tax_size = he calibrating rectangle.
    #It's called each time the calibrate toggle button is set on.
    def calibrate(self):
        #get max size
        self.update_max_size()
        #get angle for this position
        angle_width, angle_height = self.get_angle_value((self.cfg.support_width/2,
                                                    self.cfg.support_height/2))
        self.get_serial_pos((angle_width, angle_height))
        
        self.i = 0
        
    #this prepares the coordinates for the calibration movement
    def send_calibration(self):
        Gtk.main_iteration_do(False)
        print(self.i)
        self.i += 1
    
    #This computes a pixel of the picture, and append the value in a file
    #the main loop calls this on each iteration if the im.compute_flag is set
    def compute_image(self, progressbar):
        #get j and i (row index, col index) from the current pix id
        j = floor(self.pix_id / self.width)
        i = self.pix_id % self.width
        
        #get the value of the current pixel
        pix_value = mean(self.im.getpixel((i,j)))
        
        #transform the pixel value int oprojecteur value
        laser_pos = self.get_laser_pos(pix_value)
        
        #calculates position in mm
        x_pos = (i - self.width/2) * self.ratio_pix_mm
        y_pos = (j - self.height/2) * self.ratio_pix_mm
        
        #Transform this position into angle
        x_pos, y_pos = self.get_angle_value((x_pos, y_pos))
        
        #Transform this angle into projector value
        x_pos, y_pos = self.get_serial_pos((x_pos, y_pos))

        #increment the pixel id
        self.pix_id += 1
        
        #updates progressbar
        progressbar.set_fraction(self.pix_id/self.pix_qty)
        
        #if pix_id is greater than pix_qty, the whole image have been parsed.
        #set pix_id and compute_flag to 0, hide progress bar
        if self.pix_id >= self.pix_qty:
            self.pix_id = 0
            self.compute_flag = 0
            progressbar.hide()

