#!/usr/bin/python3.4

# p_serial.py
# This is part of the laser-projector project, that commands a laser projector
# for printing images on UV sensible surfaces, like cyanotypes, dichromate gum, etc.
#
# This part of the program deals with the UART connection.
# Once init from a config file (read by p_config.py), it can list ports on demand,
# send (files) to the arduino board, listening at xon:xoff signal.

import serial
from serial.tools import list_ports
from time import sleep, time


class SerialLink(serial.Serial):
    '''Handle the serial object. Define methods for sending data from image data buffer.'''
    #class attributes
    im = None
    jsp = None
    wm = None
    #init the class with the parent class constructor
    def __init__(self):
        """Init the serial object. Set flags, attributes to initial values."""
        serial.Serial.__init__(self)
        #holds incommings byte till a newl line char.
        self.raw_data = ""
        #flags sent by GUI.
        self.calibrate_flag = 0
        self.send_flag = 0
        self.pause_flag = 0
        self.stop_flag = 0
        #set when there is a new line of data available?
        self.data_flag = 0
        #set when the projector asks for data.
        self.send_ok_flag = 1
        #set when the projector asks again for the last line.
        self.send_again_flag = 0
        #keeps track of the data type received.
        self.data_type = 'json'
        #counter index used in loops.
        self.i = 0
       
       
    #init the instance of the class with values comming from the config file
    #values are passed trough a dictionnary
    def init_from_cfg(self, cfg):
        """Init the serial from dictionary construct by config object."""
        self.port = cfg['port']
        self.baudrate = cfg['baudrate']
        self.bytesize = cfg['bytesize']
        self.parity = cfg['parity']
        self.stopbits = cfg['stopbits']
        self.timeout = cfg['timeout']
        self.xonxoff = cfg['xonxoff']
        
    #This lists the ports available
    def get_ports(self):
        """Get available ports. Construct a list that is used by GUI."""
        #creates a list of the ports available
        list_all_ports = list_ports.comports()
        list_port = []
        #for each port, get its adress and append it to the list_port list
        for tup in list_all_ports:
            list_port.append(tup[0])
        return list_port
    #This returns a list of the baudrates available (for the settings menu construction)
    def get_baudrates(self):
        """Create a list containing available baudrates."""
        #TODO: try greater speed: 230400, 250000, 460800, 500000.
        tupl_baud = (300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200)
        return tupl_baud
    
    #This function sends the calibration string when the flag is on
    def send_calibration(self):
        """Send the calibration buffer values.
        Send buffer in a loop, as long as the flag is set.
        Handle start and end of operation (laser from and to zero).
        """
        if self.calibrate_flag == 0:
            return 0
        #If the board hasn't asked for datas
        if self.send_ok_flag == 0:
            return
        
        string_to_send = SerialLink.im.calibration_buffer[self.i]
        
        #If flag == 2, the calibration ends: last instruction is stop the laser
        if self.calibrate_flag == 2:
            string_to_send = SerialLink.im.calibration_buffer[5]
            self.i = 0
            self.calibrate_flag = 0
                
        #Try to write the file to the serial, else handle a serial exception,
        #exit calibration, close port and display a message.
        try:
            self.write(string_to_send)
        except serial.SerialException:
            SerialLink.wm.toolbutton_calibrate.set_active(0)
            SerialLink.wm.message_erreur('Le port a été déconnecté',
                                   'Vérifiez la connexion au projecteur')
            self.calibrate_flag = 0
            self.i = 0
            self.close()
            return 1
        else:
            SerialLink.wm.debug_append('>>> ' + string_to_send)
            self.send_ok_flag = 0   
            
        
        #Only if we are in a normal iteration (i.e. not stopping), increment self.i
        if self.calibrate_flag == 1:
            self.i += 1
        #If end of calibration buffer, loop to start
        if self.i > 4:
            self.i = 1
        #Used in the main loop: squeeze following main loop is set to 1
        return 1
    
    #This function sends the data to the board when the flag is on
    def send_data(self,):
        """Send data to projector.
        Verifies flags states.
        Write string to buffer, update GUI.
        Handle serial exceptions.
        Re-init flags state when finished.
        """
        #Look for wanted state.
        if self.send_flag == 0:
            return
        elif self.pause_flag == 1:
            return
        #If stop flag, re-init for next send.
        elif self.stop_flag == 1:
            self.i = 0
            self.send_flag = 0
            self.stop_flag = 0
            self.send_ok_flag = 1
            SerialLink.wm.set_gui_group('send', True);
            SerialLink.wm.progress_total.hide();
            return
        
        #If no data is asked by projector, return.
        #if self.send_ok_flag == 0:
            #return
        
        #First iteration: some things to set.
        if self.i == 0:
            self.start_time = time()
            SerialLink.wm.set_gui_group('send', False);
            SerialLink.wm.progress_total.show();
        
        string_to_send = SerialLink.im.data_buffer[self.i]
        #self.flush()
        self.write(string_to_send.encode('utf-8'))
        #print(string_to_send)
        
        self.send_ok_flag = 0
        self.i += 1
        
        if self.i >= SerialLink.im.pix_qty:
            sending_time = time()-self.start_time
            self.i = 0
            self.send_flag = 0
            self.send_ok_flag = 1
            SerialLink.wm.set_gui_group('send', True);
            SerialLink.wm.progress_total.hide();
            SerialLink.wm.message_info("Image insolée en %.3fs."%sending_time)
            
            

    
    def send_cfg(self, var, value):
        """Send a configuration value to the board."""
        string_to_send = '$%s:%s\n'%(var, value)
        self.write(string_to_send.encode('utf-8'))
            
            
    #This function reads raw data from the board
    def read_data(self):
        """Read data comming from the serial.
        Check serial state.
        Read data. Handle format error.
        Set flags, update progress, print ot GUI, according to what is received.
        """
        if not self.is_open:
            return
        nb_byte = self.in_waiting
        if nb_byte == 0:
            return
        
        for i in range(nb_byte):
            raw_byte = self.read()
            if raw_byte == b'$':
                self.data_type = 'cfg'
            if raw_byte == b'{':
                self.data_type = 'json'
            
            if raw_byte == b'\n':
                self.data_flag = 1
                return
            else:
                self.raw_data += raw_byte.decode('utf-8', errors='ignore')

    def parse_data(self):
        """Parse data received.
        Send to json parser, then dispatch information here and there.
        """
        #dont' do anything if the data_flag is not set.
        if self.data_flag == 0:
            return
        else:
            self.data_flag = 0
        
        if self.data_type == 'json':
            #send raw data to and get values pairs from the json parser.
            data = SerialLink.jsp.from_json(self.raw_data)
            self.raw_data = ""
            print(data)
            
            #Stop working if the data is not well formated.
            if type(data) is not dict:
                SerialLink.wm.status('Erreur de valeur')
                return
            
            #Look if there is a send flag.
            send_flag = data.get('send')
            if send_flag == 1:
                self.send_ok_flag = 1
            #elif send_flag == 2:
                #self.send_again_flag = 1
                #self.send_ok_flag = 1
                #SerialLink.wm.status('Coordonnée envoyée à nouveau')
                
            #progress = data.get('per')
            #if progress != None:
                #percent = progress/SerialLink.im.pix_qty
                #SerialLink.wm.progress_total.set_text('Insolation image: %2d%%'%(percent))
                #SerialLink.wm.progress_total.set_fraction(percent)
    
            message = data.get('message')
            if message != None:
                SerialLink.wm.status(message)
                
            #erreur = data.get('erreur')
            #if erreur != None:
                #print(erreur)
        else:
            print(self.raw_data)
            data = self.raw_data.lstrip('$')
            self.raw_data = ''
            if data == 's':
                self.send_ok_flag = 1
                
            
