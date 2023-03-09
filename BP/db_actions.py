import json
import mysql.connector as mysql
import hashlib
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.app import App
from kivy.core.window import Window

from nat_id import Parse_NID
# from main import ScanWindow
Window.size = (480, 800)


def initialize_settings():
    settings = {}
    with open("conn.config") as json_file:
        settings = json.load(json_file)
    return settings

settings = initialize_settings()



db = mysql.connect(
    host=settings["database"]["host"],
    user = settings["database"]["user"],
    passwd= settings["database"]["passwd"],
    database= settings["database"]["database"]
)
cur = db.cursor()

class data_control():
#consider writing all the execute
#queries in one file
#they will be called from that as a function
#perhaps this will need parsing of the variable 'val'
    def BP1(self, nid):
        N_idHash = nid[1]
        National_id = str(N_idHash).encode("ASCII")
        d = hashlib.sha3_256(National_id)
        N_id = d.hexdigest()
        cur.execute("SELECT id FROM Demographic WHERE national_id= %s ", [N_id])
        recs = cur.fetchall()
        for rec in recs:
            N_id2 = rec[0]

        cur.execute("SELECT sys_mmHg, dia_mmHg, BP_cart  FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 0,1",
                    [N_id2])
        rows2 = cur.fetchall()
        for row in rows2:
            current_BPsys = int(row[0])
            current_BPdia = int(row[1])
            current_BP_cart = row[2]

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
                    comment = ""

                    if previous_BPsys > 1 and previous_BPdia > 1:

                        # 1
                        if (current_BP_cart == "Low") and (previous_BP_cart == "Low"):
                            comment = " After comparing current with previous BP," + "  " + "your BP is still low "
                        elif (current_BP_cart == "Low") and (previous_BP_cart == "Normal"):
                            comment = " After comparing current with previous BP," + " " + "your BP has gone low"
                        elif (current_BP_cart == "Low") and (previous_BP_cart == "Elevated"):
                            comment = " After comparing current with previous BP," + " " + "your BP has gone low"
                        elif (current_BP_cart == "Low") and (previous_BP_cart == "Hypertension_Stage1"):
                            comment = " After comparing current with previous BP," + " " + " your BP has gone low"
                        elif (current_BP_cart == "Low") and (previous_BP_cart == "Hypertension_Stage2"):
                            comment = " After comparing current with previous BP," + " " + " your BP has gone low"
                        elif (current_BP_cart == "Low") and (previous_BP_cart == "Hypertensive_crisis"):
                            comment = " After comparing current with previous BP," + " " + " your BP has gone low"
                        
                        # 2
                        if (current_BP_cart == "Normal") and (previous_BP_cart == "Normal"):
                            comment = " After comparing current with previous BP," + "  " + "your BP is ok "
                        elif (current_BP_cart == "Normal") and (previous_BP_cart == "Low"):
                            comment = " After comparing current with previous BP," + " " + "your BP has improved"
                        elif (current_BP_cart == "Normal") and (previous_BP_cart == "Elevated"):
                            comment = " After comparing current with previous BP," + " " + "your BP has improved"
                        elif (current_BP_cart == "Normal") and (previous_BP_cart == "Hypertension_Stage1"):
                            comment = " After comparing current with previous BP," + " " + " your BP has improved"
                        elif (current_BP_cart == "Normal") and (previous_BP_cart == "Hypertension_Stage2"):
                            comment = " After comparing current with previous BP," + " " + " your BP has improved"
                        elif (current_BP_cart == "Normal") and (previous_BP_cart == "Hypertensive_crisis"):
                            comment = " After comparing current with previous BP," + " " + " your BP has improved"
                        

                        # 3
                        elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Low"):
                            comment = " After comparing current with previous BP," + " " + "your BP has improved but is slightly elevated"
                        elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Normal"):
                            comment = " After comparing current with previous BP," + " " + " your BP is slightly elevated"
                        elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Elevated"):
                            comment = " After comparing current with previous BP," + " " + " has not changed"
                        elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Hypertension_Stage1"):
                            comment = " After comparing current with previous BP," + " " + " your BP has improved"
                        elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Hypertension_Stage2"):
                            comment = " After comparing current with previous BP," + " " + " your BP has improved"
                        elif (current_BP_cart == "Elevated") and (previous_BP_cart == "Hypertensive_crisis"):
                            comment = " After comparing current with previous BP," + " " + " your BP has improved"


                        # 4  
                        elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Normal"):
                            comment = " After comparing current with previous BP," + " " + " you have high blood pressure (Hypertension_Stage1)"
                        elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Low"):
                            comment = " After comparing current with previous BP," + " " + " your BP is now High (Hypertension_Stage1)."
                        elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Elevated"):
                            comment = " After comparing current with previous BP," + " " + " your BP is now High (Hypertension_Stage1)."
                        elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Hypertension_Stage1"):
                            comment = " After comparing current with previous BP," + " " + " your BP has not improved."
                        elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Hypertension_Stage2"):
                            comment = " After comparing current with previous BP," + " " + " your BP has improved but continue the procedures the doctor advised you"
                        elif (current_BP_cart == "Hypertension_Stage1") and (previous_BP_cart == "Hypertensive_crisis"):
                            comment = " After comparing current with previous BP," + " " + " your BP has greatly improved." + " " + " Continue the procedures the doctors advised you"


                        # 5 
                        elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Normal"):
                            comment = " After comparing current with previous BP," + " " + " you have high blood pressure (Hypertension_Stage2). "
                        elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Low"):
                            comment = " After comparing current with previous BP," + " " + " your BP is now High (Hypertension_Stage2)."
                        elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Elevated"):
                            comment = " After comparing current with previous BP," + " " + " your BP is now High (Hypertension_Stage2)."
                        elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Hypertension_Stage1"):
                            comment = " After comparing current with previous BP, " + " " + "your BP is now High (Hypertension_Stage1)."
                        elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Hypertension_Stage2"):
                            comment = " After comparing current with previous BP," + " " + " your BP has not improved."
                        elif (current_BP_cart == "Hypertension_Stage2") and (previous_BP_cart == "Hypertensive_crisis"):
                            comment = " After comparing current with previous BP," + " " + " your BP has improved." + " " + " Continue the procedures the doctors advised you"


                        # 6
                        elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Low"):
                            comment = " Visit a doctor now"
                        elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Normal"):
                            comment = " Visit a doctor now"
                        elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Elevated"):
                            comment = " Visit a doctor now"
                        elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Hypertension_Stage1"):
                            comment = "Visit a doctor now"
                        elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Hypertension_Stage2"):
                            comment = "Visit a doctor now"
                        elif (current_BP_cart == "Hypertensive_crisis") and (previous_BP_cart == "Hypertensive_crisis"):
                            comment = " After comparing current with previous BP," + " " + " your BP is not improving. Visit a doctor now"

                        else:
                            comment = ""
                        

        res = {"N_id2":N_id2, "N_id":N_id, "current_BPsys":current_BPsys, "current_BPdia":current_BPdia,
                "current_BP_cart":current_BP_cart, "comment": comment}
        return(res)


    
    #initialize low to critical as 1 - 5, compare the figures accordingn to what has been tested.