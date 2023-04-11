import RPi.GPIO as GPIO
import sys
import time
import mysql.connector as mysql
import serial
import hashlib
import threading
from kivy.app import App
from kivy.clock import mainthread, Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button
from datetime import date
from _thread import interrupt_main
import json
import pycurl
from io import BytesIO
from configparser import ConfigParser

from urllib.parse import urlencode, unquote
import pycurl
from io import BytesIO

from nat_id import Parse_NID
from db_actions import data_control
# from BP.pers_data import sendSms
import setts as settings
from bp_checker import Check_BP
from pers_data import Pers_data

Window.size = (480, 800)

flag = 1
flag2 = 0
config = ConfigParser()

# def initialize_settings():
#     settings = {}
#     with open("conn.config") as json_file:
#         settings = json.load(json_file)
#     return settings
settings = settings.initialize_settings()
URL = settings["url"]

db = mysql.connect(
    host=settings["database"]["host"],
    user = settings["database"]["user"],
    passwd= settings["database"]["passwd"],
    database= settings["database"]["database"]
)
cur = db.cursor()

class MainWindow(Screen):
    pass


class ScanWindow(Screen):
    today = date.today()

    def callback(self):
        pID = Parse_NID()
        actions = data_control()
        global val
        name = self.manager.get_screen("Scan").ids["textFocus"].text
        val = pID.parse_national_id(name)
        act = actions.BP1(name)
        # val = name.split('~')
        print(len(val))
        print(val)
        if len(val) == 7:
            global fname
            fname = val["first_name"] + " " + val["middle_name"] + " " + val["last_name"]
            pBP = ""
            pBP2 = ""
            pBP3 = ""
            pBP4 = ""
            
            if(val["gender"] == "MALE"):
                n_gender = 1
            else:
                n_gender = 0
                

            # DOB = val["dob"]

            # Hash National id
            National_id = str(val["nation_id"]).encode("ASCII")
            d = hashlib.sha3_256(National_id)
            N_idHash = d.hexdigest()
            N_idHash2 = ""

            age = self.today.year - val["dob"].year - (
                    (self.today.month, self.today.day) < (val["dob"].month, val["dob"].day))

            dob = val["dob"]

            # self.manager.get_screen("Patient_Details").ids["N_id"].text = "ID: " + str(val["nation_id"])
            # self.manager.get_screen("Patient_Details").ids["N_id"].opacity = 0
            # self.manager.get_screen("Patient_Details").ids["f_name"].text = str(fname)
            # self.manager.get_screen("Patient_Details").ids["dob"].text = str(age) + " Years"
            # self.manager.get_screen("Patient_Details").ids["pBP"].text = act["text"]
            # self.manager.get_screen("Patient_Details").ids["timeStamp"].text = act["date"]
            # self.manager.transition.direction = "left"
            # self.parent.current = "Patient_Details"

            # if str(val["gender"]) == "MALE":
            #     self.manager.get_screen("Patient_Details").ids["gender"].source = "images/male.png"
            # else:
            #     self.manager.get_screen("Patient_Details").ids["gender"].source = "images/female.png"

            cur.execute("SELECT * FROM Demographic WHERE Full_name=%s", [val["first_name"]+val["middle_name"]+val["last_name"]])
            record = cur.fetchall()
            if record:
                for rec in record:
                    N_idHash2 = rec[0]
                
                # @BP 1
                cur.execute(
                    "SELECT sys_mmHg, dia_mmHg, time_stamp  FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 0,1",
                    [N_idHash2])
                rows = cur.fetchall()
                if rows:
                    for row in rows:
                        current_BPsys = str(row[0])
                        current_BPdia = str(row[1])
                        timeStamp = str(row[2]).split(" ")
                        date1 = timeStamp[0]
                        if len(current_BPsys) < 1 or len(current_BPdia) < 1:
                            self.manager.get_screen("Patient_Details").ids["N_id"].text = "ID: " + str(val["nation_id"])
                            self.manager.get_screen("Patient_Details").ids["N_id"].opacity = 0
                            self.manager.get_screen("Patient_Details").ids["f_name"].text = str(fname)
                            self.manager.get_screen("Patient_Details").ids["dob"].text = str(age) + " Years"
                            self.manager.get_screen("Patient_Details").ids["pBP"].text = ""
                            self.manager.get_screen("Patient_Details").ids["timeStamp"].text = ""
                            self.manager.transition.direction = "left"
                            self.parent.current = "Patient_Details"

                            if str(val["gender"]) == "MALE":
                                self.manager.get_screen("Patient_Details").ids["gender"].source = "images/male.png"
                            else:
                                self.manager.get_screen("Patient_Details").ids["gender"].source = "images/female.png"
                        else:
                            pBP = current_BPsys + "/" + current_BPdia
                            self.manager.get_screen("Patient_Details").ids["N_id"].text = "ID: " + str(val["nation_id"])
                            self.manager.get_screen("Patient_Details").ids["N_id"].opacity = 0
                            self.manager.get_screen("Patient_Details").ids["f_name"].text = str(fname)
                            self.manager.get_screen("Patient_Details").ids["dob"].text = str(age) + " Years"
                            self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            self.manager.get_screen("Patient_Details").ids["timeStamp"].text = date1
                            self.manager.transition.direction = "left"
                            self.parent.current = "Patient_Details"

                            if str(val["gender"]) == "MALE":
                                self.manager.get_screen("Patient_Details").ids["gender"].source = "images/male.png"
                            else:
                                self.manager.get_screen("Patient_Details").ids["gender"].source = "images/female.png"

                            # @BP 2
                            cur.execute(
                                "SELECT sys_mmHg, dia_mmHg, time_stamp  FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 1,1",
                                [N_idHash2])
                            rows2 = cur.fetchall()
                            if rows2:
                                for row2 in rows2:
                                    previous_BPsys2 = str(row2[0])
                                    previous_BPdia2 = str(row2[1])
                                    timeStamp2 = str(row2[2]).split(" ")
                                    date2 = timeStamp2[0]

                                    if len(previous_BPsys2) < 1 or len(previous_BPdia2) < 1:
                                        self.manager.get_screen("Patient_Details").ids["pBP2"].text = ""
                                        self.manager.get_screen("Patient_Details").ids["timeStamp2"].text = ""
                                    else:
                                        pBP2 = previous_BPsys2 + "/" + previous_BPdia2
                                        self.manager.get_screen("Patient_Details").ids["pBP2"].text = pBP2
                                        self.manager.get_screen("Patient_Details").ids["timeStamp2"].text = date2

                                        # @BP 3
                                        cur.execute(
                                            "SELECT sys_mmHg, dia_mmHg, time_stamp  FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 2,1",
                                            [N_idHash2])
                                        rows3 = cur.fetchall()
                                        if rows3:
                                            for row3 in rows3:
                                                previous_BPsys3 = str(row3[0])
                                                previous_BPdia3 = str(row3[1])
                                                timeStamp3 = str(row3[2]).split(" ")
                                                date3 = timeStamp3[0]
                                                if len(previous_BPsys3) < 1 or len(previous_BPdia3) < 1:
                                                    self.manager.get_screen("Patient_Details").ids["pBP3"].text = ""
                                                    self.manager.get_screen("Patient_Details").ids[
                                                        "timeStamp3"].text = ""

                                                else:
                                                    pBP3 = previous_BPsys3 + "/" + previous_BPdia3
                                                    self.manager.get_screen("Patient_Details").ids["pBP3"].text = pBP3
                                                    self.manager.get_screen("Patient_Details").ids[
                                                        "timeStamp3"].text = date3

                                                    # @BP 4
                                                    cur.execute(
                                                        "SELECT sys_mmHg, dia_mmHg, time_stamp  FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 3,1",
                                                        [N_idHash2])
                                                    rows4 = cur.fetchall()
                                                    if rows4:
                                                        for row4 in rows4:
                                                            previous_BPsys4 = str(row4[0])
                                                            previous_BPdia4 = str(row4[1])
                                                            timeStamp4 = str(row4[2]).split(" ")
                                                            date4 = timeStamp4[0]
                                                            if len(previous_BPsys4) < 1 or len(previous_BPdia4) < 1:
                                                                self.manager.get_screen("Patient_Details").ids[
                                                                    "pBP4"].text = ""
                                                                self.manager.get_screen("Patient_Details").ids[
                                                                    "timeStamp4"].text = ""

                                                            else:
                                                                pBP4 = previous_BPsys4 + "/" + previous_BPdia4
                                                                self.manager.get_screen("Patient_Details").ids[
                                                                    "pBP4"].text = pBP4
                                                                self.manager.get_screen("Patient_Details").ids[
                                                                    "timeStamp4"].text = date4

                                                    else:
                                                        self.manager.get_screen("Patient_Details").ids["pBP4"].text = ""
                                                        self.manager.get_screen("Patient_Details").ids[
                                                            "timeStamp4"].text = ""
                                        else:
                                            self.manager.get_screen("Patient_Details").ids["pBP3"].text = ""
                                            self.manager.get_screen("Patient_Details").ids["timeStamp3"].text = ""
                            else:
                                self.manager.get_screen("Patient_Details").ids["pBP2"].text = ""
                                self.manager.get_screen("Patient_Details").ids["timeStamp2"].text = ""

                else:
                    self.manager.get_screen("Patient_Details").ids["N_id"].text = "ID: " + str(val["nation_id"])
                    self.manager.get_screen("Patient_Details").ids["N_id"].opacity = 0
                    self.manager.get_screen("Patient_Details").ids["f_name"].text = str(fname)
                    self.manager.get_screen("Patient_Details").ids["dob"].text = str(age) + " Years"
                    self.manager.get_screen("Patient_Details").ids["pBP"].text = ""
                    self.manager.get_screen("Patient_Details").ids["timeStamp"].text = ""
                    self.manager.transition.direction = "left"
                    self.parent.current = "Patient_Details"

                    if str(val["gender"]) == "MALE":
                        self.manager.get_screen("Patient_Details").ids["gender"].source = "images/male.png"
                    else:
                        self.manager.get_screen("Patient_Details").ids["gender"].source = "images/female.png"

            else:
                cur.execute("INSERT INTO Demographic (national_id, Full_name, Gender, DOB) VALUES (%s, %s, %s, %s) ",
                            (N_idHash, fname, n_gender, dob))
                db.commit()
                self.manager.get_screen("Patient_Details").ids["N_id"].text = "ID: " + str(val["nation_id"])
                self.manager.get_screen("Patient_Details").ids["N_id"].opacity = 0
                self.manager.get_screen("Patient_Details").ids["f_name"].text = str(fname)
                self.manager.get_screen("Patient_Details").ids["dob"].text = str(age) + " Years"
                self.manager.get_screen("Patient_Details").ids["pBP"].text = ""
                self.manager.get_screen("Patient_Details").ids["timeStamp"].text = ""
                self.manager.transition.direction = "left"
                self.parent.current = "Patient_Details"

                if str(val["gender"]) == "MALE":
                    self.manager.get_screen("Patient_Details").ids["gender"].source = "images/male.png"
                else:
                    self.manager.get_screen("Patient_Details").ids["gender"].source = "images/female.png"

        else:

            self.parent.current = "Scan"
            self.manager.get_screen("Scan").ids["textFocus"].text = " "
            self.manager.get_screen("Scan").ids["textFocus"].focus = True

    def enter(self):
        self.manager.get_screen("Scan").ids["textFocus"].text = " "
        self.manager.get_screen("Scan").ids["textFocus"].focus = True

    def On_LED(self):
        self.do_nothing()
        LED_PIN = 6
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.output(LED_PIN, GPIO.HIGH)

    def Off_LED(self):
        self.do_nothing()
        LED_PIN = 6
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.output(LED_PIN, GPIO.LOW)

    def do_nothing(self):
        pass


