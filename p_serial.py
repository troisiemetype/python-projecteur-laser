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
    #init the class with the parent class constructor
    def __init__(self):
        serial.Serial.__init__(self)
        self.im = None
        self.send_flag = 0
        self.pause_flag = 0
        self.data_flag = 0
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
        if self.im.calibration_flag == 0:
            return
        string_to_send = self.im.calibration_buffer[self.i]
        byte_to_send = array.array('u', string_to_send)
        self.write(string_to_send.encode('utf-8'))
        
        self.i += 1
        if self.i > 4:
            self.i = 1
        if self.im.calibration_flag == 2:
            self.write('{"L":0, "mode":0}'.encode())
            self.im.calibration_flag = 0