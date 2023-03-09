from datetime import date, time
import hashlib, serial, json, pycurl
# from io import BytesIO
# from main import PatientDetails
from bp_checker import Check_BP
from nat_id import Parse_NID
from db_actions import data_control
import time

def initialize_settings():
    settings = {}
    with open("conn.config") as json_file:
        settings = json.load(json_file)
    return settings

settings = initialize_settings()
URL = settings["url"]

class Pers_data:
    # def sendSms(self):
    #     pID = Parse_NID()
    #     check = Check_BP()

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

    

            # def wifimode():
            #     try:
            #         b_obj_ = BytesIO()
            #         crl_ = pycurl.Curl()
            #         vital = str(N_id) + "|" + str(c_BP["bp"]) + "|" + c_BP["BP_cart"] + "|" + fname + "|" + val["gender"] + "|" + dob
            #         crl_.setopt(crl_.URL, URL + vital)
            #         crl_.setopt(crl_.WRITEDATA, b_obj_)
            #         crl_.perform()
            #         crl_.close()
            #         get_body_ = b_obj_.getvalue()

            #         print('Output of GET request:\n%s'%get_body_.decode('utf8'))
            #         checkpoint = '|'
            #         checkpoint2 = '!DOCTYPE'
            #         cp = checkpoint.encode()
            #         cp2 = checkpoint2.encode()
            #         if cp in get_body_ or cp2 in get_body_:
            #             print("all good")
            #         else:
            #             print("didnt get return \n sending over sms")
            #             smsmode()
            #     except pycurl.error:
            #         print("we couldnt get through")
            #         smsmode()

            #     return vital

            # wifimode()

                    