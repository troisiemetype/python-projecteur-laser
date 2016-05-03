#!/usr/bin/python3.4

#imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from p_configuration import Configuration as conf
from p_serial import SerialLink as serial
from p_window import Window as win
from p_jsonparser import JsonParser as json
from p_file import FileObject as file
from p_image import ImageObject as image

# instantiate classes,
# display the GUI
# creates the Window class instance
wm = win()

# creates the Configuration class instance
cfg = conf('config_default.cfg')
# displays a status
wm.status('Fichier de configuration chargé.')
# get the serial configuration
serial_cfg = cfg.get_serial_cfg()

# creates the SerialLink class instance
ser = serial()
# initiate it with value from configuration file
ser.init_from_cfg(serial_cfg)
serial.wm = wm
wm.status('Liaison série initialisée')

# sets a link to the SerialLink object ser, so that vm can use it
wm.ser = ser
# updates the port list and the baudrate list used in settings window
wm.update_port_list()
wm.update_baudrate_list()
wm.cfg = cfg
wm.set_serial_cfg()
wm.set_cfg(cfg)

# Creates the json parser class instance
jsp = json()
serial.jsp = jsp

# creates the imageObject class instance
fi = file()
file.cfg = cfg
file.jsp = jsp
file.wm = wm
file.ser = ser
# and attach it to the other objects
serial.fi = fi
wm.fi = fi
wm.status("gestionnaire d'image créé")
wm.status('initialisation complète')

# Main loop. Calls the window refresh on each iteration
while wm.running == 1:
    Gtk.main_iteration_do(False)
    if ser.send_calibration():
        continue

    fi.compute_file()
    ser.send_data()
    ser.read_data()
    ser.parse_data()

