import serial
import time 

ser_port = serial.Serial("/dev/ttyUSB1", 115200, timeout=1)

cmd = "AT\r\n"
ser_port.write(cmd.encode())
msg = ser_port.read(64)
time.sleep(0.1)
print (msg)