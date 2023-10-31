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
from kivy.animation import Animation
from datetime import date
from _thread import interrupt_main
import json
import pycurl
from io import BytesIO
from configparser import ConfigParser
import setts as settings
from urllib.parse import urlencode, unquote
import pycurl
from io import BytesIO
import gc

from utils.nat_id import Parse_NID
from utils.bp_checker import Check_BP
from utils.pers_data import Pers_data

from functools import lru_cache

Window.size = (480, 800)

flag = 1
flag2 = 0
config = ConfigParser()

#accessing file with all configuration settings
def initialize_settings():
    settings = {}
    with open("/home/pi/BP_Monitoring_project/BP/conn.config") as json_file:
        settings = json.load(json_file)
    return settings

settings = initialize_settings()
URL = settings["url"]

#establish database connection
db = mysql.connect(
    host=settings["database"]["host"],
    user = settings["database"]["user"],
    passwd= settings["database"]["passwd"],
    database= settings["database"]["database"]
)


class MainWindow(Screen):
    pass


class ScanWindow(Screen):
    gc.collect()
    today = date.today()
    global cur
    cur = db.cursor()
    
    
    #display the 4 most recent bp readings from the corresponding patient history if available
    def displayBP(self, current_BPsys, current_BPdia, fname, age, gender, date, val, num, pr):
        if len(current_BPsys) < 1 or len(current_BPdia) < 1:
            self.manager.get_screen("Patient_Details").ids["N_id"].text = "ID: " + str(val["nation_id"])
            self.manager.get_screen("Patient_Details").ids["N_id"].opacity = 0
            self.manager.get_screen("Patient_Details").ids["f_name"].text = str(fname)
            self.manager.get_screen("Patient_Details").ids["dob"].text = str(age) + " Years"
            self.manager.get_screen("Patient_Details").ids["pBP"+str(num)].text = ""
            self.manager.get_screen("Patient_Details").ids["pr"+str(num)].text = ""
            self.manager.get_screen("Patient_Details").ids["timeStamp"+str(num)].text = ""
            self.manager.transition.direction = "left"
            self.parent.current = "Patient_Details"

            if str(gender) == "MALE":
                self.manager.get_screen("Patient_Details").ids["gender"].source = "images/male.png"
            else:
                self.manager.get_screen("Patient_Details").ids["gender"].source = "images/female.png"
        else:
            pBP = current_BPsys + "/" + current_BPdia
            self.manager.get_screen("Patient_Details").ids["N_id"].text = "ID: " + str(val["nation_id"])
            self.manager.get_screen("Patient_Details").ids["N_id"].opacity = 0
            self.manager.get_screen("Patient_Details").ids["f_name"].text = str(fname)
            self.manager.get_screen("Patient_Details").ids["dob"].text = str(age) + " Years"
            self.manager.get_screen("Patient_Details").ids["pBP"+str(num)].text = pBP
            self.manager.get_screen("Patient_Details").ids["pr"+str(num)].text = pr
            self.manager.get_screen("Patient_Details").ids["timeStamp"+str(num)].text = date
            self.manager.transition.direction = "left"
            self.parent.current = "Patient_Details"

            if str(gender) == "MALE":
                self.manager.get_screen("Patient_Details").ids["gender"].source = "images/male.png"
            else:
                self.manager.get_screen("Patient_Details").ids["gender"].source = "images/female.png"
    
    def callback(self):
        pID = Parse_NID()
        global val
        name = self.manager.get_screen("Scan").ids["textFocus"].text
        val = pID.parse_national_id(name)
        print(val)
        if len(val) == 7:
            global fname
            fname = val["first_name"]+ " " + val["last_name"]

            N_id = val["nation_id"]

            pBP = ""
            pBP2 = ""
            pBP3 = ""
            pBP4 = ""
            gender = val["gender"]
            
            if(gender == "MALE"):
                n_gender = 1
            else:
                n_gender = 0
                

            DOB = val["dob"]

            # Hash National id
            National_id = str(N_id).encode("ASCII")
            d = hashlib.sha3_256(National_id)
            N_idHash = d.hexdigest()
            N_idHash2 = ""
            current_BPsys = ""
            current_BPdia = ""
            date = ""
            pr = ""
            num = 0
            # Calculate Age
            age = self.today.year - val["dob"].year - (
                    (self.today.month, self.today.day) < (val["dob"].month, val["dob"].day))

            dob = val["dob"]

            cur.execute("SELECT * FROM Demographic WHERE national_id=%s", [N_idHash])
            record = cur.fetchall()
            #check if any record in the database matches the ID scanned
            if record:
                for rec in record:
                    N_idHash2 = rec[0]
                    
                # cur.execute(
                    # "SELECT sys_mmHg, dia_mmHg, time_stamp, p_rate FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 4",
                    # [N_idHash2])
                cur.execute(
                    "SELECT sys_mmHg, dia_mmHg, time_stamp, p_rate FROM vitals WHERE national_id= %s ORDER BY time_stamp DESC LIMIT 4",
                    [N_idHash])
                rows = cur.fetchall()
                db.commit()
                num = 0
                if rows:
                    for row in rows:
                        current_BPsys = str(row[0])
                        current_BPdia = str(row[1])
                        timeStamp = str(row[2]).split(" ")
                        date = timeStamp[0]
                        pr = str(row[3])
                        self.displayBP(current_BPsys, current_BPdia, fname, age, gender, date, val, num, pr)
                        num += 1
                        
                else:
                    self.displayBP(current_BPsys, current_BPdia, fname, age, gender, date, val, num, pr)

                        
            #insert patient details in Demographic table if not already available
            else:
                cur.execute("INSERT INTO Demographic (national_id, Full_name, Gender, DOB) VALUES (%s, %s, %s, %s) ",
                            (N_idHash, fname, n_gender, dob))
                db.commit()
                self.displayBP(current_BPsys, current_BPdia, fname, age, gender, date, val, num, pr)

                if str(gender) == "MALE":
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

    #on and off functions for LEDs on scanner
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
    #funtion to process all 4 bp reading in history table
    def showBP(self, current_BPsys, current_BPdia, pdate, num, pr):
        if len(current_BPsys) < 1 or len(current_BPdia) < 1:
            self.manager.get_screen("Patient_Details").ids["pBP"+str(num)].text = ""
            self.manager.get_screen("Patient_Details").ids["timeStamp"+str(num)].text = ""
            self.manager.get_screen("Patient_Details").ids["pr"+str(num)].text = ""
            
        else:
            pBP = current_BPsys + "/" + current_BPdia
            self.manager.get_screen("Patient_Details").ids["pBP"+str(num)].text = pBP
            self.manager.get_screen("Patient_Details").ids["timeStamp"+str(num)].text = pdate
            self.manager.get_screen("Patient_Details").ids["pr"+str(num)].text = pr
    
    #refresh/replace bp history with new additions (after clicking 'take-bp' button)
    def regenerate(self):
        nid = str(self.manager.get_screen("Patient_Details").ids["N_id"].text).split(" ")
        N_idHash = nid[1]
        check = Check_BP()
        comment_box = check.comment_box(nid)

        National_id = str(N_idHash).encode("ASCII")
        d = hashlib.sha3_256(National_id)
        N_id = d.hexdigest()
        print("for line 236 in main this is N_id", N_id)

        # cur.execute("SELECT id FROM Demographic WHERE national_id= %s ", [N_id])
        # recs = cur.fetchall()
        # for rec in recs:
            # N_id2 = rec[0]
        # cur.execute(
            # "SELECT sys_mmHg, dia_mmHg, time_stamp, p_rate FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 4",
            # [N_id2])
        cur.execute(
            "SELECT sys_mmHg, dia_mmHg, time_stamp, p_rate FROM vitals WHERE national_id= %s ORDER BY time_stamp DESC LIMIT 4",
            [N_id])
        rows = cur.fetchall()
        db.commit()
        num = 0
        if rows:
            for row in rows:
                current_BPsys = str(row[0])
                current_BPdia = str(row[1])
                timeStamp = str(row[2]).split(" ")
                pdate = timeStamp[0]
                pr = str(row[3])
                self.showBP(current_BPsys, current_BPdia, pdate, num, pr)
                num += 1
                
        else:
            self.manager.get_screen("Patient_Details").ids["pBP0"].text = ""
            self.manager.get_screen("Patient_Details").ids["timeStamp0"].text = ""

        self.manager.get_screen("Patient_Details").ids["bpValue"].text = "Waiting for BP vitals..."
        self.manager.get_screen("Patient_Details").ids["restart"].opacity = 0
        self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 0
        self.manager.get_screen("Patient_Details").ids["pr"].text = "Waiting for pulse rate..."
        self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 1
        self.manager.get_screen("Patient_Details").ids["lblText"].text = "<-- Press the blue start button on the left"
        self.manager.get_screen("Patient_Details").ids["comment"].text = ""
        Clock.schedule_once(self.generate_BP, 1)
    

    def generate_BP(self, *args):
        global timer, nid
        self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
        nid = str(self.manager.get_screen("Patient_Details").ids["N_id"].text).split(" ")
        serialPort = serial.Serial(settings["BP"]["bp_port"],
                                    settings["BP"]["baudrate"],
                                    settings["BP"]["bytesize"],
                                    timeout= 1,
                                    stopbits= serial.STOPBITS_ONE)
      
        #listening to bp reading on serial port
        def check_data():
            global timer, nid
            timer = threading.Timer(5, check_data)
            timer.start()
            if serialPort.inWaiting() > 0:
                serialData = serialPort.readall()
                timer.cancel()
                data = str(serialData.decode('ASCII'))
                check = Check_BP()
                c_BP = check.check_port(data)
                category = check.category()
                comment_box = check.comment_box(nid[1])
                fetch = check.fetch_cart()
                
                if comment_box["N_id2"] == " ":
                    cur.execute("SELECT id FROM Demographic WHERE national_id= ", [nid])
                    recs = cur.fetchall()
                    for rec in recs:
                        comment_box["N_id2"] = rec[0]
                    db.commit()
                status = 0
                
                if c_BP["sys_mmHg"] != 0 and c_BP["dia_mmHg"] != 0:
                    print("we on line 312")
                    cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart, status, national_id, p_rate) VALUES (%s, %s, %s, %s, %s, %s, %s) ",
                                                (comment_box["N_id2"], c_BP["sys_mmHg"], c_BP["dia_mmHg"], category["BP_cart"], status, comment_box["N_id"], c_BP["p_rate"]))
                    #cur.execute("INSERT INTO vitals (sys_mmHg, dia_mmHg, BP_cart, status, national_id, p_rate) VALUES (%s, %s, %s, %s, %s, %s) ",
                                                #(c_BP["sys_mmHg"], c_BP["dia_mmHg"], category["BP_cart"], status, comment_box["N_id"], c_BP["p_rate"]))
                    
                    # comment_box["N_id2"] =""
                    db.commit()
                    self.finish_off()
                    self.manager.get_screen("Patient_Details").ids["bpValue"].text = category["bp"]
                    self.manager.get_screen("Patient_Details").ids["pr"].text = str(c_BP["p_rate"])
                    self.manager.get_screen("Patient_Details").ids["bpValue"].text = category["recommendation"]
                    self.manager.get_screen("Patient_Details").ids["bpValue"].opacity = 1
                    self.manager.get_screen("Patient_Details").ids["comment"].text = fetch["comment"]
                    Pers_data().smsmode(category["bp"], category["BP_cart"],
                                        fname, val["gender"], val["printable_dob"], comment_box["N_id"], c_BP["p_rate"])
                    self.buttons()
                else:
                    self.manager.get_screen("Patient_Details").ids["bpValue"].text = "Error...try again"
                    self.buttons()
                    timer.cancel()
            
                
                
        check_data()
            
    # tracing back to main thread
    #this is set for all major graphical changes
    @mainthread
    def buttons(self):
        self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
        self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
        self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0
        timer.cancel()

    #leave finish button visible as user waits for bp reading
    @mainthread
    def finish_off(self):
        self.manager.get_screen("Patient_Details").ids["restart"].opacity = 0

    #clear PatientDetails page after clicking finish
    def leave(self):
        self.manager.get_screen("Patient_Details").ids["bpValue"].text = "Waiting for BP vitals..."
        self.manager.get_screen("Patient_Details").ids["restart"].opacity = 0
        self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 0
        self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 1
        self.manager.get_screen("Patient_Details").ids["comment"].text = ""
        self.manager.get_screen("Patient_Details").ids["pBP0"].text = ""
        self.manager.get_screen("Patient_Details").ids["timeStamp0"].text = ""
        self.manager.get_screen("Patient_Details").ids["pr0"].text = ""
        self.manager.get_screen("Patient_Details").ids["pBP1"].text = ""
        self.manager.get_screen("Patient_Details").ids["timeStamp1"].text = ""
        self.manager.get_screen("Patient_Details").ids["pr1"].text = ""
        self.manager.get_screen("Patient_Details").ids["pBP2"].text = ""
        self.manager.get_screen("Patient_Details").ids["timeStamp2"].text = ""
        self.manager.get_screen("Patient_Details").ids["pr2"].text = ""
        self.manager.get_screen("Patient_Details").ids["pBP3"].text = ""
        self.manager.get_screen("Patient_Details").ids["timeStamp3"].text = ""
        self.manager.get_screen("Patient_Details").ids["pr3"].text = ""
        self.manager.get_screen("Patient_Details").ids["pr"].text = "Waiting for pulse rate..."
        
class Manager(ScreenManager):
    pass


class MyApp(App):
    def build(self):
        Window.clearcolor = (248 / 255, 247 / 255, 255 / 255, 1)
    #automate boot to full screen and orient page to vertical
        #Window.fullscreen = 'auto'
        #Window.rotation = -90
        return Manager()


if __name__ == "__main__":
    MyApp().run()

