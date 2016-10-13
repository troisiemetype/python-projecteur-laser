from PIL import Image, ImageChops
from math import *

# needed for creating the Gdk image file
import array

# also needed for creating the Gdk image file
import gi
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf

# needed for introducing pauses in the program
from time import sleep, time


class ImageObject:
    """Hold the image. Open it, close it, calculate coordinates."""
    # This three are links to other class used by the main program.
    # These are class attributes.
    # That way when lcosing a file, attributes are cleared but those stays
    ser = None
    cfg = None
    jsp = None
    wm = None

    def __init__(self):
        """Initialise class. Set used values to None"""
        self.uri = None
        self.im = None
        self.thumb = None
        self.compute_flag = None

    # This function deals with opening a new file
    # it tries to open the file that URI points on, gives false if it can't
    # Then computes the thumbnail so that it can be used when needed
    def open_file(self, uri):
        """Open a file.
        Verify the format.
        Get size, create thumbnail.
        Calculate black and white and inverted.
        Set values used for computing, flags and buffers.
        Print information to GUI.
        """
        # try to open the file, else give an Error message
        try:
            self.im = Image.open(uri)
        except IOError:
            return False
        # Load the image, records its uri, get its size, create thumbnail
        self.im.load()
        self.uri = uri
        self.width, self.height = self.im.size
        self.ratio = float(self.width / self.height)
        self.thumb = self.im.copy()
        self.thumb.thumbnail((450, int(450 / self.ratio)))

        # Compute black and white and inverted image
        self.im = self.im.convert('L')
        self.im_invert = ImageChops.invert(self.im)
        # Create byte array from this images.
        self.im_bytes = array.array('B', self.im.tobytes())
        self.im_invert_bytes = array.array('B', self.im_invert.tobytes())

        # Init the values used in the calc 'loops'.
        self.pix_qty = self.width * self.height
        self.pix_id = 0
        self.cur_row = 0
        self.cur_col = 0
        self.debut = 0
        self.fin = 0
        self.speed = 0
        self.mode = 1

        # Init/update the values from the settings
        self.half_width = self.width / 2
        self.half_height = self.height / 2
        self.tan_h_scan = tan(ImageObject.cfg.h_angle_rad)
        self.tan_v_scan = tan(ImageObject.cfg.v_angle_rad)
        # sets the max angle increment (half of 16 bits)
        self.angle_value_max = 2**15

        # Init the flags and buffers.
        self.inverted_flag = 0
        self.compute_flag = 0
        self.computed_flag = 0
        self.line_change_flag = 0
        self.data_buffer = []
        self.calibration_buffer = []

        # Display the status information.
        self.name = self.uri.split('/')
        self.name = self.name.pop()
        ImageObject.wm.status('%s, %sx%s pixels' % (self.name, self.width,
                               self.height), 'file')
        return True

    # this function "closes" the file that was open.
    # It simply clears all the instance attributes.
    def close_file(self):
        """Close the file. Print info to GUI, clear instance attributes."""
        ImageObject.wm.status("Pas d'image chargée", 'file')
        for item in self.__dict__:
            self.__setattr__(item, None)

    # this function converts PIL images to Pixbuf format for displaying in Gtk
    def get_pixbuf(self):
        """Compute pixbuf for GUI display. Convert the thumbnail to byte array,
        look if it has a alpha layer, create a Gdkixbuf object.
        """
        # transforms the given image into an array of pixels
        arr = array.array('B', self.thumb.tobytes())
        w, h = self.thumb.size
        # look for an alpha mask
        if self.thumb.mode == 'RGBA':
            hasAlpha = True
            dist = w * 4
        else:
            hasAlpha = False
            dist = w * 3
        # returns the pix buf. Args:
        # array, colorspace, has alpha, bits per sample,
        # width, height, distance in bytes between row starts
        return GdkPixbuf.Pixbuf.new_from_data(arr, GdkPixbuf.Colorspace.RGB,
                                              hasAlpha, 8, w, h, dist)

    # this function calculates the max size, according to the distance of the support
    def update_max_size(self):
        """Update the max size values according to the distance value
        and angle set in config file."""
        # 2 * distance * tan(angle scan)
        self.max_width = int(2 * ImageObject.cfg.distance * self.tan_h_scan)
        self.max_height = int(2 * ImageObject.cfg.distance * self.tan_v_scan)
        self.half_max_width = self.max_width / 2
        self.half_max_height = self.max_height / 2
        return self.max_width, self.max_height
    
    def update_ratio_pix_to_mm(self):
        """Update the ratio from pix to mm.
        This is the ratio that links size in px to size in mm.
        Like a resolution coef.
        """
        # depending of the orientation of the picture,
        # we take the biggest size to minimize rounding errors.
        if self.ratio > 1:
            self.ratio_pix_mm = ImageObject.cfg.width / self.width
        else:
            self.ratio_pix_mm = ImageObject.cfg.height / self.height
    
    def get_angle_value(self, pos, axe):
        """Compute the angle from a mm value.
        The pos argument is the position, in millimeters, from image center.
        So it can be negative if the pos is left or above from center."""
        # sets the angle value
        # angle = atan(support width * tan(scan angle))/max width
        # or:
        # angle = atan2(support width * tan(scan angle), max width)
        if axe == 'x':
            return atan2(pos * self.tan_h_scan, self.half_max_width)
        if axe == 'y':
            return atan2(pos * self.tan_v_scan, self.half_max_height)
                 
    def get_serial_pos(self, angle, axe):
        """Compute the projector position from an angle."""
                
        # calculates the angle ratio between the current value and the max value
        if axe == 'x':
            angle_ratio = angle / ImageObject.cfg.h_angle_rad
        elif axe == 'y':
            angle_ratio = angle / ImageObject.cfg.v_angle_rad
        # then calculates the final angle value, using the max value and the ratio
        return floor(self.angle_value_max * angle_ratio)

    def get_speed(self):
        """Compute the angle increment corresponding to the wanted speed."""
        pass
    
    def get_laser_pos(self, value):
        """Compute the laser pos according to pix value."""
        # sets the max value (16 bits)
        value_max = 2**16
        
        return int(value_max * value / 256)
    
    # This function calculates the calibrating rectangle.
    # It's called on the calibration button toggle.
    # TODO: add a cfg parameter for the laser intensity during calibrating
    def calibrate(self):
        """Populate the calibration buffer.
        Compute angle, then projector pos, from support size.
        """
        # get max size
        self.update_max_size()
        # get angle for this position
        angle_width = self.get_angle_value(ImageObject.cfg.support_width/2, 'x')
        angle_height = self.get_angle_value(ImageObject.cfg.support_height/2, 'y')
        x_pos = self.get_serial_pos(angle_width, 'x')
        y_pos = self.get_serial_pos(angle_height, 'y')
        
        l_pos = 25000
        self.calibration_buffer = []

        # First corner.
        corner = 'I%sX%sY%sL%sM%s'%(0, -x_pos, y_pos, 0, 0)
        self.calibration_buffer.append(corner)
        
        # Same place, light the laser
        corner = 'I%sX%sY%sL%s' % (1, -x_pos, y_pos, l_pos)
        self.calibration_buffer.append(corner)
        
        # Second corner.
        corner = 'I%sX%sY%sL%s' % (2, x_pos, y_pos, l_pos)
        self.calibration_buffer.append(corner)
        
        #Third Corner.
        corner = 'I%sX%sY%sL%s' % (3, x_pos, -y_pos, l_pos)
        self.calibration_buffer.append(corner)
        
        # Fourth corner.
        corner = 'I%sX%sY%sL%s' % (4, -x_pos, -y_pos, l_pos)
        self.calibration_buffer.append(corner)
        
        # Shut the laser up.
        corner = 'I%sL%s' %(5, 0)
        self.calibration_buffer.append(corner)

    # This computes a pixel of the picture, and append the value in a file
    # the main loop calls this on each iteration if the im.compute_flag is set.
    def compute_image(self):
        """Create and populate the data buffer for the image.
        Test flags.
        Init the function, show progress bar, write state to GUI.
        Compute laser, X and Y if different from previous value.
        Handle end of line and new line (laser stop, line change, laser on).
        When image processed, set back state for next compute.
        """
        # test the flag state before anything, return if 0
        if self.compute_flag != 1:
            return 0
        # Test if it has already been computed since last settings change
        if self.computed_flag == 1:
            self.compute_flag = 0
            return
        # if first iteration since flag was set, initialise some data.
        if self.pix_id == 0:
            # get updated values for the picture.
            self.update_max_size()
            self.update_ratio_pix_to_mm()
            angle_speed = self.get_angle_value(ImageObject.cfg.speed / 2,"x")
            self.speed = self.get_serial_pos(angle_speed, 'x')
            # pause sending to let the data_buffer be populated enough.
            self.ser.pause_flag = 1
            # Get the current ime to final compute time.
            self.debut = time()
            # Create a reminder of the previous pix value.
            self.pv_pix = [None, None, None]
            # Set GUI.
            ImageObject.wm.progress_compute.show()
            ImageObject.wm.status('Calcul en cours...')

        # Let compute() run a few times
        # before to enable serial sending.
        if self.pix_id == 50:
            self.ser.pause_flag = 0

        # get j and i (row index, col index) from the current pix id
        j = floor(self.pix_id / self.width)
        i = self.pix_id % self.width

        # get the value of the current pixel
        # uses the inverted image, or if inverted_flag set, the original one.
        if self.inverted_flag == 1:
            pix_value = self.im_bytes[self.pix_id]
        else:
            pix_value = self.im_invert_bytes[self.pix_id]

        # Init the dictionary with the move ID
        data_to_send = 'I%s'%self.pix_id

        if pix_value != self.pv_pix[2]:
            self.pv_pix[2] = pix_value
            # transform the pixel value into projector value
            laser_pos = floor(self.get_laser_pos(pix_value))
            # Add to the dictionary of values to send.
            data_to_send += 'L%s'%pix_value

        # Tests the current i value against the previous one
        # calculation is as follow:
        # i = position
        # L/2 = Width, or height
        # ratio = ratio_pix_mm
        # scan: scan angle max
        # angle_value_max = the value for the projector that give the max angle
        # calculates position from px to mm
        # pos = (i - L/2) * ratio
        # Transform this position into angle
        # angle = atan(pos * tan(scan) / (L/2)))
        # Transform this angle into projector value
        # pos = int(angle_value_max * angle / scan)
        if i != self.pv_pix[0]:
            self.pv_pix[0] = i
            pos = (i - self.half_width) * self.ratio_pix_mm
            alpha = self.get_angle_value(pos, 'x')
            x_pos = self.get_serial_pos(alpha, 'x')
            x_pos += 2**15
            data_to_send += 'X%s'%x_pos

            # Update speed for this position
            #speed = floor(self.speed * (1 + (pos / 2**15)))
            speed = floor(ImageObject.cfg.speed)
            #print(x_pos, speed)

            data_to_send += 'S%s'%speed
            # print(speed)

        # same for j
        if j != self.pv_pix[1]:
            self.pv_pix[1] = j
            pos = (j - self.half_height) * self.ratio_pix_mm
            alpha = self.get_angle_value(pos, 'y')
            y_pos = self.get_serial_pos(alpha, 'y')
            y_pos += 2**15
            data_to_send += 'Y%s'%y_pos

        # If line_change_flag is set, create a data string for this position, laser cut, mode 0.
        if i == 0:
            data_to_send_0 = 'I%s' % self.pix_id
            data_to_send_0 += 'L%s'%0
            data_to_send_0 += 'X%sY%s'%(x_pos, y_pos)
            data_to_send_0 += 'M%s'%0
            data_to_send_0 += '\n'
            self.data_buffer.append(data_to_send_0)
            
            # updates progressbar
            percent = int((self.pix_id / self.pix_qty) * 100)
            ImageObject.wm.progress_compute.set_text('calcul image: %s%%'
                                                     %(percent))
            ImageObject.wm.progress_compute.set_fraction(self.pix_id/self.pix_qty)
            
            
        # Current position.
        data_to_send += '\n'
        self.data_buffer.append(data_to_send)
       
        # If end of line, first shut the laser out.
        if i == self.width - 1:
            data = 'I%sL%sM%s'%(self.pix_id, 0, 0)
            data += '\n'
            self.data_buffer.append(data)
    

        # increment the pixel id
        self.pix_id += 1
        
        
        # if pix_id is greater than pix_qty, the whole image have been parsed.
        # set pix_id and compute_flag to 0, hide progress bar
        if self.pix_id >= self.pix_qty:
            self.fin = time()
            duree = self.fin - self.debut
            ImageObject.ser.send_cfg('size', self.pix_qty)
            self.pix_id = 0
            self.compute_flag = 0
            self.computed_flag = 1
            ImageObject.wm.status('Image calculée en %.3fs.'%duree)            
            ImageObject.wm.progress_compute.hide()
        return 1