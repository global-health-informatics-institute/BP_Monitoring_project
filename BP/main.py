import RPi.GPIO as GPIO
import time
import mysql.connector as mysql
import serial
import hashlib
import threading
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button
from datetime import date

Window.size = (480, 800)

db = mysql.connect(
    host="127.0.0.1",
    user="ghii",
    passwd="",
    database="Hypertension"
)
cur = db.cursor()
flag = 1
flag2 = 0

class MainWindow(Screen):
    pass


class ScanWindow(Screen):
    today = date.today()

    def callback(self):

        name = self.manager.get_screen("Scan").ids["textFocus"].text
        val = name.split('~')
        print(len(val))
        print(val)
        if len(val) == 12:
            firstname = val[6]
            funame = firstname.replace(',', ' ')
            lastname = val[4]
            fname = funame + " " + lastname
            N_id = val[5]

            pBP = ""
            pBP2 = ""
            pBP3 = ""
            pBP4 = ""

            gender = str(val[8]).upper()                            

            DOB = val[9]

            # Hash National id
            National_id = str(N_id).encode("ASCII")
            d = hashlib.sha3_256(National_id)
            N_idHash = d.hexdigest()
            N_idHash2 = ""
            # Calculate Age

            dateOfBirth = str(DOB).split(" ")
            day = dateOfBirth[0] 
            year = dateOfBirth[2]
            mon = dateOfBirth[1]

            month = int()

            if mon.upper() == "JAN":
                month = 1

            elif mon.upper() == "FEB":
                month = 2

            elif mon.upper() == "MAR":
                month = 3

            elif mon.upper() == "APR":
                month = 4

            elif mon.upper() == "MAY":
                month = 5

            elif mon.upper() == "JUN":
                month = 6

            elif mon.upper() == "JUL":
                month = 7

            elif mon.upper() == "AUG":
                month = 8

            elif mon.upper() == "SEP":
                month = 9

            elif mon.upper() == "OCT":
                month = 10

            elif mon.upper() == "NOV":
                month = 11

            elif mon.upper() == "DEC":
                month = 12

            birthDate = date(int(year), month, int(day))
            age = self.today.year - birthDate.year - (
                    (self.today.month, self.today.day) < (birthDate.month, birthDate.day))

            dob = year + "-" + str(month) + "-" + day

            cur.execute("SELECT * FROM Demographic WHERE national_id=%s", [N_idHash])
            record = cur.fetchall()
            if record:
                for rec in record:
                    N_idHash2 = rec[0]
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
                            self.manager.get_screen("Patient_Details").ids["N_id"].text = "ID: " + str(N_id)
                            self.manager.get_screen("Patient_Details").ids["N_id"].opacity = 0
                            self.manager.get_screen("Patient_Details").ids["f_name"].text = str(fname)
                            self.manager.get_screen("Patient_Details").ids["dob"].text = str(age) + " Years"
                            self.manager.get_screen("Patient_Details").ids["pBP"].text = ""
                            self.manager.get_screen("Patient_Details").ids["timeStamp"].text = ""
                            self.manager.transition.direction = "left"
                            self.parent.current = "Patient_Details"

                            if str(gender) == "MALE":
                                self.manager.get_screen("Patient_Details").ids["gender"].source = "images/male.png"
                            else:
                                self.manager.get_screen("Patient_Details").ids["gender"].source = "images/female.png"
                        else:
                            pBP = current_BPsys + "/" + current_BPdia
                            self.manager.get_screen("Patient_Details").ids["N_id"].text = "ID: " + str(N_id)
                            self.manager.get_screen("Patient_Details").ids["N_id"].opacity = 0
                            self.manager.get_screen("Patient_Details").ids["f_name"].text = str(fname)
                            self.manager.get_screen("Patient_Details").ids["dob"].text = str(age) + " Years"
                            self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            self.manager.get_screen("Patient_Details").ids["timeStamp"].text = date1
                            self.manager.transition.direction = "left"
                            self.parent.current = "Patient_Details"

                            if str(gender) == "MALE":
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
                    self.manager.get_screen("Patient_Details").ids["N_id"].text = "ID: " + str(N_id)
                    self.manager.get_screen("Patient_Details").ids["N_id"].opacity = 0
                    self.manager.get_screen("Patient_Details").ids["f_name"].text = str(fname)
                    self.manager.get_screen("Patient_Details").ids["dob"].text = str(age) + " Years"
                    self.manager.get_screen("Patient_Details").ids["pBP"].text = ""
                    self.manager.get_screen("Patient_Details").ids["timeStamp"].text = ""
                    self.manager.transition.direction = "left"
                    self.parent.current = "Patient_Details"

                    if str(gender) == "MALE":
                        self.manager.get_screen("Patient_Details").ids["gender"].source = "images/male.png"
                    else:
                        self.manager.get_screen("Patient_Details").ids["gender"].source = "images/female.png"

            else:
                cur.execute("INSERT INTO Demographic (national_id, Full_name, Gender, DOB) VALUES (%s, %s, %s, %s) ",
                            (N_idHash, fname, gen, dob))
                db.commit()
                self.manager.get_screen("Patient_Details").ids["N_id"].text = "ID: " + str(N_id)
                self.manager.get_screen("Patient_Details").ids["N_id"].opacity = 0
                self.manager.get_screen("Patient_Details").ids["f_name"].text = str(fname)
                self.manager.get_screen("Patient_Details").ids["dob"].text = str(age) + " Years"
                self.manager.get_screen("Patient_Details").ids["pBP"].text = ""
                self.manager.get_screen("Patient_Details").ids["timeStamp"].text = ""
                self.manager.transition.direction = "left"
                self.parent.current = "Patient_Details"

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
        #print("starting Timer")
        nid = str(self.manager.get_screen("Patient_Details").ids["N_id"].text).split(" ")
        N_idHash = nid[1]
        N_id2 = ""
        National_id = str(N_idHash).encode("ASCII")
        d = hashlib.sha3_256(National_id)
        N_id = d.hexdigest()
        cur.execute("SELECT id FROM Demographic WHERE national_id= %s ", [N_id])
        recs = cur.fetchall()
        for rec in recs:
            N_id2 = rec[0]

        serialPort = serial.Serial("/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_D-if00-port0",
                                   baudrate=9600, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE)
        serialData = ""
        bp = ""
        dia_mmHg = int()
        sys_mmHg = int()
        BP_cart = ""
        m = True
        
