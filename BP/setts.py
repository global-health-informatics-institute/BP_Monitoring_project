import json

def initialize_settings():
    settings = {}
    with open("/home/pi/BP_Monitoring_project/BP/utils/conn.config") as json_file:
        settings = json.load(json_file)
    return settings
