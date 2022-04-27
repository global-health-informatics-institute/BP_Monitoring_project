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
        print('Enter your something:')
        name = input()
        val = name.split('~')
        print(len(val))
        print(val)
        firstname = val[6]
        funame = firstname.replace(',', ' ')
        lastname = val[4]
        fname = funame + " " + lastname
        N_id = val[5]
        gender = val[8]
        DOB = val[9]
        BP = 0

        if len(val) == 12:
            cur.execute("SELECT * FROM Patients WHERE id=%s", [N_id])
            record = cur.fetchall()
            if record:
                self.manager.ids.scn.N_id.text = N_id
                self.manager.ids.scn.f_name.text = fname
                self.manager.ids.scn.gender.text = gender
                self.manager.ids.scn.DOB.text = DOB
                self.manager.ids.scn.BP.text = BP
                self.parent.current = "Patient_Details"

            else:
                cur.execute("INSERT INTO Patients (id, Full_name, Gender, DOB, BP) VALUES (%s, %s, %s, %s, %s) ",
                            (N_id, fname, gender, DOB, BP))
                db.commit()
                self.manager.ids.scn.N_id.text = N_id
                self.manager.ids.scn.f_name.text = fname
                self.manager.ids.scn.gender.text = gender
                self.manager.ids.scn.dob.text = DOB
                self.manager.ids.scn.bp.text = BP
                self.parent.current = "Patient_Details"

        else:
            self.parent.current = "Scan"
            self.callback()


class PatientDetails(Screen):
    # def callback(self):

    # N_id = self.manager.
    # fname = ""
    # gender = ""
    # DOB = ""
    # BP = ""
    #
    # cur.execute("SELECT * FROM Patients WHERE id=%s", [N_id])
    # record = cur.fetchall()
    # if record:
    #     self.natID.text = N_id
    #     self.fName.text = fname
    #     self.gen.text = gender
    #     self.dOB.text = DOB
    #     self.bloodP.text = BP
    #
    # else:
    #     self.parent.current = "Scan_window"
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
