from datetime import date
import hashlib, serial, json, pycurl
import time
from kivy.app import App
from kivy.clock import mainthread, Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button

def initialize_settings():
    settings = {}
    with open("conn.config") as json_file:
        settings = json.load(json_file)
    return settings

settings = initialize_settings()
URL = settings["url"]

class Pers_data:
    
    def smsmode(self, N_id, bp, BP_cart, fname, gender, dob):
        ser_port = serial.Serial(settings["gsm"]["id"],
                            settings["gsm"]["baudrate"],
                            timeout= 0.5)

        checkAT = 'AT\r'
        ser_port.write(checkAT.encode())
        mes = ser_port.read(64)
        time.sleep(5)
        print(mes)

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
        ser_port.write(cmd1.encode())
        msg = ser_port.read(64)
        time.sleep(5)
        # print(msg)

        response = str(N_id) + "|" + str(bp) + "|" + BP_cart + "|" + fname + "|" + gender + "|" + dob + '\r'
        
        ser_port.write(str.encode(response))
        msgout = ser_port.read(1000)
        time.sleep(0.1)
        print(msgout)

        ser_port.write(str.encode("\x1A"))
        read_port = ser_port.read(5)

        print("response sent")
        return response

    

           

                    
