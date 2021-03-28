from tinydb import TinyDB, Query

import json


class Persistence():

    """
    Msg is a json format
    device_tag: Tag for device register
    key: Is the key of the value
    value: Is the value for store
    """
    def insert_message(self,msg,device):        
        if msg["device_tag"] and msg["key"] and msg["value"] and msg["table"]:
            device_tag = str(msg["device_tag"])
            db = TinyDB('flaskr/device_data/'+device.tag+"/"+device_tag+".json")
            table = db.table(str(msg["table"]))
            table.insert({str(msg["key"]):str(msg["value"]),"time":str(msg["time"])})

