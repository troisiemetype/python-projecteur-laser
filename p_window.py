#!/usr/bin/python3.4

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

#needed for key pressed codes
from gi.repository import Gdk

#needed for the connexion
from serial import SerialException

#definition of main program window
class Window:
    #Init function
    #construct the main window
    #connects the widget to the function they need
    def __init__(self):
        #set at 1 the var that traces if the program is running
        self.running = 1
        #construct the window from the glade file
        self.builder = Gtk.Builder()
        self.builder.add_from_file('fenetre_projecteur.glade')
        
        #attach the main and settings window to their program objects
        self.window_main = self.builder.get_object('windowMain')
        self.window_settings = self.builder.get_object('windowSettings')
        self.window_file = self.builder.get_object('windowFile')
        self.statusbar = self.builder.get_object('statusbar1')
        
        #attache the pause button
        self.toolbutton_pause = self.builder.get_object('toolbutton_pause')
        
        #attach the image area
        self.image = self.builder.get_object('image1')
        
        #Attach the builder objects to their program objects
        self.port = self.builder.get_object('comboPortList')
        self.baudrate = self.builder.get_object('comboBaudRate')
        self.databits = self.builder.get_object('labelDataBits')
        self.parity = self.builder.get_object('labelParity')
        self.stopbits = self.builder.get_object('labelStopBits')
        self.xonxoff = self.builder.get_object('labelXON')
        
        #Attache the coordinates area to their program objects
        self.support_dimensions = self.builder.get_object('grid_support_dimensions')
        self.image_dimensions = self.builder.get_object('grid_image_dimensions')

        #Attach the builder entry to their program objects
        self.support_distance = self.builder.get_object('value_support_distance')
        self.support_width = self.builder.get_object('value_support_width')
        self.support_height = self.builder.get_object('value_support_height')
        self.support_speed = self.builder.get_object('value_support_speed')
        
        self.image_width = self.builder.get_object('value_image_width')
        self.image_height = self.builder.get_object('value_image_height')
        
        #Attach the value signals with their function
        self.support_distance.connect('activate', self.on_support_activate, 'distance')
        self.support_width.connect('activate', self.on_support_activate, 'support_width')
        self.support_height.connect('activate', self.on_support_activate, 'support_height')
        self.support_speed.connect('activate', self.on_support_activate, 'speed')
        
        self.image_width.connect('activate', self.on_image_activate, 'image_width')
        self.image_height.connect('activate', self.on_image_activate, 'image_height')
        
        self.progress_total = self.builder.get_object('progress_total')
        self.progress_step = self.builder.get_object('progress_step')

        #creates a context id for the status bar
        self.context_id = self.statusbar.get_context_id('status')
        
        self.port_list_ok = 0
        self.baud_list_ok = 0
        
        #Connect signals from the builder (mostly buttons clicks)
        self.builder.connect_signals(self)
        
    #This function sets a link to the SerialLink object, so the GUI can use it
    def set_serial(self, ser):
        self.ser = ser
    
    #This function sets a link to the Image object, so the GUI can use it
    def set_image(self, im):
        self.im = im
    
    #sets the cfg values from a serial object
    def set_serial_cfg(self):
        #populates the settings menu with values from settings file
        self.databits.set_text(str(self.ser.bytesize))
        self.parity.set_text(self.ser.parity)
        self.stopbits.set_text(str(self.ser.stopbits))
        self.xonxoff.set_text(str(self.ser.xonxoff))
    
    #sets the cfg values for the image
    def set_cfg(self, cfg):
        self.cfg = cfg
        
        self.support_distance.set_text(str(cfg.distance))
        self.support_width.set_text(str(cfg.support_width))
        self.support_height.set_text(str(cfg.support_height))
        self.support_speed.set_text(str(cfg.speed))
        
        self.image_width.set_text(str(cfg.width))
        self.image_height.set_text(str(cfg.height))
    
    #construct the port list.
    #called the first time the update_port_list() function is called
    def init_port_list(self):
        #construct the port list    
        self.port.set_model(self.list_port)
        self.cell = Gtk.CellRendererText()
        self.port.pack_start(self.cell, True)
        self.port.add_attribute(self.cell, 'text', 1)
        self.port.set_active(self.active_port)
        self.port_list_ok = 1

    #construct the baudrate list    
    def init_baud_list(self):
        self.baudrate.set_model(self.list_baud)
        self.cell = Gtk.CellRendererText()
        self.baudrate.pack_start(self.cell, True)
        self.baudrate.add_attribute(self.cell, 'text', 0)
        self.baudrate.set_active(self.active_baudrate)
        self.baud_list_ok = 1
        
        
    #defines/update the list of available ports
    def update_port_list(self, list_port, port=None):
        self.list_port = Gtk.ListStore(int, str)
        self.active_port = 0
        i = 0
        for port in list_port:
            print(port)
            self.list_port.append([i, port])
            if self.ser.port == port:
                self.active_port = i
            i += 1
        self.port.set_model(self.list_port)
        if self.port_list_ok == 0:
            self.init_port_list()
        self.status('Liste des ports mise à jour')
    
    #defines/update the list of availables baudrates
    def update_baudrate_list(self, tupl_baud, baudrate=9600):
        self.list_baud = Gtk.ListStore(int)
        self.active_baudrate = 0
        i = 0
        for baudrate in tupl_baud:
            self.list_baud.append([baudrate])
            if baudrate == baudrate:
                self.active_baudrate = i
            i += 1
        if self.baud_list_ok == 0:
            self.init_baud_list()
    
    #defines the funcion that records entry in the support field
    #just calls the cfg.update_support_cfg() function, that verifies the values passed.
    def on_support_activate(self, widget, attribute=None, event=None):
        print(event)
        answer = self.cfg.update_support_value(attribute, int(widget.get_text()))
        if answer != 0:
            self.message_erreur('Valeur maximale permise: %s'%answer,
                                "Augmentez la distance entre le projecteur et le support si vous désirez une surface d'exposition supérieure")
        self.set_cfg(self.cfg)

    #defines the funcion that records entry in the image field
    #Just calles the cfg function, that verifies values passed.
    def on_image_activate(self, widget, attribute):
        answer = self.cfg.update_image_value(attribute, int(widget.get_text()), self.im.ratio)
        if answer != 0:
            self.message_erreur ('Valeur maximale admise: %s'%answer,
                                 "Les dimensions de l'image ne peuvent exceder celles du support")
        self.set_cfg(self.cfg)
            

    #Defines the close/quit function for the main window
    def on_quit(self, widget):
        Gtk.main_quit()
        self.running = 0
        
    #defines the function for opening file
    def on_open(self, widget):
        self.window_main.set_sensitive(False)
        self.window_file.show()
    
    #defines the function for closing file
    #if self.im.im is notdefined, no image is active: return doing nothing
    #It asks if we want to close the image,
    #sets the default icon in the image area,
    #and last, call the close_file() image function
    def on_close(self, widget):
        if self.im.im == None:
            return
        answer = self.message_validation("Fermer l'image", 'Tous les réglages seront perdus')
        if answer != -5:
            return
        self.image.set_from_icon_name(Gtk.STOCK_MISSING_IMAGE, 6)
        self.image_dimensions.hide()
        self.status('Image %s fermée'%self.im.uri)
        self.im.close_file()
    
    #defines the function for preferences
    def on_settings(self, widget):
        self.window_main.set_sensitive(False)
        self.window_settings.show()
    
    #defines how the connection is handled
    def on_connect(self, widget):
        #Verifies that we're not already connected
        if self.ser.isOpen():
            self.message_erreur('Vous êtes déja connecté')
            return
        #try to connect to the port
        try:
            self.ser.open()
            self.status('Connecté à %s' %self.ser.port)
        #else catch an exception and display an error message
        except SerialException:
            self.message_erreur('Erreur de connexion',
                               'Vérifiez la connexion et/ou les paramètres de connexion')
        
    #defines the function for disconnect
    def on_disconnect(self, widget):
        self.ser.close()
        self.status('déconnecté')
    
    #Defines the function that launch/stops the calibration.
    def on_calibrate_toggle(self, widget):
        #If the button is active, then start the calibration
        if widget.get_active():
            self.support_dimensions.set_sensitive(False)
            self.image_dimensions.set_sensitive(False)
            self.im.calibration_flag = 1
            self.im.calibrate()
            
        #else it's not, so stop the calibration
        else:
            self.support_dimensions.set_sensitive(False)
            self.image_dimensions.set_sensitive(False)
            self.im.calibration_flag = 0
            
    #defines the compute function
    def on_compute(self, widget):
        self.progress_total.show()
        self.status('Calcul en cours...')
        self.im.compute_image(self.progress_total.set_fraction)
        self.status('Image calculée, prête à être envoyée au projecteur.')
        self.progress_total.hide()
        
    
    #defines the function for sending data - Empty for now
    def on_send(self, widget):
        if self.ser.pause_flag == 1:
            self.toolbutton_pause.set_active(0)
        else:
            self.ser.send_flag = 1
    
    #defines the function for pausing data - Empty for now
    def on_pause(self, widget):
        if widget.get_active():
            self.ser.pause_flag = 1
        else:
            self.ser.pause_flag = 0
    
    #defines the function for stopping data - Empty for now
    def on_stop(self, widget):
        self.ser.send_flag = 0
        #need to add a (call to a) method that init the laser on 0
    
    #defines the function for updating port list
    def on_button_scan_clicked(self, widget):
        self.update_port_list(self.ser.get_ports(), self.ser.port)
        
     #Defines a function that stop delete events to don't kill the object.
     #Needed as without it, closing the window from the cross or using "escape"
     #will kill the object, and so it won't be reachable at next call
    def on_delete_event(self, widget, event):
        widget.hide()
        self.window_main.set_sensitive(True)
        return True
    
    #defines the function for validating settings
    #TODO: find how to link it with the cfg save
    def on_settings_ok_clicked(self, widget):
        #cfg.save()
        self.window_settings.hide()
        self.window_main.set_sensitive(True)
        
    #defines the function for cancelling settings
    def on_settings_cancel_clicked(self, widget):
        self.window_settings.hide()
        self.window_main.set_sensitive(True)
        
    #defines the function that handles opening file
    #TODO: look at how to link it with the file openning
    def on_file_ok_clicked(self, widget):
        if self.im.open_file(self.window_file.get_filename()):
            self.window_main.set_sensitive(True)
            self.window_file.hide()
            self.image.set_from_pixbuf(self.im.get_pixbuf())
            self.image_dimensions.show()
            self.status('Image %s ouverte'%self.im.uri)
    
    #defines the function that handles openning file
    def on_file_cancel_clicked(self, widget):
        self.window_file.hide()
        self.window_main.set_sensitive(True)
    
    #defines the function that handle return key on file openning
    def on_window_file_key_press_event(self, widget, event):
        if event.keyval == Gdk.KEY_Return:
            self.on_file_ok_clicked(widget)
    
    #defines the basic error message
    def message_erreur(self, message='', secondary=None):
        dialog = Gtk.MessageDialog(self.window_main, Gtk.DialogFlags.MODAL,
                                          Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                                          message)
        if secondary != None:
            dialog.format_secondary_text(secondary)
        
        self.window_main.set_sensitive(False)        
        dialog.run()
        dialog.destroy()
        self.window_main.set_sensitive(True)
        
    
    #defines a dialog that display a message, and return a yes/no value
    def message_validation(self, message='', secondary=None):
        dialog = Gtk.MessageDialog(self.window_main, Gtk.DialogFlags.MODAL,
                                             Gtk.MessageType.INFO, Gtk.ButtonsType.OK_CANCEL,
                                             message)
        if secondary != None:
            dialog.format_secondary_text(secondary)
        self.window_main.set_sensitive(False)
        answer = dialog.run()
        dialog.destroy()
        self.window_main.set_sensitive(True)
        return answer
            
    #defines the status update
    def status(self, status):
        self.statusbar.push(self.context_id, status)