#        def timerStart():
#            global timer
#            print("Starting Timer")
#            timer = threading.Timer(5, check_port)
#            timer.start()
        
#        counter = 0
#        while counter < 80: #true
        def check_port():
#            timerStart()
            global timer
            timer = threading.Timer(5, check_port)
            timer.start()
            
            if serialPort.inWaiting() > 0:
                #timer = threading.Timer(5, check_port)
                #timer.start
                #timer starts here
#                timerStart()
                #set off flag2 = 1
                serialData = serialPort.readall()
                print(serialData)
                data = str(serialData.decode('ASCII'))
                BP = list(data)
                if len(data) == 10:
                    dia_mmHg = int(BP[4] + BP[5], 16)
                    x = int(BP[2] + BP[3], 16)
                    sys_mmHg = dia_mmHg + x

                    if (sys_mmHg in range(1, 119)) and (dia_mmHg in range(1, 79)):
#                        timer.cancel()
                        BP_cart = "Normal"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id2, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        compose_response()
                        check_comment(N_id2, current_BPsys, current_BPdia, current_BP_cart)

                    elif (sys_mmHg in range(1, 119)) or (dia_mmHg in range(80, 89)):
#                        timer.cancel()
                        BP_cart = "Hypertension_Stage1"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id2, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        compose_response()
                        check_comment(N_id2, current_BPsys, current_BPdia, current_BP_cart)

                    elif (sys_mmHg in range(1, 119)) or (dia_mmHg in range(90, 120)):
#                        timer.cancel()
                        BP_cart = "Hypertension_Stage2"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id2, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        compose_response()
                        check_comment(N_id2, current_BPsys, current_BPdia, current_BP_cart)

                    elif (sys_mmHg in range(1, 119)) or dia_mmHg > 120:
#                        timer.cancel()
                        BP_cart = "Hypertensive_crisis"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id2, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        compose_response()
                        check_comment(N_id2, current_BPsys, current_BPdia, current_BP_cart)
                        
                    elif (sys_mmHg in range(120, 129)) and (dia_mmHg in range(1, 79)):
