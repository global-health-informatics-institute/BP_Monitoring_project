import RPi.GPIO as GPIO
# from gpiozero import LED
import time
import mysql.connector as mysql
import serial
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from datetime import date

# import sys, os

Window.size = (480, 800)

db = mysql.connect(
    host="127.0.0.1",
    user="ghii",
    passwd="",
    database="Hypertension"
)
cur = db.cursor()


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

            cur.execute("SELECT * FROM Demographic WHERE id=%s", [N_id])
            record = cur.fetchall()
            if record:
                cur.execute(
                    "SELECT sys_mmHg, dia_mmHg, time_stamp  FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 0,1",
                    [N_id])
                rows = cur.fetchall()
                if rows:
                    for row in rows:
                        current_BPsys = str(row[0])
                        current_BPdia = str(row[1])
                        timeStamp = str(row[2]).split(" ")
                        date1 = timeStamp[0]
                        if len(current_BPsys) < 1 or len(current_BPdia) < 1:
                            self.manager.get_screen("Patient_Details").ids["N_id"].text = "ID: " + str(N_id)
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
                                [N_id])
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
                                            [N_id])
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
                                                        [N_id])
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
                cur.execute("INSERT INTO Demographic (id, Full_name, Gender, DOB) VALUES (%s, %s, %s, %s) ",
                            (N_id, fname, gender, DOB))
                db.commit()
                self.manager.get_screen("Patient_Details").ids["N_id"].text = "ID: " + str(N_id)
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
        # led = LED(6)
        # led.on()
        LED_PIN = 6
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.output(LED_PIN, GPIO.HIGH)

    def Off_LED(self):
        self.do_nothing()
        # led = LED(6)
        # led.off()
        LED_PIN = 6
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.output(LED_PIN, GPIO.LOW)

    def do_nothing(self):
        pass


