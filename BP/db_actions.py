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

    def __init__(self):
        self.N_id2 = ""
        self.N_id = ""
        self.text = ""
        self.date = ""

    def BP1(self, nid):
        # BP = list(data)
        # if len(data) == 10:
        #     self.dia_mmHg = int(BP[4] + BP[5], 16)
        #     x = int(BP[2] + BP[3], 16)
        #     self.sys_mmHg = self.dia_mmHg + x

        N_idHash = nid[1]
        National_id = str(N_idHash).encode("ASCII")
        d = hashlib.sha3_256(National_id)
        self.N_id = d.hexdigest()
        cur.execute("SELECT id FROM Demographic WHERE national_id= %s ", [self.N_id])
        recs = cur.fetchall()
        for rec in recs:
            self.N_id2 = rec[0]

            # @BP 1 
            cur.execute("SELECT sys_mmHg, dia_mmHg, time_stamp FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 4",
                        [self.N_id2])
            rows = cur.fetchall()
            for row in rows:
                current_BPsys = int(row[0])
                current_BPdia = int(row[1])
                timeStamp = str(row[2]).split(" ")
                
                if len(current_BPsys) < 1 or len(current_BPdia) < 1:
                    self.text = ""
                    self.date = ""
                else:
                    pBP = current_BPsys + "/" + current_BPdia
                    self.text = pBP
                    self.date = timeStamp[0]

                    # # @BP 2
                    # cur.execute("SELECT sys_mmHg, dia_mmHg, time_stamp  FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 1,1",
                    #             [self.N_id2])
                    # rows2 = cur.fetchall()
                    # if rows2:
                    #     for row2 in rows2:
                    #         previous_BPsys2 = str(row2[0])
                    #         previous_BPdia2 = str(row2[1])
                    #         timeStamp2 = str(row2[2]).split(" ")

                    #         if len(previous_BPsys2) < 1 or len(previous_BPdia2) < 1:
                    #             self.text = ""
                    #             self.date = ""
                    #         else:
                    #             pBP2 = previous_BPsys2 + "/" + previous_BPdia2
                    #             self.text = pBP2
                    #             self.date = timeStamp2[0]
                            
                    #         # @BP 3
                    #         cur.execute(
                    #             "SELECT sys_mmHg, dia_mmHg, time_stamp  FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 2,1",
                    #             [self.N_id2])
                    #         rows3 = cur.fetchall()
                    #         if rows3:
                    #             for row3 in rows3:
                    #                 previous_BPsys3 = str(row3[0])
                    #                 previous_BPdia3 = str(row3[1])
                    #                 timeStamp3 = str(row3[2]).split(" ")

                    #                 if len(previous_BPsys3) < 1 or len(previous_BPdia3) < 1:
                    #                     self.text = ""
                    #                     self.date = ""
                    #                 else:
                    #                     pBP3 = previous_BPsys3 + "/" + previous_BPdia3
                    #                     self.text = pBP3
                    #                     self.date = timeStamp3[0]

                    #                 # @BP 4
                    #                 cur.execute(
                    #                     "SELECT sys_mmHg, dia_mmHg, time_stamp  FROM vitals WHERE id= %s ORDER BY time_stamp DESC LIMIT 3,1",
                    #                     [self.N_id2])
                    #                 rows4 = cur.fetchall()
                    #                 if rows4:
                    #                     for row4 in rows4:
                    #                         previous_BPsys4 = str(row4[0])
                    #                         previous_BPdia4 = str(row4[1])
                    #                         timeStamp4 = str(row4[2]).split(" ")
                                            
                    #                         if len(previous_BPsys4) < 1 or len(previous_BPdia4) < 1:
                    #                             self.text = ""
                    #                             self.date = ""
                    #                         else:
                    #                             pBP4 = previous_BPsys4 + "/" + previous_BPdia4
                    #                             self.text = pBP4
                    #                             self.date = timeStamp4[0]
                

        res = {"N_id2":self.N_id2, "N_id":self.N_id, "date": self.date, "text": self.text}
        return(res)


    
    #initialize low to critical as 1 - 5, compare the figures accordingn to what has been tested.