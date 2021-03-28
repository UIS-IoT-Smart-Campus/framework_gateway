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
    mqtt.subscribe('device/data')

#If a message is sent by broker
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    msg = MQTT_Converter(message.payload.decode("utf-8"))
    if msg["device_tag"]:
        device = DeviceModel.get_device_tag(msg["device_tag"])
        if device.id is not None:
            pst.insert_message(msg,device)
        else:
            print("Error not device")
    else:
        print("Error: Not tag device register")


def init_app(app):
    mqtt.init_app(app)