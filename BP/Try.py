import serial

serialPort = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=0.5, bytesize=8, stopbits=serial.STOPBITS_ONE)

serialData = ""
m = True

while m:
    if serialPort.inWaiting() > 0:
        serialData = serialPort.readall()
        data = str(serialData.decode('ASCII'))
        BP = list(data)
        if len(data) == 10:
            dia_mmHg = int(BP[4] + BP[5], 16)
            x = int(BP[2] + BP[3], 16)
            sys_mmHg = dia_mmHg + x

            print(sys_mmHg)
            print(dia_mmHg)
        m = False

