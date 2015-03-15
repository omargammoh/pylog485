
#just experimenting with pymodbus
from pymodbus.client.sync import ModbusSerialClient as MSC
from pymodbus.transaction import ModbusRtuFramer

client = MSC(port='COM3' ,method='rtu', baudrate=9600, stopbits=1
            ,bytesize=8, parity='N'
             ,retries=1000, rtscts=True,framer=ModbusRtuFramer, timeout = 1.0)
client.connect()

from time import time

for i in range(20):
    t1 = time()
    reg = client.read_input_registers(0,unit=12)
    print 'G =%s ' %reg.registers

    reg = client.read_input_registers(1,unit=12)
    print "Tcell = %s" %(reg.registers[0]*0.1-25)
    t2 = time()
    print "%s s" %(t2-t1)


client.close()
