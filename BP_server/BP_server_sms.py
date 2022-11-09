import time
import serial
import mysql.connector as mysql
from configparser import ConfigParser
import json



def initialize_settings():
    settings = {}
    with open("conn.config") as json_file:
        settings = json.load(json_file)
    return settings

settings = initialize_settings()

ser_port = serial.Serial(settings["server_gsm"]["id"],
                        settings["server_gsm"]["baudrate"], timeout=0.5)

db = mysql.connect(
    host=settings["server_db"]["host"],
    user = settings["server_db"]["user"],
    passwd= settings["server_db"]["passwd"],
    database= settings["server_db"]["database"]
)
cur = db.cursor()

config = ConfigParser()

def parseSms(ele):
    splitdata = ele.split("|")
    print(splitdata)
    cur.execute("INSERT INTO smsload (n_id, vitals, bp_cat, fullname, gender, dob)"
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (splitdata[0], splitdata[1], splitdata[2], splitdata[3], splitdata[4], splitdata[5]))
    db.commit()
    print("sent to database")

def textmode():
    cmd = 'AT+CMGF=1\r'
    ser_port.write(cmd.encode())
    msg = ser_port.read(64)
    time.sleep(0.1)
            
    readSMS = 'AT+CMGL="ALL"\r\n'
    ser_port.write(str.encode(readSMS))
    time.sleep(5)
    msgread = ser_port.read(64)
    time.sleep(5)

    a = ser_port.readlines()
    for element in a:
        seperator = '|'
        sep = seperator.encode()
        if sep in element:
            ele = element.decode()
            parseSms(ele)
            splitdata = ele.split("|")
            
            cmd = 'AT+CMGF=1\r'
            ser_port.write(cmd.encode())
            msg = ser_port.read(64)
            time.sleep(0.1)
    
            # cmd = 'AT+CMGS=\r'
            cmd1 = 'AT+CMGS="'+settings["client_number"]+'"\r'
            ser_port.write(cmd.encode())
            msg = ser_port.read(64)
            time.sleep(0.1)
    
            outgoingmsg = "vitals received for " + splitdata[3]
            ser_port.write(str.encode(outgoingmsg))
            msgout = ser_port.read(1000)
            time.sleep(0.1)
            print(msgout)
    
            ser_port.write(str.encode("\x1A"))
            read_port = ser_port.read(5)
    
            print("response sent")
            time.sleep(5)
            
            delcom = 'AT+CMGD=1,4\r'
            ser_port.write(delcom.encode())
            delmsg = ser_port.read(64)
            time.sleep(0.1)
            print("All deleted")
            
while True:
    textmode()
            