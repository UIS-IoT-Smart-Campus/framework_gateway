from tinydb import TinyDB, Query

from tinydb import TinyDB, Query
from .models.models import DeviceModel

import json


class Persistence():

    def MQTT_Converter(self,message):
        return json.loads(message)

    """
    Msg is a json format
    device_tag: Tag for device register
    key: Is the key of the value
    value: Is the value for store
    """
    def insert_message(self,message):
        msg = self.MQTT_Converter(message)
        if msg["device_tag"] and msg["key"] and msg["value"] and msg["table"]:
            device_tag = msg["device_tag"]
            device = DeviceModel().get_device_tag(tag=device_tag)
            if device.id is not None:
                db = TinyDB('flaskr/device_data/'+device.tag+"/"+device_tag+".json")
                db.table(msg["table"])
                db.insert({msg["key"]:msg["value"]})

