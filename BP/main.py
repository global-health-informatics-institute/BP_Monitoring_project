import RPi.GPIO as GPIO
# from gpiozero import LED
from kivy.app import App
import mysql.connector as mysql
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
import serial

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

            gender = val[8]
            DOB = val[9]
            cur.execute("SELECT * FROM Demographic WHERE id=%s", [N_id])
            record = cur.fetchall()
            if record:
                self.manager.get_screen("Patient_Details").ids["N_id"].text = str(N_id)
                self.manager.get_screen("Patient_Details").ids["f_name"].text = str(fname)
                self.manager.get_screen("Patient_Details").ids["gender"].text = str(gender)
                self.manager.get_screen("Patient_Details").ids["dob"].text = str(DOB)
                self.manager.transition.direction = "left"
                self.parent.current = "Patient_Details"

            else:
                cur.execute("INSERT INTO Demographic (id, Full_name, Gender, DOB) VALUES (%s, %s, %s, %s) ",
                            (N_id, fname, gender, DOB))
                db.commit()
                self.manager.get_screen("Patient_Details").ids["N_id"].text = str(N_id)
                self.manager.get_screen("Patient_Details").ids["f_name"].text = str(fname)
                self.manager.get_screen("Patient_Details").ids["gender"].text = str(gender)
                self.manager.get_screen("Patient_Details").ids["dob"].text = str(DOB)
                self.manager.transition.direction = "left"
                self.parent.current = "Patient_Details"

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
    def generate_BP(self):
        N_id = self.manager.get_screen("Patient_Details").ids["N_id"].text
        serialPort = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=0.5, bytesize=8, stopbits=serial.STOPBITS_ONE)
        serialData = ""
        bp = ""
        BP_cart = ""
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

                    if (sys_mmHg in range(1, 120)) and (dia_mmHg in range(1, 80)):
                        BP_cart = "Normal"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        self.parent.current = "Response"

                    elif (sys_mmHg in range(121, 128)) and (dia_mmHg < 80):
                        BP_cart = "Elevated"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        self.parent.current = "Response"

                    elif (sys_mmHg in range(129, 139)) or (dia_mmHg in range(81, 89)):
                        BP_cart = "Hypertension_Stage1"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        self.parent.current = "Response"

                    elif (sys_mmHg in range(140, 180)) or (dia_mmHg in range(90, 120)):
                        BP_cart = "Hypertension_Stage2"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        self.parent.current = "Response"

                    elif (sys_mmHg > 180) or (dia_mmHg > 120):
                        BP_cart = "Hypertensive_crisis"
                        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                                    (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        db.commit()
                        bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        self.parent.current = "Response"

                    else:
                        # BP_cart = "Error"
                        # cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg, BP_cart) VALUES (%s,%s, %s, %s) ",
                        #             (N_id, sys_mmHg, dia_mmHg, BP_cart))
                        # db.commit()
                        # bp = str(sys_mmHg) + "/" + str(dia_mmHg)
                        bp = "Error..Try Again"
                        self.manager.get_screen("Patient_Details").ids["bpValue"].text = bp
                        self.parent.current = "Patient_Details"

                m = False

    def enter(self):
        self.manager.get_screen("Patient_Details").ids["bpValue"].text = "Waiting for BP vitals..."


class ResponseWindow(Screen):
    def callback(self):
        App.stop(self)
        Window.close()

    def enter(self):
        self.manager.get_screen("Patient_Details").ids["bpValue"].text = "Waiting for BP vitals..."

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
