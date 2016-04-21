from PIL import Image, ImageChops
from math import *

#needed for creating the Gdk image file
import array

#also needed for creating the Gdk image file
from gi.repository import GdkPixbuf
from gi.repository import Gdk

#needed to update the pprogress bar during computation
from gi.repository import Gtk

#needed for introducing pauses in the program
from time import sleep, time

class ImageObject:
    #This three are links to other class used by the main program.
    #These are class attributes.
    #That way when lcosing a file, attributes are cleared but those stays
    ser = None
    cfg = None
    jsp = None
    wm = None
    #this function initiate the class
    def __init__(self):
        self.uri = None
        self.im = None
        self.thumb = None
        self.compute_flag = None
        
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
        self.width, self.height = self.im.size
        self.ratio = float(self.width/self.height)
        self.thumb = self.im.copy()
        self.thumb.thumbnail((450, int(450/self.ratio)))
        
        #Compute black and white and inverted image
        self.im = self.im.convert('L')
        self.im_invert = ImageChops.invert(self.im)
        
        #Init the values used in the calc 'loops'.
        self.pix_qty =  self.width * self.height
        self.pix_id = 0
        self.cur_row = 0
        self.cur_col = 0
        self.debut = 0
        self.fin = 0
        self.mode = 1
        
        #Init/update the values from the settings
        self.half_width = self.width / 2
        self.half_height = self.height / 2
        self.tan_h_scan = tan(radians(ImageObject.cfg.h_angle))
        self.tan_v_scan = tan(radians(ImageObject.cfg.v_angle))
        #sets the max angle increment (half of 16 bits)
        self.angle_value_max = 2**15
        
        
        #Init the flags and buffers.
        self.inverted_flag = 0
        self.compute_flag = 0
        self.computed_flag = 0
        self.line_change_flag = 0
        self.data_buffer = []
        self.calibration_buffer = []
        
        #Display the status informations.
        self.name = self.uri.split('/')
        self.name = self.name.pop()
        ImageObject.wm.status('%s, %sx%s pixels'%(self.name,self.width, self.height),
                              'file')
        return True
    
    #this function "closes" the file that was open.
    #It simply clears all the instance attributes.
    def close_file(self):
        ImageObject.wm.status("Pas d'image chargée", 'file')
        for item in self.__dict__:
            self.__setattr__(item, None)
            
    #this function converts PIL images to Pixbuf format for displaying in Gtk
    def get_pixbuf(self):
        #transforms the given image into an array of pixels
        arr = array.array('B', self.thumb.tobytes())
        w,h = self.thumb.size
        #look for an alpha mask
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
    #This function updates the values  
    #this function calculates the max size, according to the distance of the support
    def update_max_size(self):
        #h_angle & v_angle in degrees, length in mm
        #2 * distance * tan(angle balayage)
        self.max_width = int(2 * ImageObject.cfg.distance * self.tan_h_scan)
        self.max_height = int(2 * ImageObject.cfg.distance * self.tan_v_scan)
        return self.max_width, self.max_height
    
    #This function transformates the size in pixels into millimeters
    def update_ratio_pix_to_mm(self):
        #depending of the orientation of the picture, we take the biggest size to minimize rouding errors.
        if self.ratio > 1:
            self.ratio_pix_mm = ImageObject.cfg.width / self.width
        else:
            self.ratio_pix_mm = ImageObject.cfg.height / self.height
    
    #This function get the angle value from the millimeters value
    #the pos argument is the position, in mm, from center.
    #So it can hold negative values. In fact it does, half the time.
    #the angle returned is in radians
    def get_angle_value(self, pos, axe):
        #sets the angle value
        #angle = atan(support width * tan(angle balayage))/max width  
        if axe == 'x':
            return atan(pos * self.tan_h_scan / self.half_width)
        if axe == 'y':
            return atan(pos * self.tan_v_scan / self.half_height)
                 
    #This function calculates the position to send to the projector, given the angle
    def get_serial_pos(self, angle, axe):
                
        #calculates the angle ratio between the current value and the max value
        if axe == 'x':
            angle_ratio = degrees(angle) / ImageObject.cfg.h_angle
        elif axe == 'y':
            angle_ratio = degrees(angle) / ImageObject.cfg.v_angle
        #then calculates the final angle value, using the max value and the ratio
        return int(self.angle_value_max * angle_ratio)

    
    def get_laser_pos(self, value):
        #sets the max value (16 bits)
        value_max = 2**16
        
        return int(value_max * value / 256)
    
    #This function calculates the calibrating rectangle.
    #It's called on the calibration button toggle.
    #TODO: add a cfg parameter for the laser intensity during calibrating
    #TODO: modify the call to jsonparser, to send a dictionnary instead of several values.
    def calibrate(self):
        #get max size
        self.update_max_size()
        #get angle for this position
        angle_width, angle_height = self.get_angle_value((ImageObject.cfg.support_width/2,
                                                    ImageObject.cfg.support_height/2))
        x_pos, y_pos = self.get_serial_pos((angle_width, angle_height))
        
        l_pos = 25000
        self.calibration_buffer = []
        corner = self.jsp.to_json(0, -x_pos, y_pos, 0, 0, 0)
        self.calibration_buffer.append(corner)
        corner = self.jsp.to_json(1, -x_pos, y_pos, l_pos, 0, 0)
        self.calibration_buffer.append(corner)
        corner = self.jsp.to_json(2, x_pos, y_pos, l_pos, 0, 0)
        self.calibration_buffer.append(corner)
        corner = self.jsp.to_json(3, x_pos, -y_pos, l_pos, 0, 0)
        self.calibration_buffer.append(corner)
        corner = self.jsp.to_json(4, -x_pos, -y_pos, l_pos, 0, 0)
        self.calibration_buffer.append(corner)
        corner = self.jsp.to_json(5, -x_pos, -y_pos, 0, 0, 0)
        self.calibration_buffer.append(corner)
            
    #This computes a pixel of the picture, and append the value in a file
    #the main loop calls this on each iteration if the im.compute_flag is set
    def compute_image(self):
        #test the flag state before anything, return if 0
        if self.compute_flag != 1:
            return 0
        #Test if it has already been computed since last settings change
        if self.computed_flag == 1:
            self.compute_flag = 0
            return
        #if first iteration since flag was set, initialise some datas
        if self.pix_id == 0:
            self.update_max_size()
            self.update_ratio_pix_to_mm()
            self.ser.pause_flag = 1
            self.debut = time()
            self.pv_pix = (None, None, None)
            ImageObject.wm.progress_compute.show()
            ImageObject.wm.status('Calcul en cours...')
            
        #Let the compute image run a few times before to enable serial sending.
        if self.pix_id == 5:
            self.ser.pause_flag = 0
            
        #get j and i (row index, col index) from the current pix id
        j = floor(self.pix_id / self.width)
        i = self.pix_id % self.width
        
        #detect and of a line, to manage the line change
        if i == self.width - 1:
            line_change_flag = 1
        
        #get the value of the current pixel
        #uses the inverted image, or if inverted_flag set, the originale one.
        if self.inverted_flag == 1:
            pix_value = self.im.getpixel((i,j))
        else:
            pix_value = self.im_invert.getpixel((i,j))
        
        #Init the dictionnary with the move ID
        data_to_send ={'ID': self.pix_id}
        
        if pix_value != self.pv_pix[2]:
            #transform the pixel value into projecteur value
            laser_pos = self.get_laser_pos(pix_value)
            #Add to the dictionnary ofvalues to send.
            data_to_send.update({'L': laser_pos})
        
        #Tests the current i value against the previous one
        #calcul is as follow:
        #i = position
        #L/2 = Width, or height
        #ratio = ratio_pix_mm
        #scan: scan angle max
        #angle_value_max = the value for the projector that give the max angle
        #calculates position from px to mm
        #pos = (i - L/2) * ratio
        #Transform this position into angle
        #angle = atan(pos * tan(scan) / (L/2)))
        #Transform this angle into projector value
        #pos = int(angle_value_max * angle / scan)
        #It factors as follow:
        #pos = angle_value_max * atan(ratio * tan(scan)*((i / L/2) - 1)) / scan
        if i != self.pv_pix[0]:
            pos = self.angle_value_max *\
                degrees(atan(self.ratio_pix_mm * self.tan_h_scan * ((i / self.half_width)-1))) /\
                ImageObject.cfg.h_angle
            data_to_send.update({'X':pos})
        
        #same for j
        if j != self.pv_pix[1]:
            pos = self.angle_value_max *\
               degrees(atan(self.ratio_pix_mm * self.tan_v_scan * ((j / self.half_width)-1))) /\
               ImageObject.cfg.v_angle
            data_to_send.update({'Y':pos})

        #Call the json_creator and add the line to buffer.
        #If line_change_flag is set, create a json string for this position, laser cut, mode 0.
        if i == 0:
            data = data_to_send.copy()
            data.pop('L', None)
            data.update({'L':0})
            json_string = self.jsp.to_json(data)
            self.data_buffer.append(json_string)
            data_to_send.update({'speed':ImageObject.cfg.speed,'mode':self.mode})
            
        # Current position. 
        json_string = self.jsp.to_json(data_to_send)
        self.data_buffer.append(json_string)
       
        # If end of line, first shut the laser out.
        if i == self.width - 1:
            data = {'ID':self.pix_id, 'L':0, 'mode':0}
            json_string = self.jsp.to_json(data)
            self.data_buffer.append(json_string)
    
        #records the pix position for next increment
        self.pv_pix = (i, j, pix_value)
        
        #increment the pixel id
        self.pix_id += 1
        
        #updates progressbar
        ImageObject.wm.progress_compute.set_text('calcul pixel %s/%s'%(self.pix_id,self.pix_qty))
        ImageObject.wm.progress_compute.set_fraction(self.pix_id/self.pix_qty)
        
        #if pix_id is greater than pix_qty, the whole image have been parsed.
        #set pix_id and compute_flag to 0, hide progress bar
        if self.pix_id >= self.pix_qty:
            self.fin = time()
            duree = self.fin - self.debut
            self.pix_id = 0
            self.compute_flag = 0
            self.computed_flag = 1
            ImageObject.wm.status('Image calculée en %.3fs.'%duree)            
            ImageObject.wm.progress_compute.hide()
        return 1