#                        timer.cancel()
                        BP_cart = "Elevated"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id2, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        compose_response()
                        check_comment(N_id2, current_BPsys, current_BPdia, current_BP_cart)

                    elif (sys_mmHg in range(120, 129)) or (dia_mmHg in range(80, 89)):
#                        timer.cancel()
                        BP_cart = "Hypertension_Stage1"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id2, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        compose_response()
                        check_comment(N_id2, current_BPsys, current_BPdia, current_BP_cart)
                        
                    elif (sys_mmHg in range(120, 129)) or (dia_mmHg in range(90, 119)):
#                        timer.cancel()
                        BP_cart = "Hypertension_Stage2"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id2, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        compose_response()
                        check_comment(N_id2, current_BPsys, current_BPdia, current_BP_cart)
                        
                    elif (sys_mmHg in range(120, 129)) or dia_mmHg > 120:
#                        timer.cancel()
                        BP_cart = "Hypertensive_crisis"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id2, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        self.compose_response()
                        self.check_comment(N_id2, current_BPsys, current_BPdia, current_BP_cart)
                        
                    elif (sys_mmHg in range(130, 139)) or (dia_mmHg in range(81, 89)):
#                        timer.cancel()
                        BP_cart = "Hypertension_Stage1"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id2, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        compose_response()
                        check_comment(N_id2, current_BPsys, current_BPdia, current_BP_cart)
                        
                    elif (sys_mmHg in range(130, 139)) or (dia_mmHg in range(90, 119)):
#                        timer.cancel()
                        BP_cart = "Hypertension_Stage2"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id2, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        compose_response()
                        check_comment(N_id2, current_BPsys, current_BPdia, current_BP_cart)
                        
                    elif (sys_mmHg in range(130, 139)) or dia_mmHg > 120:
#                        timer.cancel()
                        BP_cart = "Hypertensive_crisis"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id2, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        compose_response()
                        check_comment(N_id2, current_BPsys, current_BPdia, current_BP_cart)
                        
                    elif (sys_mmHg in range(140, 180)) or (dia_mmHg in range(90, 120)):
#                        timer.cancel()
                        BP_cart = "Hypertension_Stage2"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id2, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        compose_response()
                        check_comment(N_id2, current_BPsys, current_BPdia, current_BP_cart)
                        
                    elif (sys_mmHg in range(140, 180)) or dia_mmHg > 120:
#                        timer.cancel()
                        BP_cart = "Hypertensive_crisis"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id2, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        compose_response()
                        check_comment(N_id2, current_BPsys, current_BPdia, current_BP_cart)
                        
                    elif (sys_mmHg > 180) or (dia_mmHg > 120):
#                        timer.cancel()
                        BP_cart = "Hypertensive_crisis"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id2, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        compose_response()
                        check_comment(N_id2, current_BPsys, current_BPdia, current_BP_cart)
                        
                    else:
                        bp = "Error..Try Again"
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        self.manager.get_screen("Patient_Details").ids["comment"].text = ""
                        self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0
                        timer.cancel()
            
