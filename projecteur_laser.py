#!/usr/bin/python3.4

#imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import ConfigParser

import serial
import serial.tools.list_ports

from PIL import Image

import array
from gi.repository import GdkPixbuf

im = Image.new('RGB', (20,20))
#thumbnail = Image

ser = serial.Serial()

tuplBaud = (300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200)

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
        self.windowFile = interface.get_object('windowFile')
        self.statusbar = interface.get_object('statusbar1')
        
        #attach the interface area to their program objects
        self.image = interface.get_object('image1')
        
        #Attach the interface objects to their program objects
        self.port = interface.get_object('comboPortList')
        self.baudrate = interface.get_object('comboBaudRate')
        self.databits = interface.get_object('labelDataBits')
        self.parity = interface.get_object('labelParity')
        self.stopbits = interface.get_object('labelStopBits')
        self.xonxoff = interface.get_object('labelXON')
        
        #construct the port list
        self.updateListPort()

        self.port.set_model(self.listPort)
        self.cell = Gtk.CellRendererText()
        self.port.pack_start(self.cell, True)
        self.port.add_attribute(self.cell, 'text', 1)
        self.port.set_active(self.activePort)
        
        #construct the baudrate list
        self.updateListBaudrate()
        
        self.baudrate.set_model(self.listBaud)
        self.cell = Gtk.CellRendererText()
        self.baudrate.pack_start(self.cell, True)
        self.baudrate.add_attribute(self.cell, 'text', 0)
        self.baudrate.set_active(self.activeBaudrate)
        
        
        #populates the settings menu with values from settings file
        self.databits.set_text(str(cfg.databits))
        self.parity.set_text(cfg.parity)
        self.stopbits.set_text(str(cfg.stopbits))
        self.xonxoff.set_text(str(cfg.xonxoff))
        
        #creates a context id for the status bar
        self.context_id = self.statusbar.get_context_id('status')
        
        #Connect signals from interface (mostly buttons clicks)
        interface.connect_signals(self)
    
    #defines/update the list of available ports
    def updateListPort(self):
        lp = serialGetPorts()
        self.listPort = Gtk.ListStore(int, str)
        self.activePort = 0
        i = 0
        for port in lp:
            self.listPort.append([i, port])
            if cfg.port == port:
                self.activePort = i
            i += 1
    
    #defines/update the list of availables baudrates
    def updateListBaudrate(self):
        self.listBaud = Gtk.ListStore(int)
        self.activeBaudrate = 0
        i = 0
        for baudrate in tuplBaud:
            self.listBaud.append([baudrate])
            if cfg.baudrate == baudrate:
                self.activeBaudrate = i
            i += 1
            
    #Defines the close/quit function for the main window
    def on_quit(self, widget):
        Gtk.main_quit()
    
    #defines the function for opening file
    def on_open(self, widget):
        self.windowFile.show()
    
    #defines the function for closing file
    def on_close(self, widget):
        pass
    
    #defines the function for preferences
    def on_settings(self, widget):
        self.windowSettings.show()
    
    #defines the function for connect
    def on_connect(self, widget):
        #try to connect to the board
        if ser.isOpen():
            self.messageErreur('Vous êtes déjà connecté')
            return
        try:
            ser.open()
            self.status('Connecté à %s' %ser.port)
        #else catch an exception and display an error message
        except serial.SerialException:
            self.messageErreur('Erreur de connexion',
                               'Vérifiez la connexion et/ou les paramètres de connexion')
    
    #defines the function for disconnect
    def on_disconnect(self, widget):
        ser.close()
        self.status('deconnecté')
    
    #defines the function for sending data
    def on_send(self, widget):
        pass
    
    #defines the fnuction for pausing data
    def on_pause(self, widget):
        pass
    
    #defines the function for stopping data
    def on_stop(self, widget):
        pass
   
   #defines the function for updating port list
    def on_buttonScan_clicked(self, widget):
        self.updateListPort()
    
    #defines a function that stop delete events to don't kill the object
    #needed as without it, closing the window from the cross or using "escape"
    #will kill the object, and so it won't be reachable at next call
    def on_delete_event(self, widget, event):
        widget.hide()
        return True
    
    #defines the function for validating settings
    def on_settingsOK_clicked(self, widget):
        cfg.save()
        self.windowSettings.hide()
        
    #defines the function for cancelling settings
    def on_settingsCancel_clicked(self, widget):
        self.windowSettings.hide()
    
    #defines the function for validating opening file
    def on_fileOK_clicked(self, widget):
        if openFile(self.windowFile.get_filename()):
            self.windowFile.hide()
    
    #defines the function for cancelling openning file
    def on_fileCancel_clicked(self, widget):
        self.windowFile.hide()
        
    def on_dialog_close(self, widget):
        self.windowFile.hide()
        self.status('closed with escape')
    
    #defines the basic error message
    def messageErreur(self, message='', secondary=None):
        windowMessage = Gtk.MessageDialog(self.windowMain, Gtk.DialogFlags.MODAL,
                                          Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                                          message)
        if secondary != None:
            windowMessage.format_secondary_text(secondary)
        windowMessage.run()
        windowMessage.destroy()
    
    #defines the status update
    def status(self, status):
        self.statusbar.push(self.context_id, status)
        

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
def serialGetPorts():
    listPortInfo = serial.tools.list_ports.comports()
    listPort = []
    for tup in listPortInfo:
        listPort.append(tup[0])
    return listPort

#This function deals with openning a new file
def openFile(uri):
    #try to open the file, else give an Error message
    try:
        im = Image.open(uri)
    except IOError:
        wm.messageErreur('Veuillez choisir un fichier image',
                         'Fichiers pris en charge: bmp, jpg, png, tiff, svg')
        return False
    #display status
    wm.status('open %s' %uri)
    #Load the image, get its size, create thumbnail
    im.load()
    w,h = im.size
    thumb = im
    thumb.thumbnail((450, int(450*h/w)))
    #sets the thumbnail in the image area, through the imageToPixbuf function
    wm.image.set_from_pixbuf(imageToPixbuf(thumb))
    return True

#this function converts PIL images to Pixbuf format for displaying in Gtk
def imageToPixbuf(im):
    #transforms the given image into an array of pixels
    arr = array.array('B', im.tostring())
    w,h=im.size
    #look at a an alpha mask
    if im.mode == 'RGBA':
        hasAlpha = True
        dist = w*4
    else:
        hasAlpha = False
        dist = w*3
    #returns the pix buf. Args:
    #array, colorspace, has alpha, bits per sample,
    #width, height, distance in bytes between row starts
    return GdkPixbuf.Pixbuf.new_from_data(arr, GdkPixbuf.Colorspace.RGB, hasAlpha, 8, w, h, dist)

    

#instanciates the config and window objects.
#call the serial initialisation function
#display the GUI
if __name__ == "__main__":
    cfg = config()
    serialInit(ser)
    wm = window()
    serialInit(ser)
    wm.status('Initialisation réussie')
    Gtk.main()