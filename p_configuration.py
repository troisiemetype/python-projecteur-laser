
import configparser

from math import tan, degrees, radians

#definition of the config parser class
class Configuration:
    #init function
    def __init__(self, cfg_file):
        #Creation of the config object
        self.cfg_file = cfg_file
        self.config = configparser.ConfigParser()
        self.config.read(cfg_file)
        
        #creation of an attribute for each var
        #Serial attributes
        self.configfile = self.config.get('configuration', 'config')
        self.port = self.config.get('serial','port')
        self.baudrate = self.config.getint('serial','baudrate')
        self.databits = self.config.getint('serial', 'databits')
        self.parity = self.config.get('serial', 'parity')
        self.stopbits = self.config.getint('serial', 'stopbits')
        self.timeout = self.config.getint('serial', 'timeout')
        self.xonxoff = self.config.getboolean('serial', 'flowcontrolxon')
        
        #image attributes
        self.height = self.config.getint('image', 'height')
        self.width = self.config.getint('image', 'width')
        self.distance = self.config.getint('image', 'distance')
        self.speed = self.config.getint('image', 'speed')
        self.support_width = self.config.getint('image', 'support_width')
        self.support_height = self.config.getint('image', 'support_height')
        self.h_angle = self.config.getint('image', 'h_angle')
        self.v_angle = self.config.getint('image', 'v_angle')
        
    
    #getter for serial cfg
    #construct a dictionnary with the values read in config file
    def get_serial_cfg(self):
        cfg_dict = {'port': self.port, 'baudrate': self.baudrate, 'bytesize': self.databits,
                    'parity': self.parity, 'stopbits': self.stopbits, 'timeout': self.timeout, 
                    'xonxoff': self.xonxoff}
        return cfg_dict
    
    #getter for image cfg
    #construct a dictionnary with the values read in config file
    def get_image_cfg(self):
        cfgdict = {'ditance':self.distance, 'support_width':self.support_width,
                   'support_height':self.support_height, 'speed':self.speed,
                   'width':self.width, 'height':self.height,
                   'v_angle':self.v_angle, 'h_angle':self.h_angle}
        return cfg_dict
    
    #defines the function that update the cfg support values from the Gtk entries
    #before to update it verifies that the values are correct
    def update_support_value(self, attribute, value):
        if attribute == 'distance':
            self.distance = value
            max_width = int(2 * value * tan(radians(self.h_angle/2)))
            max_height = int(2 * value * tan(radians(self.v_angle/2)))
            if self.support_width > max_width:
                self.support_width = max_width
            if self.support_height > max_height:
                self.support_height = max_height
            if self.width > self.support_width:
                self.width = self.support_width
            if self.height > self.support_height:
                self.width = self.support_height
    
        elif attribute =='support_width':
            if value > (2 * self.distance * tan(radians(self.h_angle/2))):
                return int(2 * self.distance * tan(radians(self.h_angle/2)))
            else:
                self.support_width = value
        elif attribute =='support_height':
            if value > (2 * self.distance * tan(radians(self.v_angle/2))):
                return int(2 * self.distance * tan(radians(self.v_angle/2)))
            else:
                self.support_height = value
        elif attribute =='speed':
            self.speed == value
        return 0
                        

    #defines the function that update the cfg image values from the Gtk entries
    #before to update it verifies that the values are correct
    def update_image_value(self, attribute, value, ratio):
        if attribute == 'image_width':
            #tests that value is less than the support
            if value > self.support_width:
                return self.support_width
            #if no, records the new value, and set the other one according to ratio
            else:
                self.width = value
                self.height = int(value / ratio)
        #same with the other value
        elif attribute == 'image_height':
            if value > self.support_height:
                return self.support_height
            else:
                self.height = value
                self.width = int(value * ratio)
        #returns 0 when the writing was successful
        return 0
    
    #definition of the save function
    def save(self):
        with open('config_copie.cfg', 'w') as configfile:
            self.config.write(configfile)