#            else:
#                print("listening")
                
        check_port()
        
        def compose_response():
            cur.execute("SELECT id FROM vitals LIMIT 0,1")
            rows = cur.fetchall()
            N_id = ""
            N_id2 = ""
            current_BPsys = int()
            current_BPdia = int()
            current_BP_cart = ""
            previous_BPsys = int()
            previous_BPdia = int()
            previous_BP_cart = ""

            for row in rows:
                nid = str(self.manager.get_screen("Patient_Details").ids["N_id"].text).split(" ")
                N_idHash = nid[1]

                National_id = str(N_idHash).encode("ASCII")
                d = hashlib.sha3_256(National_id)
                N_id = d.hexdigest()

                cur.execute("SELECT id FROM Demographic WHERE national_id= %s", [N_id])
                recs = cur.fetchall()
                for rec in recs:
                    N_id2 = rec[0]

            cur.execute("SELECT sys_mmHg, dia_mmHg, BP_cart  FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 0,1",
                        [N_id2])
            rows = cur.fetchall()

            recommendation = ""
            comment = ""
            bp = ""
            pBP = ""

            for row in rows:
                current_BPsys = int(row[0])
                current_BPdia = int(row[1])
                current_BP_cart = row[2]

            # Response
            if current_BPsys > 1 and current_BPdia > 1:

                if (current_BPsys < 120) and (current_BPdia < 80):
                    recommendation = str(current_BPsys) + "/" + str(
                        current_BPdia) + " " + "[Normal]"
                    self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation
                    check_comment(self, N_id2, current_BPsys, current_BPdia, current_BP_cart)

                elif (current_BPsys < 120) or (current_BPdia in range(80, 89)):
                    recommendation = str(current_BPsys) + "/" + str(
                        current_BPdia) + "" + "[Hypertension(1)]"
                    self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation
                    check_comment(self, N_id2, current_BPsys, current_BPdia, current_BP_cart)

                elif (current_BPsys < 120) or (current_BPdia in range(90, 119)):
                    recommendation = str(current_BPsys) + "/" + str(
                        current_BPdia) + "" + "[Hypertension(2)]"
                    self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation
                    check_comment(self, N_id2, current_BPsys, current_BPdia, current_BP_cart)

                elif (current_BPsys < 120) or (current_BPdia > 120):
                    recommendation = str(current_BPsys) + "/" + str(
                        current_BPdia) + "" + "[Hypertension Crisis]"
                    self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation
                    check_comment(self, N_id2, current_BPsys, current_BPdia, current_BP_cart)

                elif (current_BPsys in range(120, 129)) and (current_BPdia < 80):
                    recommendation = str(current_BPsys) + "/" + str(
                        current_BPdia) + "" + "[Elevated]"
                    self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation
                    check_comment(self, N_id2, current_BPsys, current_BPdia, current_BP_cart)

                elif (current_BPsys in range(120, 129)) or (current_BPdia in range(80, 89)):
                    recommendation = str(current_BPsys) + "/" + str(
                        current_BPdia) + "" + "[Hypertension(1)]"
                    self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation
                    check_comment(self, N_id2, current_BPsys, current_BPdia, current_BP_cart)

                elif (current_BPsys in range(120, 129)) or (current_BPdia in range(90, 119)):
                    recommendation = str(current_BPsys) + "/" + str(
                        current_BPdia) + "" + "[Hypertension(2)]"
                    self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation
                    check_comment(self, N_id2, current_BPsys, current_BPdia, current_BP_cart)

                elif (current_BPsys in range(120, 129)) or (current_BPdia > 120):
                    recommendation = str(current_BPsys) + "/" + str(
                        current_BPdia) + "" + "[Hypertension Crisis]"
                    self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation
                    check_comment(self, N_id2, current_BPsys, current_BPdia, current_BP_cart)

                elif (current_BPsys in range(130, 139)) or (current_BPdia in range(80, 89)):
                    recommendation = str(current_BPsys) + "/" + str(
                        current_BPdia) + " [Hypertension(1)]"
                    self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation
                    check_comment(self, N_id2, current_BPsys, current_BPdia, current_BP_cart)

                elif (current_BPsys in range(130, 139)) or (current_BPdia in range(90, 120)):
                    recommendation = str(current_BPsys) + "/" + str(
                        current_BPdia) + " [Hypertension(2)]"
                    self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation
                    check_comment(self, N_id2, current_BPsys, current_BPdia, current_BP_cart)

                elif (current_BPsys in range(130, 139)) or current_BPdia > 120:
                    recommendation = str(current_BPsys) + "/" + str(
                        current_BPdia) + " [Hypertension Crisis]"
                    self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation
                    check_comment(self, N_id2, current_BPsys, current_BPdia, current_BP_cart)

                elif (current_BPsys in range(140, 180)) or (current_BPdia in range(90, 120)):
                    recommendation = str(current_BPsys) + "/" + str(
                        current_BPdia) + " [Hypertension(2)]"
                    self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation
                    check_comment(self, N_id2, current_BPsys, current_BPdia, current_BP_cart)

                elif (current_BPsys in range(140, 180)) or current_BPdia > 120:
                    recommendation = str(current_BPsys) + "/" + str(
                        current_BPdia) + " [Hypertension Crisis]"
                    self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation
                    self.manager.get_screen("Patient_Details").ids["bpValue"].color = (1, 0, 0, 1)
                    check_comment(self, N_id2, current_BPsys, current_BPdia, current_BP_cart)

                elif (current_BPsys > 180) or (current_BPdia > 120):
                    recommendation = str(current_BPsys) + "/" + str(
                        current_BPdia) + " [Hypertension Crisis]"
                    self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation
                    self.manager.get_screen("Patient_Details").ids["bpValue"].color = (1, 0, 0, 1)
                    check_comment(self, N_id2, current_BPsys, current_BPdia, current_BP_cart)
                else:
                    pass

            else:
                pass
                # recommendation = "Error!!!! Please start again the process!!!"
                # self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation
                # self.manager.get_screen("Response").ids["response"].font_size = 27
                # self.manager.get_screen("Response").ids["response"].bold = True
                # return 0

            # Comparison
        
        def check_comment(self, N_id2, current_BPsys, current_BPdia, current_BP_cart):
            cur.execute("SELECT sys_mmHg, dia_mmHg, BP_cart FROM vitals WHERE id = %s ORDER BY time_stamp DESC LIMIT 1,1",
                        [N_id2])
            rows = cur.fetchall()
            if rows:
                for row in rows:
                    if len(str(row[0])) < 1 or len(str(row[1])) < 1:
                        pass
                    else:
                        previous_BPsys = int(row[0])
                        previous_BPdia = int(row[1])
                        previous_BP_cart = row[2]

                        print(previous_BPsys)
                        print(previous_BPdia)
                        print(previous_BP_cart)
                        print(current_BPsys)
                        print(current_BPdia)
                        print(current_BP_cart)
                        if previous_BPsys > 1 and previous_BPdia > 1:

                            if (current_BP_cart == "Normal") and (previous_BP_cart == "Normal"):
                                comment = " After comparing current with previous BP," + "  " + "your BP is ok "
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            elif (current_BP_cart == "Normal") and (previous_BP_cart == "Elevated"):
                                comment = " After comparing current with previous BP," + " " + "your BP has improved"
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            elif (current_BP_cart == "Normal") and (previous_BP_cart == "Hypertension_Stage1"):
                                comment = " After comparing current with previous BP," + " " + " your BP has improved"
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            elif (current_BP_cart == "Normal") and (previous_BP_cart == "Hypertension_Stage2"):
                                comment = " After comparing current with previous BP," + " " + " your BP has improved"
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            elif (current_BP_cart == "Normal") and (previous_BP_cart == "Hypertensive_crisis"):
                                comment = " After comparing current with previous BP," + " " + " your BP has improved"
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            # 1

                            elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Normal"):
                                comment = " After comparing current with previous BP," + " " + " your BP is slightly elevated"
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Elevated"):
                                comment = " After comparing current with previous BP," + " " + " has not changed"
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Hypertension_Stage1"):
                                comment = " After comparing current with previous BP," + " " + " your BP has improved"
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Hypertension_Stage2"):
                                comment = " After comparing current with previous BP," + " " + " your BP has improved"
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Hypertensive_crisis"):
                                comment = " After comparing current with previous BP," + " " + " your BP has improved"
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            # 2

                            elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Normal"):
                                comment = " After comparing current with previous BP," + " " + " you have high blood pressure (Hypertension_Stage1)"
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Elevated"):
                                comment = " After comparing current with previous BP," + " " + " your BP is now High (Hypertension_Stage1)."
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Hypertension_Stage1"):
                                comment = " After comparing current with previous BP," + " " + " your BP has not improved."
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Hypertension_Stage2"):
                                comment = " After comparing current with previous BP," + " " + " your BP has improved but continue the procedures the doctor advised you"
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Hypertensive_crisis"):
                                comment = " After comparing current with previous BP," + " " + " your BP has greatly improved." + " " + " Continue the procedures the doctors advised you"
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            # 3

                            elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Normal"):
                                comment = " After comparing current with previous BP," + " " + " you have high blood pressure (Hypertension_Stage2). "
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Elevated"):
                                comment = " After comparing current with previous BP," + " " + " your BP is now High (Hypertension_Stage2)."
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Hypertension_Stage1"):
                                comment = " After comparing current with previous BP, " + " " + "your BP is now High (Hypertension_Stage1)."
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Hypertension_Stage2"):
                                comment = " After comparing current with previous BP," + " " + " your BP has not improved."
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Hypertensive_crisis"):
                                comment = " After comparing current with previous BP," + " " + " your BP has improved." + " " + " Continue the procedures the doctors advised you"
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            # 4

                            elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Normal"):
                                comment = " Visit a doctor now"
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
                                self.manager.get_screen("Patient_Details").ids["comment"].color = (1, 0, 0, 1)
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Elevated"):
                                comment = " Visit a doctor now"
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
                                self.manager.get_screen("Patient_Details").ids["comment"].color = (1, 0, 0, 1)
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Hypertension_Stage1"):
                                comment = "Visit a doctor now"
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
                                self.manager.get_screen("Patient_Details").ids["comment"].color = (1, 0, 0, 1)
