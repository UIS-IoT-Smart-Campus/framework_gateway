from tinydb import TinyDB, Query

import json


class Persistence():

    """
    Msg is a json format
    device_tag: Tag for device register
    keys: Is the keys of the values
    values: Is the values for store
    """
    def insert_message(self,msg,device):        
        if msg["device_tag"] and msg["keys"] and msg["values"] and msg["table"]:
            device_tag = str(msg["device_tag"])
            db = TinyDB('flaskr/device_data/'+device.tag+"/"+device_tag+".json")
            table = db.table(str(msg["table"]))
            values = {}
            value = 0
            for key in msg["keys"]:
                values[key] = msg["values"][value]
                value+=1
            values["time"] = msg["time"]
            table.insert(values)

