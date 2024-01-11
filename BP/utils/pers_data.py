from datetime import date
import hashlib, serial, json, pycurl
import time
from kivy.app import App
from kivy.clock import mainthread, Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button
import mysql.connector as mysql

def initialize_settings():
    settings = {}
    with open("/home/pi/BP_Monitoring_project/BP/utils/conn.config") as json_file:
        settings = json.load(json_file)
    return settings

settings = initialize_settings()
URL = settings["url"]

db = mysql.connect(
    host=settings["database"]["host"],
    user = settings["database"]["user"],
    passwd= settings["database"]["passwd"],
    database= settings["database"]["database"]
)

cur = db.cursor()

class Pers_data:
    
    def smsmode(self, bp, BP_cart, fname, gender, dob, hex_id, p_rate):
        ser_port = serial.Serial(settings["gsm"]["id"],
                            settings["gsm"]["baudrate"],
                            timeout= 0.5)

        checkAT = 'AT\r'
        ser_port.write(checkAT.encode())
        mes = ser_port.read(64)
        time.sleep(5)
        print(mes)
        
        cur.execute("SELECT * from vitals WHERE status = 0")
        rows = cur.fetchall()
        for row in rows:
            N_idU = row[6]
            
        if b'AT\r\r\nOK\r\n' in mes:
            print("success")
            cur.execute("UPDATE vitals SET status = 1 WHERE national_id = %s", [N_idU])
            db.commit()
            print("db updated")
        else:
            print("unsuccessful")
            

        stres = 'AT+CMGF=1\r'
        ser_port.write(stres.encode())
        # msg = ser_port.read(64)
        time.sleep(0.1)

        # cmd3 = 'AT+CMGF=1\r'
        # ser_port.write(cmd3.encode())
        # msg = ser_port.read(64)
        # time.sleep(0.1)
        
        # cmd1 = 'AT+CMGS=\r'
        cmd1 = 'AT+CMGS="'+settings["server_number"]+'"\r'
        print(settings["server_number"])
        ser_port.write(cmd1.encode())
        msg = ser_port.read(64)
        time.sleep(5)
        # print(msg)

        response = str(bp) + "|" + BP_cart + "|" + fname + "|" + gender + "|" + dob +  "|" + hex_id + "|" + str(p_rate) +'\r'
        
        ser_port.write(str.encode(response))
        msgout = ser_port.read(1000)
        time.sleep(0.1)
        print(msgout)
        
        ser_port.write(str.encode("\x1A"))
        read_port = ser_port.read(5)
   
        print("response sent")
        return response

    

           

                    
