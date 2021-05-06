from tinydb import TinyDB, Query

from models import User,Device,Topic
from app import db

import json
from datetime import date


class Persistence():

    """
    Msg is a json format
    device_tag: Tag for device
    keys: Is the keys of the values
    values: Is the values for store
    """
    def insert_message(self,msg,device):        
        if msg["device_tag"] and msg["keys"] and msg["values"] and msg["device_topic"]:
            device_tag = str(msg["device_tag"])
            device_topic = str(msg["device_topic"])
            db_t = TinyDB('device_data/'+device.tag+"/"+device_tag+".json")
            table = db_t.table(str(msg["device_topic"]))
            values = {}
            value = 0
            for key in msg["keys"]:
                values[key] = msg["values"][value]
                value+=1
            values["time"] = msg["time"]
            table.insert(values)
            topic = Topic.query.filter_by(topic=device_topic).first()
            if topic is None:
                topic = Topic(topic=device_topic,active_devices=1)
            else:
                topic.active_devices += 1
                topic.last_update = date.today()
            device = Device.query.filter_by(tag=device_tag).first()
            device.topics.append(topic)            
            db.session.add(device)
            db.session.commit()



    
    def insert_gateway_record(self,msg):
        db = TinyDB('device_data/Gateway/gateway_records.json')
        table = db.table('gateway_records')
        values = {}
        value = 0
        for key in msg["keys"]:
            values[key] = msg["values"][value]
            value+=1
        values["time"] = msg["time"]
        table.insert(values)
    
    @staticmethod
    def get_gateway_records():
         db = TinyDB('device_data/Gateway/gateway_records.json')
         table = db.table('gateway_records')
         data = table.all()
         return data
    

    @staticmethod
    def delete_device_topic(device,topic):
        try:
            print(topic.topic)
            db_t = TinyDB('device_data/'+device.tag+"/"+device.tag+".json")
            table = db_t.table(topic.topic)
            table.truncate()
            return 1
        except:
            return 0


