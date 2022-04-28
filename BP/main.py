from kivy.app import App
import mysql.connector as mysql
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window

Window.size = (600, 800)

db = mysql.connect(
    host="127.0.0.1",
    user="ghii",
    passwd="",
    database="BP_Project"
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
            BP = 0
            cur.execute("SELECT * FROM Patients WHERE id=%s", [N_id])
            record = cur.fetchall()
            if record:
                self.manager.get_screen("Patient_Details").ids["N_id"].text = str(N_id)
                self.manager.get_screen("Patient_Details").ids["f_name"].text = str(fname)
                self.manager.get_screen("Patient_Details").ids["gender"].text = str(gender)
                self.manager.get_screen("Patient_Details").ids["dob"].text = str(DOB)
                self.manager.get_screen("Patient_Details").ids["bp"].text = str(BP)
                self.parent.current = "Patient_Details"

            else:
                cur.execute("INSERT INTO Patients (id, Full_name, Gender, DOB, BP) VALUES (%s, %s, %s, %s, %s) ",
                            (N_id, fname, gender, DOB, BP))
                db.commit()
                db.close()
                self.manager.get_screen("Patient_Details").ids["N_id"].text = str(N_id)
                self.manager.get_screen("Patient_Details").ids["f_name"].text = str(fname)
                self.manager.get_screen("Patient_Details").ids["gender"].text = str(gender)
                self.manager.get_screen("Patient_Details").ids["dob"].text = str(DOB)
                self.manager.get_screen("Patient_Details").ids["bp"].text = str(BP)
                self.parent.current = "Patient_Details"

        else:

            self.parent.current = "Scan"
            self.manager.get_screen("Scan").ids["textFocus"].text = " "
            self.manager.get_screen("Scan").ids["textFocus"].focus = True


class PatientDetails(Screen):
    pass


class ResponseWindow(Screen):
    pass


class Manager(ScreenManager):
    pass


class MyApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 1, 1)
        return Manager()


if __name__ == "__main__":
    MyApp().run()