class PatientDetails(Screen):
    def regenerate(self):
        N_id2 = ""
        nid = str(self.manager.get_screen("Patient_Details").ids["N_id"].text).split(" ")
        N_idHash = nid[1]

        National_id = str(N_idHash).encode("ASCII")
        d = hashlib.sha3_256(National_id)
        N_id = d.hexdigest()

        cur.execute("SELECT id FROM Demographic WHERE national_id= %s ", [N_id])
        recs = cur.fetchall()
        for rec in recs:
            N_id2 = rec[0]
        cur.execute(
            "SELECT sys_mmHg, dia_mmHg, time_stamp  FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 0,1",
            [N_id2])
        rows = cur.fetchall()
        if rows:
            for row in rows:
                current_BPsys = str(row[0])
                current_BPdia = str(row[1])
                timeStamp = str(row[2]).split(" ")
                pdate = timeStamp[0]
                if len(current_BPsys) < 1 or len(current_BPdia) < 1:
                    self.manager.get_screen("Patient_Details").ids["pBP"].text = ""
                    self.manager.get_screen("Patient_Details").ids["timeStamp"].text = ""

                else:
                    pBP = current_BPsys + "/" + current_BPdia
                    self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                    self.manager.get_screen("Patient_Details").ids["timeStamp"].text = pdate

                    # @pBP 2
                    cur.execute(
                        "SELECT sys_mmHg, dia_mmHg, time_stamp  FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 1,1",
                        [N_id2])
                    rows2 = cur.fetchall()
                    if rows2:
                        for row2 in rows2:
                            previous_BPsys2 = str(row2[0])
                            previous_BPdia2 = str(row2[1])
                            timeStamp2 = str(row2[2]).split(" ")
                            date2 = timeStamp2[0]
                            if len(previous_BPsys2) < 1 or len(previous_BPdia2) < 1:
                                self.manager.get_screen("Patient_Details").ids["pBP2"].text = ""
                                self.manager.get_screen("Patient_Details").ids["timeStamp2"].text = ""

                            else:
                                pBP2 = previous_BPsys2 + "/" + previous_BPdia2
                                self.manager.get_screen("Patient_Details").ids["pBP2"].text = pBP2
                                self.manager.get_screen("Patient_Details").ids["timeStamp2"].text = date2

                                # @pBP 3
                                cur.execute(
                                    "SELECT sys_mmHg, dia_mmHg, time_stamp  FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 2,1",
                                    [N_id2])
                                rows3 = cur.fetchall()
                                if rows3:
                                    for row3 in rows3:
                                        previous_BPsys3 = str(row3[0])
                                        previous_BPdia3 = str(row3[1])
                                        timeStamp3 = str(row3[2]).split(" ")
                                        date3 = timeStamp3[0]
                                        if len(previous_BPsys3) < 1 or len(previous_BPdia3) < 1:
                                            self.manager.get_screen("Patient_Details").ids["pBP3"].text = ""
                                            self.manager.get_screen("Patient_Details").ids["timeStamp3"].text = ""

                                        else:
                                            pBP3 = previous_BPsys3 + "/" + previous_BPdia3
                                            self.manager.get_screen("Patient_Details").ids["pBP3"].text = pBP3
                                            self.manager.get_screen("Patient_Details").ids["timeStamp3"].text = date3

                                        # @pBP 4
                                        cur.execute(
                                            "SELECT sys_mmHg, dia_mmHg, time_stamp  FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 3,1",
                                            [N_id2])
                                        rows4 = cur.fetchall()
                                        if rows4:
                                            for row4 in rows4:
                                                previous_BPsys4 = str(row4[0])
                                                previous_BPdia4 = str(row4[1])
                                                timeStamp4 = str(row4[2]).split(" ")
                                                date4 = timeStamp4[0]
                                                if len(previous_BPsys4) < 1 or len(previous_BPdia4) < 1:
                                                    self.manager.get_screen("Patient_Details").ids["pBP4"].text = ""
                                                    self.manager.get_screen("Patient_Details").ids[
                                                        "timeStamp4"].text = ""

                                                else:
                                                    pBP4 = previous_BPsys4 + "/" + previous_BPdia4
                                                    self.manager.get_screen("Patient_Details").ids["pBP4"].text = pBP4
                                                    self.manager.get_screen("Patient_Details").ids[
                                                        "timeStamp4"].text = date4

                                        else:
                                            self.manager.get_screen("Patient_Details").ids["pBP4"].text = ""
                                            self.manager.get_screen("Patient_Details").ids["timeStamp4"].text = ""
                                else:
                                    self.manager.get_screen("Patient_Details").ids["pBP3"].text = ""
                                    self.manager.get_screen("Patient_Details").ids["timeStamp3"].text = ""

                    else:
                        self.manager.get_screen("Patient_Details").ids["pBP2"].text = ""
                        self.manager.get_screen("Patient_Details").ids["timeStamp2"].text = ""
        else:

            self.manager.get_screen("Patient_Details").ids["pBP"].text = ""
            self.manager.get_screen("Patient_Details").ids["timeStamp"].text = ""

        self.manager.get_screen("Patient_Details").ids["bpValue"].text = "Waiting for BP vitals..."
        self.manager.get_screen("Patient_Details").ids["restart"].opacity = 0
        self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 0
        self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 1
        self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
        self.manager.get_screen("Patient_Details").ids["comment"].text = ""
        Clock.schedule_once(self.generate_BP, 1)

    def generate_BP(self, *args):
        global timer
        nid = str(self.manager.get_screen("Patient_Details").ids["N_id"].text).split(" ")
        

        serialPort = serial.Serial(settings["BP"]["bp_port"],
                                    settings["BP"]["baudrate"],
                                    settings["BP"]["bytesize"],
                                    timeout= 1,
                                    stopbits= serial.STOPBITS_ONE)

        def check_data():
            global timer
            timer = threading.Timer(5, check_data)
            timer.start()
            if serialPort.inWaiting() > 0:
                serialData = serialPort.readall()
                print(serialData)
                timer.cancel()
                data = str(serialData.decode('ASCII'))
                check = Check_BP()
                c_BP = check.check_port(data, nid)
                # act = actions.BP1(nid, data)

                cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                            (c_BP["N_id2"], c_BP["sys_mmHg"], c_BP["dia_mmHg"], c_BP["BP_cart"]))
                db.commit()
                self.manager.get_screen("Patient_Details").ids["bpValue"].text = c_BP["bp"]
                self.manager.get_screen("Patient_Details").ids["bpValue"].text = c_BP["recommendation"]
                self.manager.get_screen("Patient_Details").ids["bpValue"].opacity = 1
                self.manager.get_screen("Patient_Details").ids["comment"].text = c_BP["comment"]
                # self.compose_response()
                Pers_data().smsmode(c_BP["N_id2"], c_BP["bp"], c_BP["BP_cart"],
                                    fname, val["gender"], val["printable_dob"])
                self.buttons()

        check_data()
    
    # tracing back to main thread
    #this is set for all major graphical changes
    @mainthread
    def buttons(self):
        self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
        self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
        self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

class Manager(ScreenManager):
    pass


class MyApp(App):
    def build(self):
        Window.clearcolor = (248 / 255, 247 / 255, 255 / 255, 1)
        Window.fullscreen = 'auto'
        return Manager()


if __name__ == "__main__":
    MyApp().run()