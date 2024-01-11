from datetime import date
import hashlib, serial, json, pycurl
import time
import mysql.connector as mysql

def initialize_settings():
    settings = {}
    with open("/home/pi/BP_Monitoring_project/BP/conn.config") as json_file:
        settings = json.load(json_file)
    return settings

settings = initialize_settings()
URL = settings["url"]

db = mysql.connect(
    host=settings["database"]["host"],
    user = settings["database"]["user"],
    passwd= settings["database"]["passwd"],
    database= settings["database"]["database"]
)

cur = db.cursor()

ser_port = serial.Serial(settings["gsm"]["id"],
                            settings["gsm"]["baudrate"],
                            timeout= 0.5)

#while True:
# cur.execute("SELECT * from vitals WHERE status = 0")
cur.execute("SELECT v.id, v.sys_mmHg, v.dia_mmHg, v.BP_cart, D.Full_name, D.Gender, D.DOB, v.national_id, v.p_rate from vitals v JOIN Demographic D ON v.national_id = D.national_id WHERE status = 0")
rows = cur.fetchall()
print (rows)
for row in rows:
    N_id = row[0]
#    print("this is id ", N_id)
    bp = str(row[1]) + "/" + str(row[2])
#    print(bp)
    BP_cart = row[3]
    fname = row[4]
    gender = row[5]
    dob = row[6]
    hex_id = row[7]
    p_rate = row[8]
    
    checkAT = 'AT\r'
    ser_port.write(checkAT.encode())
    mes = ser_port.read(64)
    time.sleep(5)
    #print(mes)
    
    if b'AT\r\r\nOK\r\n' or b'AT\r\n> ' in mes:
#        print("success")
        cur.execute("UPDATE vitals SET status = 1 WHERE id = %s", [N_id])
        db.commit()
#        print("db updated")
    else:
        print("unsuccessful")

    stres = 'AT+CMGF=1\r'
    ser_port.write(stres.encode())
    time.sleep(0.1)
    
    cmd1 = 'AT+CMGS="'+settings["server_number"]+'"\r'
    ser_port.write(cmd1.encode())
    msg = ser_port.read(64)
    time.sleep(5)
    
    # response = str(N_id) + "|" + str(bp) + "|" + BP_cart + "|" + str(dob) + "|" + str(hex_id) + "|" + str(p_rate) + '\r'
    response = str(N_id) + "|" + str(bp) + "|" + BP_cart + "|" + fname + "|" + gender + "|" + str(dob) +  "|" + hex_id + "|" + str(p_rate) +'\r'
    ser_port.write(str.encode(response))
    msgout = ser_port.read(1000)
    time.sleep(0.1)
    print(msgout)
    
    ser_port.write(str.encode("\x1A"))
    read_port = ser_port.read(5)

    print("response sent")

