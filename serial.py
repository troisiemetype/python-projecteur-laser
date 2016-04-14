
import serial
import serial.tools.list_ports

tuplBaud = (300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200)

ser = serial.Serial()




#init the serial link with the values copied from the config file
def serial_init(serial):
    serial.port = cfg.port
    serial.baudrate = cfg.baudrate
    serial.bitsize = cfg.databits
    serial.parity = cfg.parity
    serial.stopbits = cfg.stopbits
    serial.xonxoff = cfg.xonxoff
    serial.timeout = 1

#get a list of the available ports. don't know yet if it's faisible
def serial_get_ports():
    listPortInfo = serial.tools.list_ports.comports()
    listPort = []
    for tup in listPortInfo:
        listPort.append(tup[0])
    return listPort

