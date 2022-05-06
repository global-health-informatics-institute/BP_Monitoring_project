from kivy.app import App
import mysql.connector as mysql
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
import random

Window.size = (480, 800)

db = mysql.connect(
    host="127.0.0.1",
    user="ghii",
    passwd="",
    database="Hypertension"
)
cur = db.cursor()


class MainWindow(Screen):
    def callback(self):
        App.stop(self)
        Window.close()


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
            BP = 0
            cur.execute("SELECT * FROM Demographic WHERE id=%s", [N_id])
            record = cur.fetchall()
            if record:
                self.manager.get_screen("Patient_Details").ids["N_id"].text = str(N_id)
                self.manager.get_screen("Patient_Details").ids["f_name"].text = str(fname)
                self.manager.get_screen("Patient_Details").ids["gender"].text = str(gender)
                self.manager.get_screen("Patient_Details").ids["dob"].text = str(DOB)
                self.parent.current = "Patient_Details"

            else:
                cur.execute("INSERT INTO Demographic (id, Full_name, Gender, DOB) VALUES (%s, %s, %s, %s) ",
                            (N_id, fname, gender, DOB))
                db.commit()
                db.close()
                self.manager.get_screen("Patient_Details").ids["N_id"].text = str(N_id)
                self.manager.get_screen("Patient_Details").ids["f_name"].text = str(fname)
                self.manager.get_screen("Patient_Details").ids["gender"].text = str(gender)
                self.manager.get_screen("Patient_Details").ids["dob"].text = str(DOB)
                self.parent.current = "Patient_Details"

        else:

            self.parent.current = "Scan"
            self.manager.get_screen("Scan").ids["textFocus"].text = " "
            self.manager.get_screen("Scan").ids["textFocus"].focus = True


class PatientDetails(Screen):
    def generate_BP(self):
        N_id = self.manager.get_screen("Patient_Details").ids["N_id"].text
        systolic = random.randint(8, 170)
        diastolic = random.randint(6, 120)
        cur.execute("INSERT INTO vitals (id, sys_mmHg, dia_mmHg) VALUES (%s,%s, %s) ",
                    (N_id, systolic, diastolic))
        db.commit()
        print(diastolic)
        print(N_id)


class ResponseWindow(Screen):
    def callback(self):
        App.stop(self)
        Window.close()

    def compose_response(self):
        cur.execute("SELECT id FROM vitals LIMIT 0,1")
        rows = cur.fetchall()
        N_id = ""
        current_BPsys = int()
        current_BPdia = int()
        previous_BPsys = int()
        previous_BPdia = int()

        for row in rows:
            N_id = row[0]

        cur.execute("SELECT sys_mmHg, dia_mmHg  FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 0,1", [N_id])
        rows = cur.fetchall()

        recommendation = ""
        comment = ""
        bp = ""

        for row in rows:
            current_BPsys = int(row[0])
            current_BPdia = int(row[1])
        print(current_BPsys)
        print(current_BPdia)

        # Response
        if current_BPsys > 1 and current_BPdia > 1:

            if (current_BPsys < 120) and (current_BPdia < 80):
                recommendation = "Your BP is: " + str(current_BPsys) + "/" + str(
                    current_BPdia) + "\nYour Blood pressure is normal"
                self.manager.get_screen("Response").ids["response"].text = recommendation

            elif (current_BPsys in range(121, 128)) and (current_BPdia < 80):
                recommendation = "Your BP is: " + str(current_BPsys) + "/" + str(
                    current_BPdia) + " \nYour BP is elevated. See clinician within a month"
                self.manager.get_screen("Response").ids["response"].text = recommendation

            elif (current_BPsys in range(129, 139)) or (current_BPdia in range(81, 89)):
                recommendation = "Your BP is: " + str(current_BPsys) + "/" + str(
                    current_BPdia) + " \nYou have hypertension (Stage one)..See a clinician soon"
                self.manager.get_screen("Response").ids["response"].text = recommendation

            elif (current_BPsys >= 140) or (current_BPdia > 90):
                recommendation = " Your BP is: " + str(current_BPsys) + "/" + str(
                    current_BPdia) + "\nHigh Blood Pressure..visit a doctor in a week"
                self.manager.get_screen("Response").ids["response"].text = recommendation

            elif (current_BPsys > 180) or (current_BPdia > 120):
                recommendation = " Your BP is: " + str(current_BPsys) + "/" + str(
                    current_BPdia) + "\nHigh Blood Pressure..visit a doctor in a now"
                self.manager.get_screen("Response").ids["response"].text = recommendation
            else:
                pass

        else:

            bp = "Your BP is: " + str(current_BPsys) + "/" + str(
                current_BPdia)
            comment = "Your Blood Pressure has been recorded successfully"
            self.manager.get_screen("Response").ids["response"].text = bp
            self.manager.get_screen("Response").ids["comment"].text = comment

        # Comparison

        cur.execute("SELECT sys_mmHg, dia_mmHg FROM vitals WHERE id = %s ORDER BY time_stamp DESC LIMIT 1,1", [N_id])
        rows = cur.fetchall()
        for row in rows:
            if len(str(row[0])) < 1 or len(str(row[1])) < 1:

                bp = "Your BP is: " + str(current_BPsys) + "/" + str(
                    current_BPdia)
                comment = "You do not have any history record. Your Blood Pressure has been recorded successfully"
                self.manager.get_screen("Response").ids["response"].text = bp
                self.manager.get_screen("Response").ids["comment"].text = comment

            else:
                previous_BPsys = int(row[0])
                previous_BPdia = int(row[1])

                print(previous_BPdia)
                print(previous_BPsys)
                print(current_BPdia)
                print(current_BPsys)

                if previous_BPsys > 1 and previous_BPdia > 1:

                    if (previous_BPsys > current_BPsys) and (previous_BPdia > current_BPdia):
                        comment = " After comparing current with previous BP your BP has improved "
                        self.manager.get_screen("Response").ids["comment"].text = comment

                    elif (previous_BPsys < current_BPsys) and (previous_BPdia < current_BPdia):
                        comment = " After comparing with current and previous BP your BP has not improved "
                        self.manager.get_screen("Response").ids["comment"].text = comment

                    else:
                        pass

                else:
                    pass


class Manager(ScreenManager):
    pass


class MyApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 1, 1)
        Window.borderless = True
        # Window.custom_titlebar = True

        return Manager()


if __name__ == "__main__":
    MyApp().run()
