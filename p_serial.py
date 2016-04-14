import serial
import serial.tools.list_ports

class SerialLink(serial.Serial):
    #init the class with the parent class constructor
    def __init__(self):
        serial.Serial.__init__(self)
    
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
        list_all_ports = serial.tools.list_ports.comports()
        list_port = []
        #for each port, get its adress and append it to the list_port list
        for tup in list_all_ports:
            list_port.append(tup[0])
        return list_port
    #This returns a list of the baudrates available (for the settings menu construction)
    def get_baudrates(self):
        tupl_baud = (300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200)
        return tupl_baud