#                                self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Hypertension_Stage2"):
                                comment = "Visit a doctor now"
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
                                self.manager.get_screen("Patient_Details").ids["comment"].color = (1, 0, 0, 1)                               
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Hypertensive_crisis"):
                                comment = " After comparing current with previous BP," + " " + " your BP is not improving. Visit a doctor now"
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
                                self.manager.get_screen("Patient_Details").ids["comment"].color = (1, 0, 0, 1)
                                self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
                                self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
                                self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

                            else:
                                comment = ""
                                self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        else:
                            comment = ""
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment
            else:
                comment = "Data recorded"
                self.manager.get_screen("Patient_Details").ids["comment"].text = comment
                
        
#        counter = counter + 1
#        print(counter)
#        time.sleep(0.5)
#        if flag == 1:\
#           timerStart()
#            flag = 0
#            if flag2 == 0:
#                if sys_mmHg > 0 or dia_mmHg > 0:
#                    print("strange")
#                    self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
#                    self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
#                    self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
#                    self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0
#
#                elif sys_mmHg == 0 or dia_mmHg == 0:
#                    print("== 0")
#                    print(sys_mmHg)
#                    print(dia_mmHg)
#                    self.manager.get_screen("Patient_Details").ids[
#                        "lblText"].opacity = 1
#                    self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
#                    self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
#                    self.manager.get_screen("Patient_Details").ids[
#                        "lblText"].text = "Timeout/Error!!!..Press take BP button to capture BP"
#
#                else:
#                    print("else")
#                    print(sys_mmHg)
#                    print(dia_mmHg)
#                    self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
#                    self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
#                    self.manager.get_screen("Patient_Details").ids[
#                        "lblText"].text = "Timeout/Error!!!..Press take BP button to capture BP"
#                    self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 1

