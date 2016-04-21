#!/usr/bin/python3.4

#imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

#program classes (like includes)
from p_configuration import Configuration as conf
from p_serial import SerialLink as serial
from p_window import Window as win
from p_jsonparser import JsonParser as json
from p_image import ImageObject as image

#instanciate classes,
#display the GUI
#creates the Window class instance
wm = win()

#creates the Configuration class instance
cfg = conf('config_default.cfg')   
#displays a status
wm.status('Fichier de configuration chargé.')
#get the serial configuration
serial_cfg = cfg.get_serial_cfg()

#creates the SerialLink class instance
ser = serial()
#initiate it with value from configuration file
ser.init_from_cfg(serial_cfg)
serial.wm = wm
wm.status('Liaison série initialisée')

#sets a link to the SerialLink object ser, so that vm can use it
wm.ser = ser
#updates the port list and the baudrate list used in settings window
wm.update_port_list(ser.get_ports(), ser.port)
wm.update_baudrate_list(ser.get_baudrates(), ser.baudrate)
wm.cfg = cfg
wm.set_serial_cfg()
wm.set_cfg(cfg)

#Creates the json parser class instance
jsp = json()
serial.jsp = jsp

#creates the imageObject class instance
im = image()
image.cfg = cfg
image.jsp = jsp
image.wm = wm
image.ser = ser
#and attach it to the other objects
serial.im = im
wm.im = im
wm.status("gestionnaire d'image créé")
wm.status('initialisation réussie')

#Main loop. Calls the window refresh on each iteration
while wm.running == 1:
    Gtk.main_iteration_do(False)
    if ser.send_calibration():
        continue
    im.compute_image()
    ser.send_data()
    ser.read_data()