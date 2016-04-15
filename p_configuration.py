
import configparser

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
        cfgdict = {'ditance':self.distance, 'width':self.width,
                   'height':self.height, 'speed':self.speed}
        return cfg_dict
    
    #definition of the save function
    def save(self):
        with open('config_copie.cfg', 'w') as configfile:
            self.config.write(configfile)
