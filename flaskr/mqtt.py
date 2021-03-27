from flask_mqtt import Mqtt
from .persistence import Persistence



mqtt = Mqtt()
pst = Persistence()


#When the client subscribe to broker
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.unsubscribe_all()
    mqtt.subscribe('device/data')

#If a message is sent by broker
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    msg = message.payload.decode("utf-8")
    print(msg)
    pst.insert_message(msg)


def init_app(app):
    mqtt.init_app(app)