class PatientDetails(Screen):
    def regenerate(self):
        nid = str(self.manager.get_screen("Patient_Details").ids["N_id"].text).split(" ")
        N_id = nid[1]
        cur.execute(
            "SELECT sys_mmHg, dia_mmHg, time_stamp  FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 0,1",
            [N_id])
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
                        [N_id])
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
                                    [N_id])
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
                                            [N_id])
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
        Clock.schedule_once(self.generate_BP, 5)

    def generate_BP(self, *args):
        nid = str(self.manager.get_screen("Patient_Details").ids["N_id"].text).split(" ")
        N_id = nid[1]
        serialPort = serial.Serial("/dev/ttyUSB0", baudrate=9600, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE)
        serialData = ""
        bp = ""
        dia_mmHg = int()
        sys_mmHg = int()
        BP_cart = ""
        m = True
        counter = 0
        while counter < 60:
            # serialData = serialPort.readall().decode("ASCII")
            # print("wee!!")
            # if serialData == "":
            #     break

            if serialPort.inWaiting() > 0:
                serialData = serialPort.readall()
                data = str(serialData.decode('ASCII'))
                BP = list(data)
                if len(data) == 10:
                    dia_mmHg = int(BP[4] + BP[5], 16)
                    x = int(BP[2] + BP[3], 16)
                    sys_mmHg = dia_mmHg + x

                    if (sys_mmHg in range(1, 119)) and (dia_mmHg in range(1, 79)):
                        BP_cart = "Normal"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        # self.parent.current = "Response"
                        self.compose_response()
                        counter = 60
                        # break

                    elif (sys_mmHg in range(1, 119)) or (dia_mmHg in range(80, 89)):
                        BP_cart = "Hypertension_Stage1"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        # self.parent.current = "Response"
                        self.compose_response()
                        counter = 60
                        # break

                    elif (sys_mmHg in range(1, 119)) or (dia_mmHg in range(90, 120)):
                        BP_cart = "Hypertension_Stage2"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        # self.parent.current = "Response"
                        self.compose_response()
                        counter = 60
                        # break

                    elif (sys_mmHg in range(1, 119)) or dia_mmHg > 120:
                        BP_cart = "Hypertensive_crisis"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        # self.parent.current = "Response"
                        self.compose_response()
                        counter = 60
                        # break

                    elif (sys_mmHg in range(120, 129)) and (dia_mmHg in range(1, 79)):
                        BP_cart = "Elevated"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        # self.parent.current = "Response"
                        self.compose_response()
                        counter = 60
                        # break

                    elif (sys_mmHg in range(120, 129)) or (dia_mmHg in range(80, 89)):
                        BP_cart = "Hypertension_Stage1"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        # self.parent.current = "Response"
                        self.compose_response()
                        counter = 60
                        # break

                    elif (sys_mmHg in range(120, 129)) or (dia_mmHg in range(90, 119)):
                        BP_cart = "Hypertension_Stage2"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        # self.parent.current = "Response"
                        self.compose_response()
                        counter = 60
                        # break

                    elif (sys_mmHg in range(120, 129)) or dia_mmHg > 120:
                        BP_cart = "Hypertensive_crisis"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        # self.parent.current = "Response"
                        self.compose_response()
                        counter = 60
                        # break

                    elif (sys_mmHg in range(130, 139)) or (dia_mmHg in range(81, 89)):
                        BP_cart = "Hypertension_Stage1"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        # self.parent.current = "Response"
                        self.compose_response()
                        counter = 60
                        # break

                    elif (sys_mmHg in range(130, 139)) or (dia_mmHg in range(90, 119)):
                        BP_cart = "Hypertension_Stage2"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        # self.parent.current = "Response"
                        self.compose_response()
                        counter = 60
                        # break

                    elif (sys_mmHg in range(130, 139)) or dia_mmHg > 120:
                        BP_cart = "Hypertensive_crisis"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        # self.parent.current = "Response"
                        self.compose_response()
                        counter = 60
                        # break

                    elif (sys_mmHg in range(140, 180)) or (dia_mmHg in range(90, 120)):
                        BP_cart = "Hypertension_Stage2"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        # self.parent.current = "Response"
                        self.compose_response()
                        counter = 60
                        # break

                    elif (sys_mmHg in range(140, 180)) or dia_mmHg > 120:
                        BP_cart = "Hypertensive_crisis"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        # self.parent.current = "Response"
                        self.compose_response()
                        counter = 60
                        # break

                    elif (sys_mmHg > 180) or (dia_mmHg > 120):
                        BP_cart = "Hypertensive_crisis"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        # self.parent.current = "Response"
                        self.compose_response()
                        counter = 60
                        # break

                    else:
                        # BP_cart = "Error"
                        # cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                        #             (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        # db.commit()
                        # bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        bp = "Error..Try Again"
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        self.manager.get_screen("Patient_Details").ids["comment"].text = ""
                        self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0
                        # self.manager.get_screen("Patient_Details").ids["bpValue"].color = (1, 0, 0, 1)
                        # self.parent.current = "Patient_Details"

                        counter = 60

            counter = counter + 1
            time.sleep(0.5)
        if sys_mmHg > 0 or dia_mmHg > 0:
            self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
            self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
            self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
            self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 0

        elif sys_mmHg == 0 or dia_mmHg == 0:
            print(sys_mmHg)
            print(dia_mmHg)
            self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
            self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
            self.manager.get_screen("Patient_Details").ids[
                "lblText"].text = "BP Error. Press Take BP button to capture Bp"
            self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 1

        else:
            print(sys_mmHg)
            print(dia_mmHg)
            self.manager.get_screen("Patient_Details").ids["restart"].opacity = 1
            self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 1
            self.manager.get_screen("Patient_Details").ids[
                "lblText"].text = "Timeout/Error!!!..Press take BP button to capture BP"
            self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 1

    def enter(self):
        self.manager.get_screen("Patient_Details").ids["bpValue"].text = "Waiting for BP vitals..."
        self.manager.get_screen("Patient_Details").ids["restart"].opacity = 0
        self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 0
        self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 1
        self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 1
        self.manager.get_screen("Patient_Details").ids["lblText"].text = "Press the Blue Round Button"
        # self.manager.get_screen("Patient_Details").ids["pBP"].text = ""

    def leave(self):
        self.manager.get_screen("Patient_Details").ids["bpValue"].text = "Waiting for BP vitals..."
        self.manager.get_screen("Patient_Details").ids["restart"].opacity = 0
        self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 0
        self.manager.get_screen("Patient_Details").ids["lblText"].opacity = 1
        self.manager.get_screen("Patient_Details").ids["comment"].text = ""
        self.manager.get_screen("Patient_Details").ids["pBP"].text = ""

    def compose_response(self):
        cur.execute("SELECT id FROM vitals LIMIT 0,1")
        rows = cur.fetchall()
        N_id = ""
        current_BPsys = int()
        current_BPdia = int()
        current_BP_cart = ""
        previous_BPsys = int()
        previous_BPdia = int()
        previous_BP_cart = ""

        for row in rows:
            nid = str(self.manager.get_screen("Patient_Details").ids["N_id"].text).split(" ")
            N_id = nid[1]

        cur.execute("SELECT sys_mmHg, dia_mmHg, BP_cart  FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 0,1",
                    [N_id])
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
                # recommendation = "Your BP is: " + str(current_BPsys) + "/" + str(
                #     current_BPdia) + "\n\nYour Blood pressure is normal"
                # self.manager.get_screen("Response").ids["response"].text = recommendation
                recommendation = str(current_BPsys) + "/" + str(
                    current_BPdia) + " " + "[Normal]"
                self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation

            elif (current_BPsys < 120) or (current_BPdia in range(80, 89)):
                # recommendation = "Your BP is: " + str(current_BPsys) + "/" + str(
                #     current_BPdia) + "\n\nYour Blood pressure is normal"
                # self.manager.get_screen("Response").ids["response"].text = recommendation
                recommendation = str(current_BPsys) + "/" + str(
                    current_BPdia) + "" + "[Hypertension(1)]"
                self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation

            elif (current_BPsys < 120) or (current_BPdia in range(90, 119)):
                # recommendation = "Your BP is: " + str(current_BPsys) + "/" + str(
                #     current_BPdia) + "\n\nYour Blood pressure is normal"
                # self.manager.get_screen("Response").ids["response"].text = recommendation
                recommendation = str(current_BPsys) + "/" + str(
                    current_BPdia) + "" + "[Hypertension(2)]"
                self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation

            elif (current_BPsys < 120) or (current_BPdia > 120):
                # recommendation = "Your BP is: " + str(current_BPsys) + "/" + str(
                #     current_BPdia) + "\n\nYour Blood pressure is normal"
                # self.manager.get_screen("Response").ids["response"].text = recommendation
                recommendation = str(current_BPsys) + "/" + str(
                    current_BPdia) + "" + "[Hypertension Crisis]"
                self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation

            elif (current_BPsys in range(120, 129)) and (current_BPdia < 80):
                # recommendation = "Your BP is: " + str(current_BPsys) + "/" + str(
                #     current_BPdia) + " \n\nYour BP is normal. Though elevated"
                # self.manager.get_screen("Response").ids["response"].text = recommendation
                recommendation = str(current_BPsys) + "/" + str(
                    current_BPdia) + "" + "[Elevated]"
                self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation

            elif (current_BPsys in range(120, 129)) or (current_BPdia in range(80, 89)):
                # recommendation = "Your BP is: " + str(current_BPsys) + "/" + str(
                #     current_BPdia) + " \n\nYour BP is normal. Though elevated"
                # self.manager.get_screen("Response").ids["response"].text = recommendation
                recommendation = str(current_BPsys) + "/" + str(
                    current_BPdia) + "" + "[Hypertension(1)]"
                self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation

            elif (current_BPsys in range(120, 129)) or (current_BPdia in range(90, 119)):
                # recommendation = "Your BP is: " + str(current_BPsys) + "/" + str(
                #     current_BPdia) + " \n\nYour BP is normal. Though elevated"
                # self.manager.get_screen("Response").ids["response"].text = recommendation
                recommendation = str(current_BPsys) + "/" + str(
                    current_BPdia) + "" + "[Hypertension(2)]"
                self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation

            elif (current_BPsys in range(120, 129)) or (current_BPdia > 120):
                # recommendation = "Your BP is: " + str(current_BPsys) + "/" + str(
                #     current_BPdia) + " \n\nYour BP is normal. Though elevated"
                # self.manager.get_screen("Response").ids["response"].text = recommendation
                recommendation = str(current_BPsys) + "/" + str(
                    current_BPdia) + "" + "[Hypertension Crisis]"
                self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation

            elif (current_BPsys in range(130, 139)) or (current_BPdia in range(80, 89)):
                # recommendation = "Your BP is: " + str(current_BPsys) + "/" + str(
                #     current_BPdia) + " \n\nHigh Blood Pressure..Hypertension( Stage 1)"
                # self.manager.get_screen("Response").ids["response"].text = recommendation
                recommendation = str(current_BPsys) + "/" + str(
                    current_BPdia) + " [Hypertension(1)]"
                self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation

            elif (current_BPsys in range(130, 139)) or (current_BPdia in range(90, 120)):
                # recommendation = "Your BP is: " + str(current_BPsys) + "/" + str(
                #     current_BPdia) + " \n\nHigh Blood Pressure..Hypertension( Stage 1)"
                # self.manager.get_screen("Response").ids["response"].text = recommendation
                recommendation = str(current_BPsys) + "/" + str(
                    current_BPdia) + " [Hypertension(2)]"
                self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation

            elif (current_BPsys in range(130, 139)) or current_BPdia > 120:
                # recommendation = "Your BP is: " + str(current_BPsys) + "/" + str(
                #     current_BPdia) + " \n\nHigh Blood Pressure..Hypertension( Stage 1)"
                # self.manager.get_screen("Response").ids["response"].text = recommendation
                recommendation = str(current_BPsys) + "/" + str(
                    current_BPdia) + " [Hypertension Crisis]"
                self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation

            elif (current_BPsys in range(140, 180)) or (current_BPdia in range(90, 120)):
                # recommendation = " Your BP is: " + str(current_BPsys) + "/" + str(
                #     current_BPdia) + "\n\nHigh Blood Pressure..Hypertension(stage 2)"
                # self.manager.get_screen("Response").ids["response"].text = recommendation
                recommendation = str(current_BPsys) + "/" + str(
                    current_BPdia) + " [Hypertension(2)]"
                self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation

            elif (current_BPsys in range(140, 180)) or current_BPdia > 120:
                # recommendation = " Your BP is: " + str(current_BPsys) + "/" + str(
                #     current_BPdia) + "\n\nHigh Blood Pressure..Hypertension(stage 2)"
                # self.manager.get_screen("Response").ids["response"].text = recommendation
                recommendation = str(current_BPsys) + "/" + str(
                    current_BPdia) + " [Hypertension Crisis]"
                self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation

            elif (current_BPsys > 180) or (current_BPdia > 120):
                # recommendation = " Your BP is: " + str(current_BPsys) + "/" + str(
                #     current_BPdia) + "\n\nHypertension crisis..seek emergency care"
                # self.manager.get_screen("Response").ids["response"].text = recommendation
                recommendation = str(current_BPsys) + "/" + str(
                    current_BPdia) + " [Hypertension Crisis]"
                self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation
            else:
                pass

        else:
            recommendation = "Error!!!! Please start again the process!!!"
            # self.manager.get_screen("Response").ids["response"].text = recommendation
            self.manager.get_screen("Patient_Details").ids["bpValue"].text = recommendation
            self.manager.get_screen("Response").ids["response"].font_size = 27
            self.manager.get_screen("Response").ids["response"].bold = True
            return 0

        # Comparison

        cur.execute("SELECT sys_mmHg, dia_mmHg, BP_cart FROM vitals WHERE id = %s ORDER BY time_stamp DESC LIMIT 1,1",
                    [N_id])
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
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        elif (current_BP_cart == "Normal") and (previous_BP_cart == "Elevated"):
                            comment = " After comparing current with previous BP," + " " + "your BP has improved"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        elif (current_BP_cart == "Normal") and (previous_BP_cart == "Hypertension_Stage1"):
                            comment = " After comparing current with previous BP," + " " + " your BP has improved"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        elif (current_BP_cart == "Normal") and (previous_BP_cart == "Hypertension_Stage2"):
                            comment = " After comparing current with previous BP," + " " + " your BP has improved"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        elif (current_BP_cart == "Normal") and (previous_BP_cart == "Hypertensive_crisis"):
                            comment = " After comparing current with previous BP," + " " + " your BP has improved"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        # 1

                        elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Normal"):
                            comment = " After comparing current with previous BP," + " " + " your BP is slightly elevated but normal"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Elevated"):
                            comment = " After comparing current with previous BP," + " " + " has not changed"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Hypertension_Stage1"):
                            comment = " After comparing current with previous BP," + " " + " your BP has improved"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Hypertension_Stage2"):
                            comment = " After comparing current with previous BP," + " " + " your BP has improved"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Hypertensive_crisis"):
                            comment = " After comparing current with previous BP," + " " + " your BP has improved"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        # 2

                        elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Normal"):
                            comment = " After comparing current with previous BP," + " " + " you have high blood pressure (Hypertension_Stage1). You need to visit a doctor"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Elevated"):
                            comment = " After comparing current with previous BP," + " " + " your BP is now High (Hypertension_Stage1). You need to visit a doctor"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Hypertension_Stage1"):
                            comment = " After comparing current with previous BP," + " " + " your BP has not improved." + " " + " Visit a doctor for further clarifications"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Hypertension_Stage2"):
                            comment = " After comparing current with previous BP," + " " + " your BP has improved but continue the procedures the doctor advised you"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Hypertensive_crisis"):
                            comment = " After comparing current with previous BP," + " " + " your BP has greatly improved." + " " + " Continue the procedures the doctors advised you"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        # 3

                        elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Normal"):
                            comment = " After comparing current with previous BP," + " " + " you have high blood pressure (Hypertension_Stage2). " + " " + "You need to visit a doctor soon"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Elevated"):
                            comment = " After comparing current with previous BP," + " " + " your BP is now High (Hypertension_Stage2)." + " " + " You need to visit a doctor soon"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Hypertension_Stage1"):
                            comment = " After comparing current with previous BP, " + " " + "your BP is now High (Hypertension_Stage1)." + " " + " you need to visit a doctor soon"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Hypertension_Stage2"):
                            comment = " After comparing current with previous BP," + " " + " your BP has not improved." + " " + " Visit a doctor soon for further clarifications"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Hypertensive_crisis"):
                            comment = " After comparing current with previous BP," + " " + " your BP has improved." + " " + " Continue the procedures the doctors advised you"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        # 4

                        elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Normal"):
                            comment = " Visit a doctor now"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Elevated"):
                            comment = " Visit a doctor now"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Hypertension_Stage1"):
                            comment = "Visit a doctor now"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Hypertension_Stage2"):
                            comment = "Visit a doctor now"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Hypertensive_crisis"):
                            comment = " After comparing current with previous BP," + " " + " your BP is not improving. Visit a doctor now"
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                        else:
                            comment = ""
                            # pBP = str(previous_BPsys) + "/" + str(
                            #     previous_BPdia)
                            # self.manager.get_screen("Patient_Details").ids["pBP"].text = pBP
                            # self.manager.get_screen("Response").ids["comment"].text = comment
                            self.manager.get_screen("Patient_Details").ids["comment"].text = comment

                    else:
                        comment = ""
                        # pBP = str(current_BPsys) + "/" + str(
                        #     current_BPdia) + " [Hypertension Crisis]"
                        # self.manager.get_screen("Response").ids["comment"].text = comment
                        self.manager.get_screen("Patient_Details").ids["comment"].text = comment
        else:
            comment = "Data recorded"
            # self.manager.get_screen("Response").ids["comment"].text = comment
            self.manager.get_screen("Patient_Details").ids["comment"].text = comment


