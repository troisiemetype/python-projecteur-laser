#!/usr/bin/python3.4

#imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import ConfigParser

import serial

serialLink = serial.Serial()

tuplBaud = (300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200)
listPorts = []

#definition of the config parser class
class config:
    #init function
    def __init__(self):
        #Creation of the config object
        self.config = ConfigParser.ConfigParser()
        self.config.read('config_default.cfg')
        
        #creation of an attribute for each var
        #Serial attributes
        self.configfile = self.config.get('configuration', 'config')
        self.port = self.config.get('serial','port')
        self.baudrate = self.config.getint('serial','baudrate')
        self.databits = self.config.getint('serial', 'databits')
        self.parity = self.config.get ('serial', 'parity')
        self.stopbits = self.config.getint('serial', 'stopbits')
        
        self.xonxoff = self.config.getboolean('serial', 'flowcontrolxon')
        
        #image attributes
        self.height = self.config.getint('image', 'height')
        self.width = self.config.getint('image', 'width')
        self.distance = self.config.getint('image', 'distance')
        self.speed = self.config.getint('image', 'speed')
    
    #definition of the save function
    def save(self):
        with open('config_copie.cfg', 'w') as configfile:
            self.config.write(configfile)
    
        
#definition of main program window
class window:
    #Init function
    #construct the main window
    #connects the widget to the function they need
    def __init__(self):
        #construct the window from the glade file
        interface = Gtk.Builder()
        interface.add_from_file('fenetre_projecteur.glade')
        
        #attach the main and settings window to their program objects
        self.windowMain = interface.get_object('windowMain')
        self.windowSettings = interface.get_object('windowSettings')
        
        #Attach the interface objects to thier program objects
        self.port = interface.get_object('comboPortList')
        self.baudrate = interface.get_object('comboBaudRate')
        self.databits = interface.get_object('labelDataBits')
        self.parity = interface.get_object('labelParity')
        self.stopbits = interface.get_object('labelStopBits')
        self.xonxoff = interface.get_object('labelXON')
        
        #define the list of baudrates
        #TODO: use the list that's defined at the beginning of the program instead
        self.listBaud = Gtk.ListStore(int, str)
        self.listBaud.append([1,"300"])
        self.listBaud.append([2,"600"])
        self.listBaud.append([3,"1200"])
        self.listBaud.append([4,"2400"])
        self.listBaud.append([5,"4800"])
        self.listBaud.append([6,"9600"])
        self.listBaud.append([7,"14400"])
        self.listBaud.append([8,"19200"])
        self.listBaud.append([9,"28800"])
        self.listBaud.append([10,"38400"])
        self.listBaud.append([11,"57600"])
        self.listBaud.append([12,"115200"])
        
        #construct the list
        self.cell = Gtk.CellRendererText()
        self.baudrate.pack_start(self.cell, True)
        self.baudrate.add_attribute(self.cell, 'text', 1)
        
        #self.baudrate.set_active(item)
        
        #populates the settings menu with values from settings file
        self.baudrate.set_model(self.listBaud)
        self.databits.set_text(str(cfg.databits))
        self.parity.set_text(cfg.parity)
        self.stopbits.set_text(str(cfg.stopbits))
        self.xonxoff.set_text(str(cfg.xonxoff))
        
        #Connect signals from interface (mostly buttons clicks)
        interface.connect_signals(self)
        
    #Defines the close/quit function for the main window
    def on_mainWindow_destroy(self, widget):
        Gtk.main_quit()
    
    #defines the function when quitting from menu/file/quit
    def on_menuQuit_activate(self, widget):
        Gtk.main_quit()
    
    #defines the function for menu/file/open
    def on_menuOpen_activate(self, widget):
        pass
    
    #defines the function for menu/file/close
    def on_menuClose_activate(self, widget):
        pass
    
    #defines the function for menu/edit/pref
    def on_menuSettings_activate(self, widget):
        self.windowSettings.show()
    
    #defines the function for menu/serial/connect
    def on_menuConnect_activate(self, widget):
        #try to connect to the board
        try:
            serialLink.open()
        #else catch an exception and display an error message
        except serial.SerialException:
            self.messageErreur('Erreur de connexion',
                               'Vérifiez la connexion et/ou les paramètres de connexion')
    
    #defines the function for menu/serial/disconnect
    def on_menuDisconnect_activate(self, widget):
        serial.close()
            
    #defines the function for validating settings
    def on_settingsOK_clicked(self, widget):
        cfg.save()
        self.windowSettings.hide()
        
    #defines the function for cancelling settings
    def on_settingsCancel_clicked(self, widget):
        self.windowSettings.hide()
        
    #defines the basic error message
    def messageErreur(self, message='', secondary=None):
        windowMessage = Gtk.MessageDialog(self.windowMain, Gtk.DialogFlags.MODAL,
                                          Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                                          message)
        if secondary != None:
            windowMessage.format_secondary_text(secondary)
        windowMessage.run()
        windowMessage.destroy()

#init the serial link with the values copied from the config file
def serialInit(serial):
    serial.port = cfg.port
    serial.baudrate = cfg.baudrate
    serial.bitsize = cfg.databits
    serial.parity = cfg.parity
    serial.stopbits = cfg.stopbits
    serial.xonxoff = cfg.xonxoff
    serial.timeout = 1

#get a list of the available ports. don't know yet if it's faisible
def serialGetPorts(serial):
    pass

#instanciates the config and window objects.
#call the serial initialisation function
#display the GUI
if __name__ == "__main__":
    cfg = config()
    wm = window()
    serialInit(serialLink)
    Gtk.main()