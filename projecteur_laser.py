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
#creates the Window class instance
wm = p_window.Window()

#creates the Configuration class instance
cfg = p_configuration.Configuration('config_default.cfg')   
#displays a status
wm.status('Fichier de configuration chargé.')
#get the serial configuration
serial_cfg = cfg.get_serial_cfg()

#creates the SerialLink class instance
ser = p_serial.SerialLink()
#initiate it with value from configuration file
ser.init_from_cfg(serial_cfg)
wm.status('Liaison série initialisée')

#sets a link to the SerialLink object ser, so that vm can use it
wm.set_serial(ser)
#updates the port list and the baudrate list used in settings window
wm.update_port_list(ser.get_ports(), ser.port)
wm.update_baudrate_list(ser.get_baudrates(), ser.baudrate)
wm.set_serial_cfg()
wm.set_cfg(cfg)

#creates the imageObject class instance
im = p_image.ImageObject()
im.set_cfg(cfg)
#and attach it to the wm object
wm.set_image(im)
wm.status("gestionnaire d'image créé")
wm.status('initialisation réussie')

#Main loop. Calls the window refresh on each iteration
while wm.running == 1:
    Gtk.main_iteration_do(False)
    try:
        if im.calibration_flag == 1:
            im.send_calibration()
    except:
        pass
    try:
        if im.compute_flag == 1:
            im.compute_image(wm.progress_total)
    except:
        pass