class ResponseWindow(Screen):
    def callback(self):
        App.stop(self)
        Window.close()

    def enter(self):
        self.manager.get_screen("Patient_Details").ids["bpValue"].text = ""
        self.manager.get_screen("Patient_Details").ids["restart"].opacity = 0
        self.manager.get_screen("Patient_Details").ids["takeBP"].opacity = 0

    def compose_response(self):
        cur.execute("SELECT id FROM vitals LIMIT 0,1")
        rows = cur.fetchall()
        N_id = ""
        current_BPsys = int()
        current_BPdia = int()
        current_BP_cart = ""
        previous_BPsys = int()
        previous_BPdia = int()
        previous_BP_cart = ""

        for row in rows:
            N_id = self.manager.get_screen("Patient_Details").ids["N_id"].text

        cur.execute("SELECT sys_mmHg, dia_mmHg, BP_cart  FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 0,1",
                    [N_id])
        rows = cur.fetchall()

        recommendation = ""
        comment = ""
        bp = ""

        for row in rows:
            current_BPsys = int(row[0])
            current_BPdia = int(row[1])
            current_BP_cart = row[2]

        # Response
        if current_BPsys > 1 and current_BPdia > 1:

            if (current_BPsys < 120) and (current_BPdia < 80):
                recommendation = "Your BP is: " + str(current_BPsys) + "/" + str(
                    current_BPdia) + "\n\nYour Blood pressure is normal"
                self.manager.get_screen("Response").ids["response"].text = recommendation

            elif (current_BPsys in range(121, 128)) and (current_BPdia < 80):
                recommendation = "Your BP is: " + str(current_BPsys) + "/" + str(
                    current_BPdia) + " \n\nYour BP is normal. Though elevated"
                self.manager.get_screen("Response").ids["response"].text = recommendation

            elif (current_BPsys in range(129, 139)) or (current_BPdia in range(81, 89)):
                recommendation = "Your BP is: " + str(current_BPsys) + "/" + str(
                    current_BPdia) + " \n\nHigh Blood Pressure..Hypertension( Stage 1)"
                self.manager.get_screen("Response").ids["response"].text = recommendation

            elif (current_BPsys in range(140, 180)) or (current_BPdia in range(90, 120)):
                recommendation = " Your BP is: " + str(current_BPsys) + "/" + str(
                    current_BPdia) + "\n\nHigh Blood Pressure..Hypertension(stage 2)"
                self.manager.get_screen("Response").ids["response"].text = recommendation

            elif (current_BPsys > 180) or (current_BPdia > 120):
                recommendation = " Your BP is: " + str(current_BPsys) + "/" + str(
                    current_BPdia) + "\n\nHypertension crisis..seek emergency care"
                self.manager.get_screen("Response").ids["response"].text = recommendation
            else:
                pass

        else:
            recommendation = "Error!!!! Please start again the process!!!"
            self.manager.get_screen("Response").ids["response"].text = recommendation
            self.manager.get_screen("Response").ids["response"].font_size = 27
            self.manager.get_screen("Response").ids["response"].bold = True
            return 0

        # Comparison

        cur.execute("SELECT sys_mmHg, dia_mmHg, BP_cart FROM vitals WHERE id = %s ORDER BY time_stamp DESC LIMIT 1,1",
                    [N_id])
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
                            comment = " After comparing current with previous BP, your BP is ok "
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        elif (current_BP_cart == "Normal") and (previous_BP_cart == "Elevated"):
                            comment = " After comparing current with previous BP, your BP has improved"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        elif (current_BP_cart == "Normal") and (previous_BP_cart == "Hypertension_Stage1"):
                            comment = " After comparing current with previous BP, your BP has improved"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        elif (current_BP_cart == "Normal") and (previous_BP_cart == "Hypertension_Stage2"):
                            comment = " After comparing current with previous BP, your BP has improved"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        elif (current_BP_cart == "Normal") and (previous_BP_cart == "Hypertensive_crisis"):
                            comment = " After comparing current with previous BP, your BP has improved"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        # 1

                        elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Normal"):
                            comment = " After comparing current with previous BP, your BP is slightly elevated but normal"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Elevated"):
                            comment = " After comparing current with previous BP, has not changed"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Hypertension_Stage1"):
                            comment = " After comparing current with previous BP, your BP has improved"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Hypertension_Stage2"):
                            comment = " After comparing current with previous BP, your BP has improved"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Hypertensive_crisis"):
                            comment = " After comparing current with previous BP, your BP has improved"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        # 2

                        elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Normal"):
                            comment = " After comparing current with previous BP, you have high blood pressure (Hypertension_Stage1). You need to visit a doctor"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Elevated"):
                            comment = " After comparing current with previous BP, your BP is now High (Hypertension_Stage1). You need to visit a doctor"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Hypertension_Stage1"):
                            comment = " After comparing current with previous BP, your BP has not improved. visit a doctor for further clarifications"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Hypertension_Stage2"):
                            comment = " After comparing current with previous BP, your BP has improved but continue the procedures the doctor advised you"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Hypertensive_crisis"):
                            comment = " After comparing current with previous BP, your BP has greatly improved. Continue the procedures the doctors advised you"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        # 3

                        elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Normal"):
                            comment = " After comparing current with previous BP, you have high blood pressure (Hypertension_Stage2). You need to visit a doctor soon"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Elevated"):
                            comment = " After comparing current with previous BP, your BP is now High (Hypertension_Stage2). You need to visit a doctor soon"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Hypertension_Stage1"):
                            comment = " After comparing current with previous BP, your BP is now High (Hypertension_Stage1). you need to visit a doctor soon"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Hypertension_Stage2"):
                            comment = " After comparing current with previous BP, your BP has not improved. Visit a doctor soon for further clarifications"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Hypertensive_crisis"):
                            comment = " After comparing current with previous BP, your BP has improved. Continue the procedures the doctors advised you"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        # 4

                        elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Normal"):
                            comment = " Visit a doctor now"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Elevated"):
                            comment = " Visit a doctor now"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Hypertension_Stage1"):
                            comment = "Visit a doctor now"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Hypertension_Stage2"):
                            comment = "Visit a doctor now"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Hypertensive_crisis"):
                            comment = " After comparing current with previous BP, your BP is not improving. Visit a doctor now"
                            self.manager.get_screen("Response").ids["comment"].text = comment

                        else:
                            comment = ""
                            self.manager.get_screen("Response").ids["comment"].text = comment

                    else:
                        comment = ""
                        self.manager.get_screen("Response").ids["comment"].text = comment
        else:
            comment = "Data recorded"
            self.manager.get_screen("Response").ids["comment"].text = comment

        # for row in rows:
        #     current_BPsys = int(row[0])
        #     current_BPdia = int(row[1])
        #
        # # Response
        # if current_BPsys > 1 and current_BPdia > 1:
        #
        #     if (current_BPsys < 120) and (current_BPdia < 80):
        #         recommendation = "Your BP is: " + str(current_BPsys) + "/" + str(
        #             current_BPdia) + "\n\nYour Blood pressure is normal"
        #         self.manager.get_screen("Response").ids["response"].text = recommendation
        #
        #     elif (current_BPsys in range(121, 128)) and (current_BPdia < 80):
        #         recommendation = "Your BP is: " + str(current_BPsys) + "/" + str(
        #             current_BPdia) + " \n\nYour BP is normal. Though elevated"
        #         self.manager.get_screen("Response").ids["response"].text = recommendation
        #
        #     elif (current_BPsys in range(129, 139)) or (current_BPdia in range(81, 89)):
        #         recommendation = "Your BP is: " + str(current_BPsys) + "/" + str(
        #             current_BPdia) + " \n\nHigh Blood Pressure..Hypertension( Stage 1)"
        #         self.manager.get_screen("Response").ids["response"].text = recommendation
        #
        #     elif (current_BPsys >= 140) or (current_BPdia > 90):
        #         recommendation = " Your BP is: " + str(current_BPsys) + "/" + str(
        #             current_BPdia) + "\n\nHigh Blood Pressure..Hypertension(stage 2)"
        #         self.manager.get_screen("Response").ids["response"].text = recommendation
        #
        #     elif (current_BPsys > 180) or (current_BPdia > 120):
        #         recommendation = " Your BP is: " + str(current_BPsys) + "/" + str(
        #             current_BPdia) + "\n\nHypertension crisis..seek emergency care"
        #         self.manager.get_screen("Response").ids["response"].text = recommendation
        #     else:
        #         pass
        #
        # else:
        #     recommendation = "Error!!!! Please start again the process!!!"
        #     self.manager.get_screen("Response").ids["response"].text = recommendation
        #     self.manager.get_screen("Response").ids["response"].font_size = 27
        #     self.manager.get_screen("Response").ids["response"].bold = True
        #
        # # Comparison
        #
        # cur.execute("SELECT sys_mmHg, dia_mmHg FROM vitals WHERE id = %s ORDER BY time_stamp DESC LIMIT 1,1", [N_id])
        # rows = cur.fetchall()
        # for row in rows:
        #     if len(str(row[0])) < 1 or len(str(row[1])) < 1:
        #         comment = "BP recorded"
        #         self.manager.get_screen("Response").ids["comment"].text = comment
        #
        #     else:
        #         previous_BPsys = int(row[0])
        #         previous_BPdia = int(row[1])
        #
        #         print(previous_BPsys)
        #         print(previous_BPdia)
        #         print(current_BPsys)
        #         print(current_BPdia)
        #         if previous_BPsys > 1 and previous_BPdia > 1:
        #
        #             if (previous_BPsys > current_BPsys) and (previous_BPdia > current_BPdia):
        #                 comment = " After comparing current with previous BP your BP has improved "
        #                 self.manager.get_screen("Response").ids["comment"].text = comment
        #
        #             elif (previous_BPsys < current_BPsys) and (previous_BPdia < current_BPdia):
        #                 comment = " After comparing with current and previous BP your BP has not improved "
        #                 self.manager.get_screen("Response").ids["comment"].text = comment
        #
        #             else:
        #                 pass
        #
        #         else:
        #             comment = ""
        #             self.manager.get_screen("Response").ids["comment"].text = comment


class Manager(ScreenManager):
    pass


class MyApp(App):
    def build(self):
        Window.clearcolor = (248 / 255, 247 / 255, 255 / 255, 1)
        Window.fullscreen = 'auto'
        return Manager()


if __name__ == "__main__":
    MyApp().run()
