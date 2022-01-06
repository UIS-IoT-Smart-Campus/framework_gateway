from tinydb import TinyDB, Query

from models import User,Device,Topic
from app import db

import json
from datetime import datetime
from paho.mqtt import client as mqtt_client
import configparser



class Persistence():

    

    """
    Msg is a json format
    device_tag: Tag for device
    keys: Is the keys of the values
    values: Is the values for store
    """
    def insert_message(self,msg,device):        
        if msg["tag"] and msg["content"] and msg["topic"]:
            tag = str(msg["tag"])
            topic = str(msg["topic"])
            db_t = TinyDB('device_data/'+device.tag+"/"+tag+".json")
            table = db_t.table(topic)
            values = msg["content"]
            values["time"] = msg["time"]
            table.insert(values)
            topic = Topic.query.filter_by(topic=topic).first()
            device = Device.query.filter_by(tag=tag).first()
            if topic is None:
                topic = Topic(topic=topic,active_devices=1)
            else:
                add = True
                for top_dev in device.topics:
                    if top_dev.topic == topic.topic:
                        add = False
                if add:
                    topic.active_devices += 1
                topic.last_update = datetime.utcnow()
            
            device.topics.append(topic)            
            db.session.add(device)
            db.session.commit()

            config = configparser.ConfigParser()
            config.readfp(open('init.cfg'))
            standalone = config.getboolean('DEFAULT','standalone')
            if standalone:
                #Send message to MQTT broker
                if msg["time"]:
                    msg.pop("time",None)
                msg_json = json.dumps(msg)
                def on_connect(client, userdata, flags, rc):
                    if rc == 0:
                        pass
                        #print("Connected to MQTT Broker!")
                    else:
                        pass
                        #print("Failed to connect, return code %d\n", rc)
                broker = config.get('DEFAULT','brokerIp')
                port = config.get('DEFAULT','brokerPort')
                backend_topic = config.get('DEFAULT','backend_topic')
                MqttClient = config.get('DEFAULT','MqttClient')
                client = mqtt_client.Client(MqttClient)
                client.on_connect = on_connect
                client.connect(broker, port)
                client.publish(backend_topic, msg_json)

    
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
            db_t = TinyDB('device_data/'+device.tag+"/"+device.tag+".json")
            table = db_t.table(topic.topic)
            table.truncate()
            return 1
        except:
            return 0


