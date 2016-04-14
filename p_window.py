import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

#definition of main program window
class Window:
    #Init function
    #construct the main window
    #connects the widget to the function they need
    def __init__(self):
        #construct the window from the glade file
        interface = Gtk.Builder()
        interface.add_from_file('fenetre_projecteur.glade')
        
        #attach the main and settings window to their program objects
        self.window_main = interface.get_object('windowMain')
        self.window_settings = interface.get_object('windowSettings')
        self.window_file = interface.get_object('windowFile')
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

        #creates a context id for the status bar
        self.context_id = self.statusbar.get_context_id('status')
    
        #Connect signals from interface (mostly buttons clicks)
        interface.connect_signals(self)
        
    #construct the port list
    #self.update_port_list()

    self.port.set_model(self.listPort)
    self.cell = Gtk.CellRendererText()
    self.port.pack_start(self.cell, True)
    self.port.add_attribute(self.cell, 'text', 1)
    self.port.set_active(self.activePort)
    
    #construct the baudrate list
    self.update_baudrate_list()
    
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
    
    #sets the cfg values from a serial object
    def set_serial_cfg(self, serial):
        
    #defines/update the list of available ports
    def update_port_list(self):
        lp = serial_get_ports()
        self.list_port = Gtk.ListStore(int, str)
        self.active_port = 0
        i = 0
        for port in lp:
            self.list_port.append([i, port])
            if cfg.port == port:
                self.active_port = i
            i += 1
    
    #defines/update the list of availables baudrates
    def update_baudrate_list(self):
        self.list_baud = Gtk.ListStore(int)
        self.active_baudrate = 0
        i = 0
        for baudrate in tupl_baud:
            self.list_baud.append([baudrate])
            if cfg.baudrate == baudrate:
                self.active_baudrate = i
            i += 1
            
    #Defines the close/quit function for the main window
    def on_quit(self, widget):
        Gtk.main_quit()
    
    #defines the function for opening file
    def on_open(self, widget):
        self.window_file.show()
    
    #defines the function for closing file
    def on_close(self, widget):
        return
        answer = self.message_validation("Fermer l'image", 'Tous les reglages seront perdus')
        if answer == -5:
            close_file()
    
    #defines the function for preferences
    def on_settings(self, widget):
        self.window_settings.show()
    
    #defines the function for connect
    def on_connect(self, widget):
        #try to connect to the board
        if ser.isOpen():
            self.message_erreur('Vous etes deja connecte')
            return
        try:
            ser.open()
            self.status('Connecte a %s' %ser.port)
        #else catch an exception and display an error message
        except serial.SerialException:
            self.message_erreur('Erreur de connexion',
                               'Verifiez la connexion et/ou les parametres de connexion')
    
    #defines the function for disconnect
    def on_disconnect(self, widget):
        ser.close()
        self.status('deconnecte')
    
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
    def on_button_scan_clicked(self, widget):
        self.update_port_list()
    
    #defines a function that stop delete events to don't kill the object
    #needed as without it, closing the window from the cross or using "escape"
    #will kill the object, and so it won't be reachable at next call
    def on_delete_event(self, widget, event):
        widget.hide()
        return True
    
    #defines the function for validating settings
    def on_settings_ok_clicked(self, widget):
        cfg.save()
        self.window_ettings.hide()
        
    #defines the function for cancelling settings
    def on_settings_cancel_clicked(self, widget):
        self.window_settings.hide()
    
    #defines the function for validating opening file
    def on_file_ok_clicked(self, widget):
        if openFile(self.window_file.get_filename()):
            self.window_file.hide()
    
    #defines the function for cancelling openning file
    def on_file_cancel_clicked(self, widget):
        self.window_file.hide()
    
    def on_window_file_key_press_event(self, widget, event):
        if event.keyval == Gdk.KEY_Return:
            self.on_file_ok_clicked(widget)
        
    def on_dialog_close(self, widget):
        self.window_file.hide()
    
    #defines the basic error message
    def message_erreur(self, message='', secondary=None):
        dialog = Gtk.MessageDialog(self.windowMain, Gtk.DialogFlags.MODAL,
                                          Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                                          message)
        if secondary != None:
            dialog.format_secondary_text(secondary)
        dialog.run()
        dialog.destroy()
    
    def message_validation(self, message='', secondary=None):
        dialog = Gtk.MessageDialog(self.windowMain, Gtk.DialogFlags.MODAL,
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
