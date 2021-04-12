from flask_mqtt import Mqtt
from flaskr.persistence import Persistence
from flaskr.models.models import DeviceModel
import json



mqtt = Mqtt()
pst = Persistence()

def MQTT_Converter(message):
    return json.loads(message)


#When the client subscribe to broker
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.unsubscribe_all()
    #For get devices data
    mqtt.subscribe('device/data')
    #For get gateway sensor data
    mqtt.subscribe('gateway/record')

#If a message is sent by broker
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    if message.topic == 'device/data':
        print("entro")
        """
        msg = MQTT_Converter(message.payload.decode("utf-8"))
        if msg["device_tag"]:
            device = DeviceModel.get_device_tag(msg["device_tag"])
            if device.id is not None:
                pst.insert_message(msg,device)
            else:
                pass
        else:
            pass
        """
    
    if message.topic == 'gateway/record':
        msg = MQTT_Converter(message.payload.decode("utf-8"))
        pst.insert_gateway_record()



def init_app(app):
    mqtt.init_app(app)