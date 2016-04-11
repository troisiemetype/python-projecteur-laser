#!/usr/bin/python3.4

#imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

#definition of main program window
class winMain:
    #Init function
    #construct the main window
    #connects the widget to the function they need
    def __init__(self):
        #construct the window from the glade file
        interface = Gtk.Builder()
        interface.add_from_file('fenetre_projecteur.glade')
        
        self.windowSettings = interface.get_object('windowSettings')
        
        interface.connect_signals(self)
        
        
    def on_mainWindow_destroy(self, widget):
        Gtk.main_quit()
        
    def on_menuQuit_activate(self, widget):
        Gtk.main_quit()
    
    def on_menuOpen_activate(self, widget):
        pass
    
    def on_menuClose_activate(self, widget):
        pass
    
    def on_menuSettings_activate(self, widget):
        self.windowSettings.show()
        
    def on_settingsOK_clicked(self, widget):
        self.windowSettings.hide()
        
    def on_settingsCancel_clicked(self, widget):
        self.windowSettings.hide()
        


if __name__ == "__main__":
    wm = winMain()
    Gtk.main()