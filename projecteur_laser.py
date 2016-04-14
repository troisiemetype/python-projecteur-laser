#!/usr/bin/python3.4

#imports
import p_configuration
import p_serial
#import window

#instanciate classes,
#display the GUI
if __name__ == "__main__":
    #creates the config class
    default_cfg = p_configuration.Configuration('config_default.cfg')
    
    #get the serial configuration
    serial_cfg = default_cfg.get_serial_cfg()
    
    #creates the serial class
    ser = p_serial.SerialLink()
    #initiate it with value from configuration file
    ser.init_from_cfg(serial_cfg)
    
    #wm = Window()
    #serialInit(ser)
    #wm.status('Initialisation réussie')
    #Gtk.main()