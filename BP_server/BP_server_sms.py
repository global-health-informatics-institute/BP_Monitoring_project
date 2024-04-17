import time
import serial
import mysql.connector as mysql
from configparser import ConfigParser
import json


def initialize_settings():
    settings = {}
    with open("/home/pi/BP_Monitoring_project/BP_server/conn.config") as json_file:
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
    cur.execute("INSERT INTO smsload (n_id, vitals, bp_cat, fullname, gender, dob, nat_id, p_rate)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (splitdata[0], splitdata[1], splitdata[2], splitdata[3], splitdata[4], splitdata[5], splitdata[6], splitdata[7]))
    db.commit()
    print("sent to database")

def acknowledgement(patient_name):
    responses = []
    outgoingmsg = "vitals received for " + patient_name
    responses.append(outgoingmsg)
    print("this is responses: ", responses)
    
    cmd = 'AT+CMGF=1\r'
    ser_port.write(cmd.encode())
    msg = ser_port.read(64)
    time.sleep(0.1)

    cmd1 = 'AT+CMGS="'+settings["client_number"]+'"\r'
    ser_port.write(cmd.encode())
    msg = ser_port.read(64)
    time.sleep(0.1)

    
    for i in responses:
        ser_port.write(str.encode(i))
        msgout = ser_port.read(1000)
        time.sleep(0.1)
        print("this is msgout in i loop: ", msgout)
        print("response sent")
        time.sleep(5)

def textmode():
    print("staring textmode")
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
        print("Starting loop: ", a)
        seperator = '|'
        sep = seperator.encode()
        if sep in element:
            ele = element.decode()
            print(ele)
            parseSms(ele)
            splitdata = ele.split(seperator)

            delcom = 'AT+CMGD=1,4\r'
            ser_port.write(delcom.encode())
            delmsg = ser_port.read(64)
            print(delmsg)
            time.sleep(5)
            print("All deleted")

            acknowledgement(splitdata[3])
    
            
while True:
    textmode()
    
