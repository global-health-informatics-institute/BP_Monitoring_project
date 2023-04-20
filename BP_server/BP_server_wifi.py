import time
import serial
import mysql.connector as mysql
from flask import Flask, request
from configparser import ConfigParser
import json

app = Flask(__name__)

def initialize_settings():
    settings = {}
    with open("/home/pi/BP_Monitoring_project/BP_server/conn.config") as json_file:
        settings = json.load(json_file)
    return settings

settings = initialize_settings()

db = mysql.connect(
    host=settings["server_db"]["host"],
    user = settings["server_db"]["user"],
    passwd= settings["server_db"]["passwd"],
    database= settings["server_db"]["database"]
    )
cur = db.cursor()

@app.route('/BPserver', methods = ['GET', 'POST'])
def BPserver():
    vitals = request.args.get('vitals')
    print(vitals)
    sep = '|'
    if sep in vitals:
        ele = vitals
        parseSms(vitals)
    return(vitals)

def parseSms(ele):
    splitdata = ele.split("|")
    print(splitdata)
    cur.execute("INSERT INTO smsload (n_id, vitals, bp_cat, fullname, gender, dob)"
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (splitdata[0], splitdata[1], splitdata[2], splitdata[3], splitdata[4], splitdata[5]))
    db.commit()
    print("sent to database")
    
if __name__ == '__main__':
    app.run(
        settings["flask_app"]["host"],
        settings["flask_app"]["port"]
        )