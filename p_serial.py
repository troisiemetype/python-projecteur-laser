# p_serial.py
# This is part of the laser-projector project, that commands a laser projector
# for printing images on UV sensible surfaces, like cyanotypes, dichromate gum, etc.
#
# This part of the program deals with the UART connection.
# Once init from a config file (read by p_config.py), it can list ports on demand,
# send (files) to the arduino board, listening at xon:xoff signal.

import serial
from serial.tools import list_ports

#needed for transforming strings to bytes
import array

class SerialLink(serial.Serial):
    #class attributes
    im = None
    jsp = None
    wm = None
    #init the class with the parent class constructor
    def __init__(self):
        serial.Serial.__init__(self)
        self.im = None
        self.jsp = None
        self.wm = None
        self.calibrate_flag = 0
        self.send_flag = 0
        self.pause_flag = 0
        self.stop_flag = 0
        self.data_flag = 0
        self.send_ok_flag = 1
        self.i = 0
    
    #init the instance of the class with values comming from the config file
    #values are passed trough a dictionnary
    def init_from_cfg(self, cfg):
        self.port = cfg['port']
        self.baudrate = cfg['baudrate']
        self.bytesize = cfg['bytesize']
        self.parity = cfg['parity']
        self.stopbits = cfg['stopbits']
        self.timeout = cfg['timeout']
        self.xonxoff = cfg['xonxoff']
        
    #This lists the ports available
    def get_ports(self):
        #creates a list of the ports available
        list_all_ports = list_ports.comports()
        list_port = []
        #for each port, get its adress and append it to the list_port list
        for tup in list_all_ports:
            list_port.append(tup[0])
        return list_port
    #This returns a list of the baudrates available (for the settings menu construction)
    def get_baudrates(self):
        tupl_baud = (300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200)
        return tupl_baud
    
    #This function sends the calibration string when the flag is on
    def send_calibration(self):
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
            
        byte_to_send = array.array('u', string_to_send)
        
        #Try to write the file to the serial, else handle a serial exception,
        #exit calibration, close port and display a message.
        try:
            self.write(string_to_send.encode('utf-8'))
            SerialLink.wm.debug_append('>>> ' + string_to_send)
            self.send_ok_flag = 0
        except serial.SerialException:
            SerialLink.wm.toolbutton_calibrate.set_active(0)
            SerialLink.wm.message_erreur('Le port a été déconnecté',
                                   'Vérifiez la connexion au projecteur')
            self.calibrate_flag = 0
            self.i = 0
            self.close()
            return 1
        
        #Only if we are in a normal iteration (i.e. not stopping), increment self.i
        if self.calibrate_flag == 1:
            self.i += 1
        #If end of calibration buffer, loop to start
        if self.i > 4:
            self.i = 1
        #Used in the main loop: squeeze following main loop is set to 1
        return 1
    
    #This function sends the data to the board when the flag is on
    def send_data(self):
        #Don't do anything if the send flag is not set.
        if self.send_flag == 0:
            return
        #If the pause falg is set, don't do neither
        if self.pause_flag == 1:
            return
        #If the board hasn't asked for datas
        if self.send_ok_flag == 0:
            return
        string_to_send = SerialLink.im.data_buffer[self.i]
      
        SerialLink.wm.debug_append('>>> ' + string_to_send)
        
        self.i += 1
        
        try:
            self.write(string_to_send.encode('utf-8'))
            SerialLink.wm.debug_append('>>> ' + string_to_send)
            self.send_ok_flag = 0
        except serial.SerialException:
            SerialLink.wm.message_erreur('Le port a été déconnecté',
                                   'Vérifiez la connexion au projecteur')
            self.data_flag = 0
            self.i = 0
            self.close()
            return 1
        except serial.SerialTimeoutException:
            print('timeout')
            return 1
             
        if self.i >= len(SerialLink.im.data_buffer):
            self.send_flag = 0
            self.i = 0
        if self.stop_flag == 1:
            self.i = 0
            self.send_flag = 0
            self.stop_flag = 0
            
    #This function reads raw data from the board
    def read_data(self):
        if not self.is_open:
            return
        if self.in_waiting == 0:
            return
        
        data = {}
        raw_data = self.readline()
        data = SerialLink.jsp.from_json(raw_data.decode('utf-8'))
        #TODO: handle error raised by the json parser.
        if type(data) is not dict:
            print('erreur transmise')
            return
            
        send_flag = data.get('send')
        if send_flag == 1:
            self.send_ok_flag = 1
            
        progress = data.get('progress')
        if progress != None:
            SerialLink.wm.progress_step.set_fraction(progress)
            SerialLink.wm.progress_total.set_fraction(data.get('ID')/SerialLink.im.pix_qty)

        message = data.get('message')
        if message != None:
            print(message)
        