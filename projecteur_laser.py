#!/usr/bin/python3.4

#imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

#program classes (like includes)
import p_configuration
import p_serial
import p_window
import p_image

#instanciate classes,
#display the GUI
if __name__ == "__main__":
    #creates the Configuration class instance
    cfg = p_configuration.Configuration('config_default.cfg')
    
    #get the serial configuration
    serial_cfg = cfg.get_serial_cfg()
    
    #creates the SerialLink class instance
    ser = p_serial.SerialLink()
    #initiate it with value from configuration file
    ser.init_from_cfg(serial_cfg)
    
    #creates the Window class instance
    wm = p_window.Window()
    #sets a link to the SerialLink object ser, so that vm can use it
    wm.set_serial(ser)
    #updates the port list and the baudrate list used in settings window
    wm.update_port_list(ser.get_ports(), ser.port)
    wm.update_baudrate_list(ser.get_baudrates(), ser.baudrate)
    wm.set_serial_cfg()
    wm.status('initialisation réussie')
    wm.set_image_cfg(cfg)
    
    #creates the imageObject class instance
    im = p_image.ImageClass()
    #and attach it to the wm object
    wm.set_image(im)
    
    #launch the main Gtk loop, that displays the GUI
    Gtk.main()