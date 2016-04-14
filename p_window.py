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
        #construct the window from the glade file
        self.builder = Gtk.Builder()
        self.builder.add_from_file('fenetre_projecteur.glade')
        
        #attach the main and settings window to their program objects
        self.window_main = self.builder.get_object('windowMain')
        self.window_settings = self.builder.get_object('windowSettings')
        self.window_file = self.builder.get_object('windowFile')
        self.statusbar = self.builder.get_object('statusbar1')
        
        #attach the the builder area to their program objects
        self.image = self.builder.get_object('image1')
        
        #Attach the the builder objects to their program objects
        self.port = self.builder.get_object('comboPortList')
        self.baudrate = self.builder.get_object('comboBaudRate')
        self.databits = self.builder.get_object('labelDataBits')
        self.parity = self.builder.get_object('labelParity')
        self.stopbits = self.builder.get_object('labelStopBits')
        self.xonxoff = self.builder.get_object('labelXON')

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

    #construct the     
    def init_baud_list(self):
        #construct the baudrate list
        self.baudrate.set_model(self.list_baud)
        self.cell = Gtk.CellRendererText()
        self.baudrate.pack_start(self.cell, True)
        self.baudrate.add_attribute(self.cell, 'text', 0)
        self.baudrate.set_active(self.active_baudrate)
        self.baud_list_ok = 1
        
        
    #defines/update the list of available ports
    def update_port_list(self, list_port, port=None):
        self.list_port = Gtk.ListStore(int, str)
        print(self.list_port)
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
            
    #Defines the close/quit function for the main window
    def on_quit(self, widget):
        Gtk.main_quit()
        
    #defines the function for opening file
    def on_open(self, widget):
        self.window_file.show()
    
    #defines the function for closing file
    def on_close(self, widget):
        answer = self.message_validation("Fermer l'image", 'Tous les reglages seront perdus')
        if answer == -5:
            close_file()
    
    #defines the function for preferences
    def on_settings(self, widget):
        self.window_settings.show()
    
    #defines how the connection is handled
    def on_connect(self, widget):
        #Verifies that we're not already connected
        if self.ser.isOpen():
            self.message_erreur('Vous etes deja connecte')
            return
        #try to connect to the port
        try:
            self.ser.open()
            self.status('Connecte a %s' %self.ser.port)
        #else catch an exception and display an error message
        except SerialException:
            self.message_erreur('Erreur de connexion',
                               'Verifiez la connexion et/ou les parametres de connexion')
        
    #defines the function for disconnect
    def on_disconnect(self, widget):
        self.ser.close()
        self.status('deconnecte')

    
    #defines the function for sending data - Empty for now
    def on_send(self, widget):
        pass
    
    #defines the fnuction for pausing data - Empty for now
    def on_pause(self, widget):
        pass
    
    #defines the function for stopping data - Empty for now
    def on_stop(self, widget):
        pass
    
    #defines the function for updating port list
    def on_button_scan_clicked(self, widget):
        self.update_port_list(self.ser.get_ports(), self.ser.port)
     #Defines a function that stop delete events to don't kill the object.
     #Needed as without it, closing the window from the cross or using "escape"
     #will kill the object, and so it won't be reachable at next call
    def on_delete_event(self, widget, event):
        widget.hide()
        return True
    
    #defines the function for validating settings
    #TODO: find how to link it with the cfg save
    def on_settings_ok_clicked(self, widget):
        #cfg.save()
        self.window_settings.hide()
        
    #defines the function for cancelling settings
    def on_settings_cancel_clicked(self, widget):
        self.window_settings.hide()
        
    #defines the function that handles opening file
    #TODO: look at how to link it with the file openning
    def on_file_ok_clicked(self, widget):
        #if openFile(self.window_file.get_filename()):
            self.window_file.hide()
    
    #defines the function that handles openning file
    def on_file_cancel_clicked(self, widget):
        self.window_file.hide()
    
    #defines the function that handle return key on file openning
    def on_window_file_key_press_event(self, widget, event):
        if event.keyval == Gdk.KEY_Return:
            self.on_file_ok_clicked(widget)
    
    #defines the close cancel button handeling
    def on_dialog_close(self, widget):
        self.window_file.hide()
    
    #defines the basic error message
    def message_erreur(self, message='', secondary=None):
        dialog = Gtk.MessageDialog(self.window_main, Gtk.DialogFlags.MODAL,
                                          Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                                          message)
        if secondary != None:
            dialog.format_secondary_text(secondary)
        dialog.run()
        dialog.destroy()
    
    #defines a dialog that display a message, and return a yes/no value
    def message_validation(self, message='', secondary=None):
        dialog = Gtk.MessageDialog(self.window_main, Gtk.DialogFlags.MODAL,
                                             Gtk.MessageType.INFO, Gtk.ButtonsType.OK_CANCEL,
                                             message)
        if secondary != None:
            dialog.format_secondary_text(secondary)
        answer = dialog.run()
        dialog.destroy()
        return answer
            
    #defines the status update
    def status(self, status):
        self.statusbar.push(self.context_id, status)














def __init__(self):  
    self.show_all()
    