#        def leave():
#            self.manager.get_screen("Patient_Details").ids["bpValue"].text = "Waiting for BP vitals..."
#            self.manager.get_screen("Patient_Details").ids["restart"].opacity = 0
#            self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 0
#            self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 1
#            self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
#            self.manager.get_screen("Patient_Details").ids["comment"].text = ""
#            self.manager.get_screen("Patient_Details").ids["pBP"].text = ""
#            self.manager.get_screen("Patient_Details").ids["pBP2"].text = ""
#            self.manager.get_screen("Patient_Details").ids["pBP3"].text = ""
#            self.manager.get_screen("Patient_Details").ids["pBP4"].text = ""
#            self.manager.get_screen("Patient_Details").ids["timeStamp"].text = ""
#            self.manager.get_screen("Patient_Details").ids["timeStamp2"].text = ""
#            self.manager.get_screen("Patient_Details").ids["timeStamp3"].text = ""
#            self.manager.get_screen("Patient_Details").ids["timeStamp4"].text = ""
#            self.manager.get_screen("Patient_Details").ids["bpValue"].color = (0, 0, 0, 1)
#            self.manager.get_screen("Patient_Details").ids["bpValue"].color = (0, 0, 0, 1)
            
    
        

class Manager(ScreenManager):
    pass


class MyApp(App):
    def build(self):
        Window.clearcolor = (248 / 255, 247 / 255, 255 / 255, 1)
        Window.fullscreen = 'auto'
        return Manager()


if __name__ == "__main__":
    MyApp().run()
