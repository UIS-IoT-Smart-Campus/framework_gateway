import os

from flask import Flask
from flask_mqtt import Mqtt
from persistence import Persistence
#from flaskr.models.models import DeviceModel
from flask_sqlalchemy import SQLAlchemy
import json


#Initial configuration
test_config = None


#Create and configure the app
app = Flask(__name__, instance_relative_config=True)

#DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),

#Set app configuration
app.config.from_mapping(
    SECRET_KEY='dev',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_DATABASE_URI='sqlite:///instance/db.sqlite3',    
    MQTT_BROKER_URL='localhost',
    MQTT_BROKER_PORT=1883,
    MQTT_KEEPALIVE=60,
)

#Create Database
db = SQLAlchemy(app)

if test_config is None:
    #Load the instance config, if it exists, when not testing
    app.config.from_pyfile('config.py', silent=True)
else:
    #load the test config if passed in
    app.config.from_mapping(test_config)


#ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

#Models
from models import User,Device

#Registrar espacio de trabajo para login y registro
import auth
app.register_blueprint(auth.bp)

#Registrar espacio de trabajo para el index
import index
app.register_blueprint(index.bp)
app.add_url_rule('/', endpoint='index')

#Registrar espacio de tabajo para devices
import device
app.register_blueprint(device.bp)
app.add_url_rule('/device', endpoint='index')

#Registrar espacio de tabajo para devices
import gateway
app.register_blueprint(gateway.bp)
app.add_url_rule('/gateway', endpoint='index')


#MQTT registration
#from . import mqtt
#mqtt.init_app(app)
mqtt = Mqtt(app)
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
        msg = MQTT_Converter(message.payload.decode("utf-8"))
        if msg["device_tag"]:
            with app.app_context():
                device = Device.query.filter_by(tag= msg["device_tag"]).first()
            if device is not None:
                pst.insert_message(msg,device)
            else:
                print("Error not device")
        else:
            print("Error: Not tag device register")
        
    if message.topic == 'gateway/record':
        msg = MQTT_Converter(message.payload.decode("utf-8"))
        pst.insert_gateway_record(msg)
    
#Registrar gestion de la base de datos en la app
#from . import db
#db.init_app(app)
