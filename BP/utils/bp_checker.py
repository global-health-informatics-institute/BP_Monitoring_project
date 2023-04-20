import serial
import setts as settings
import threading
import hashlib
import mysql.connector as mysql
#from main import mysql
from kivy.app import App
from kivy.clock import mainthread, Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button

settings = settings.initialize_settings()

db = mysql.connect(
    host=settings["database"]["host"],
    user = settings["database"]["user"],
    passwd= settings["database"]["passwd"],
    database= settings["database"]["database"]
)
cur = db.cursor()

serialPort = serial.Serial(settings["BP"]["bp_port"],
                                    settings["BP"]["baudrate"],
                                    settings["BP"]["bytesize"],
                                    timeout= 1,
                                    stopbits= serial.STOPBITS_ONE
                                   )

class Check_BP():
    def __init__(self):
        self.bp = ""
        self.BP_cart = ""
        self.sys_mmHg = ""
        self.dia_mmHg = ""
        self.N_id2 = ""
        self.N_id = ""
        self.recommendation = ""
        self.comm_count = ""
        self.comment = ""
        self.nid = ""

    def check_port(self, data, nid):
        BP = list(data)
        if len(data) == 10:
            self.dia_mmHg = int(BP[4] + BP[5], 16)
            x = int(BP[2] + BP[3], 16)
            self.sys_mmHg = self.dia_mmHg + x

            print(self.bp)

            if (self.sys_mmHg in range(1,89)) or (self.dia_mmHg in range(1,59)):
                self.BP_cart = "Low"
                self.bp = str(self.sys_mmHg) + "/" + str(self.dia_mmHg)
                self.recommendation = str(self.sys_mmHg) + "/" + str(self.dia_mmHg) + " " + "Low"
            
            elif (self.sys_mmHg in range(90, 120)) and (self.dia_mmHg in range(60, 80)):
                self.BP_cart = 'Normal'
                self.bp = str(self.sys_mmHg) + "/" + str(self.dia_mmHg)
                self.recommendation = str(self.sys_mmHg) + "/" + str(self.dia_mmHg) + " " + "Normal"
            
            elif (self.sys_mmHg in range(121, 129)) or (self.dia_mmHg in range(1, 79)):
                self.BP_cart = "Elevated"
                self.bp = str(self.sys_mmHg) + "/" + str(self.dia_mmHg)
                self.recommendation = str(self.sys_mmHg) + "/" + str(self.dia_mmHg) + " " + "Elevated"
           
            elif (self.sys_mmHg in range(130, 139)) or (self.dia_mmHg in range(81, 89)):
                self.BP_cart = "Hypertension_Stage1"
                self.bp = str(self.sys_mmHg) + "/" + str(self.dia_mmHg)
                self.recommendation = str(self.sys_mmHg) + "/" + str(self.dia_mmHg) + " " + "Hypertension_Stage1"
          
            elif (self.sys_mmHg in range(140, 180)) or (self.dia_mmHg in range(90, 120)):
                self.BP_cart = "Hypertension_Stage2"
                self.recommendation = str(self.sys_mmHg) + "/" + str(self.dia_mmHg) + " " + "Hypertension_Stage2"
         
            elif (self.sys_mmHg > 180) or (self.dia_mmHg > 120):
                self.BP_cart = "Hypertensive_crisis"
                self.bp = str(self.sys_mmHg) + "/" + str(self.dia_mmHg)
                self.recommendation = str(self.sys_mmHg) + "/" + str(self.dia_mmHg) + " " + "Hypertension_crisis"
          
            else:
                self.BP_cart = "No feedback; an error occured"
                self.bp = "Error...Try Again"
                self.recommendation = "Error...Try Again"

        N_idHash = nid[1]
        National_id = str(N_idHash).encode("ASCII")
        d = hashlib.sha3_256(National_id)
        N_id = d.hexdigest()
        cur.execute("SELECT id FROM Demographic WHERE national_id= %s ", [N_id])
        recs = cur.fetchall()
        for rec in recs:
            self.N_id2 = rec[0]

        cur.execute("SELECT sys_mmHg, dia_mmHg, BP_cart FROM vitals WHERE id = %s ORDER BY time_stamp DESC LIMIT 0,1",
                    [self.N_id2])
        rows = cur.fetchall()
        if rows:
            for row in rows:
                if len(str(row[0])) < 1 or len(str(row[1])) < 1:
                    pass
                else:
                    previous_BPsys = int(row[0])
                    previous_BPdia = int(row[1])
                    previous_BP_cart = row[2]

                    if previous_BPsys > 1 and previous_BPdia > 1:

                        # 1
                        if (self.BP_cart == "Low") and (previous_BP_cart == "Low"):
                            self.comment = " After comparing current with previous BP," + "  " + "your BP is still low "
                        elif (self.BP_cart == "Low") and (previous_BP_cart == "Normal"):
                            self.comment = " After comparing current with previous BP," + " " + "your BP has gone low"
                        elif (self.BP_cart == "Low") and (previous_BP_cart == "Elevated"):
                            self.comment = " After comparing current with previous BP," + " " + "your BP has gone low"
                        elif (self.BP_cart == "Low") and (previous_BP_cart == "Hypertension_Stage1"):
                            self.comment = " After comparing current with previous BP," + " " + " your BP has gone low"
                        elif (self.BP_cart == "Low") and (previous_BP_cart == "Hypertension_Stage2"):
                            self.comment = " After comparing current with previous BP," + " " + " your BP has gone low"
                        elif (self.BP_cart == "Low") and (previous_BP_cart == "Hypertensive_crisis"):
                            self.comment = " After comparing current with previous BP," + " " + " your BP has gone low"
                        
                        # 2
                        if (self.BP_cart == "Normal") and (previous_BP_cart == "Normal"):
                            self.comment = " After comparing current with previous BP," + "  " + "your BP is ok "
                        elif (self.BP_cart == "Normal") and (previous_BP_cart == "Low"):
                            self.comment = " After comparing current with previous BP," + " " + "your BP has improved"
                        elif (self.BP_cart == "Normal") and (previous_BP_cart == "Elevated"):
                            self.comment = " After comparing current with previous BP," + " " + "your BP has improved"
                        elif (self.BP_cart == "Normal") and (previous_BP_cart == "Hypertension_Stage1"):
                            self.comment = " After comparing current with previous BP," + " " + " your BP has improved"
                        elif (self.BP_cart == "Normal") and (previous_BP_cart == "Hypertension_Stage2"):
                            self.comment = " After comparing current with previous BP," + " " + " your BP has improved"
                        elif (self.BP_cart == "Normal") and (previous_BP_cart == "Hypertensive_crisis"):
                            self.comment = " After comparing current with previous BP," + " " + " your BP has improved"
                        

                        # 3
                        elif (self.BP_cart == "Elevated") and (previous_BP_cart == "Low"):
                            self.comment = " After comparing current with previous BP," + " " + "your BP has improved but is slightly elevated"
                        elif (self.BP_cart == "Elevated") and (previous_BP_cart == "Normal"):
                            self.comment = " After comparing current with previous BP," + " " + " your BP is slightly elevated"
                        elif (self.BP_cart == "Elevated") and (previous_BP_cart == "Elevated"):
                            self.comment = " After comparing current with previous BP," + " " + " has not changed"
                        elif (self.BP_cart == "Elevated") and (previous_BP_cart == "Hypertension_Stage1"):
                            self.comment = " After comparing current with previous BP," + " " + " your BP has improved"
                        elif (self.BP_cart == "Elevated") and (previous_BP_cart == "Hypertension_Stage2"):
                            self.comment = " After comparing current with previous BP," + " " + " your BP has improved"
                        elif (self.BP_cart == "Elevated") and (previous_BP_cart == "Hypertensive_crisis"):
                            self.comment = " After comparing current with previous BP," + " " + " your BP has improved"


                        # 4  
                        elif (self.BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Normal"):
                            self.comment = " After comparing current with previous BP," + " " + " you have high blood pressure (Hypertension_Stage1)"
                        elif (self.BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Low"):
                            self.comment = " After comparing current with previous BP," + " " + " your BP is now High (Hypertension_Stage1)."
                        elif (self.BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Elevated"):
                            self.comment = " After comparing current with previous BP," + " " + " your BP is now High (Hypertension_Stage1)."
                        elif (self.BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Hypertension_Stage1"):
                            self.comment = " After comparing current with previous BP," + " " + " your BP has not improved."
                        elif (self.BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Hypertension_Stage2"):
                            self.comment = " After comparing current with previous BP," + " " + " your BP has improved but continue the procedures the doctor advised you"
                        elif (self.BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Hypertensive_crisis"):
                            self.comment = " After comparing current with previous BP," + " " + " your BP has greatly improved." + " " + " Continue the procedures the doctors advised you"


                        # 5 
                        elif (self.BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Normal"):
                            self.comment = " After comparing current with previous BP," + " " + " you have high blood pressure (Hypertension_Stage2). "
                        elif (self.BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Low"):
                            self.comment = " After comparing current with previous BP," + " " + " your BP is now High (Hypertension_Stage2)."
                        elif (self.BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Elevated"):
                            self.comment = " After comparing current with previous BP," + " " + " your BP is now High (Hypertension_Stage2)."
                        elif (self.BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Hypertension_Stage1"):
                            self.comment = " After comparing current with previous BP, " + " " + "your BP is now High (Hypertension_Stage1)."
                        elif (self.BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Hypertension_Stage2"):
                            self.comment = " After comparing current with previous BP," + " " + " your BP has not improved."
                        elif (self.BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Hypertensive_crisis"):
                            self.comment = " After comparing current with previous BP," + " " + " your BP has improved." + " " + " Continue the procedures the doctors advised you"


                        # 6
                        elif (self.BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Low"):
                            self.comment = " Visit a doctor now"
                        elif (self.BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Normal"):
                            self.comment = " Visit a doctor now"
                        elif (self.BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Elevated"):
                            self.comment = " Visit a doctor now"
                        elif (self.BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Hypertension_Stage1"):
                            self.comment = "Visit a doctor now"
                        elif (self.BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Hypertension_Stage2"):
                            self.comment = "Visit a doctor now"
                        elif (self.BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Hypertensive_crisis"):
                            self.comment = " After comparing current with previous BP," + " " + " your BP is not improving. Visit a doctor now"

                    #     else:
                    #         self.comment = ""

                    # else:
                    #     self.comment = "Nothing to compare to currently"
        else:
            self.comment = "Data recorded"            

            
        result = {"bp": self.bp, "BP_cart": self.BP_cart, "dia_mmHg": self.dia_mmHg, "sys_mmHg": self.sys_mmHg, 
                    "N_id":self.N_id, "N_id2":self.N_id2, "recommendation":self.recommendation, "comment": self.comment}
        # print(result)
        return result

# check_port()