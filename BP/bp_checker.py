import serial
import setts as settings
import threading
import hashlib

settings = settings.initialize_settings()

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

    def check_port(self, data):
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


            
        result = {"bp": self.bp, "BP_cart": self.BP_cart, "dia_mmHg": self.dia_mmHg, "sys_mmHg": self.sys_mmHg, 
                    "N_id":self.N_id, "recommendation":self.recommendation}
        # print(result)
        return result

# check_port()