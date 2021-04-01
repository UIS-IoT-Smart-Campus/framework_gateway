import os

from flask import Flask
from flask_mqtt import Mqtt
from flaskr.persistence import Persistence
from flaskr.models.models import DeviceModel
import json



def create_app(test_config=None):
    #Create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    #Set app configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        FLASK_DEBUG=False,
        MQTT_BROKER_URL='localhost',
        MQTT_BROKER_PORT=1883,
        MQTT_KEEPALIVE=60,
    )


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
        mqtt.subscribe('device/data')

    #If a message is sent by broker
    @mqtt.on_message()
    def handle_mqtt_message(client, userdata, message):
        msg = MQTT_Converter(message.payload.decode("utf-8"))
        if msg["device_tag"]:
            with app.app_context():
                device = DeviceModel.get_device_tag(msg["device_tag"])
            if device.id is not None:
                pst.insert_message(msg,device)
            else:
                print("Error not device")
        else:
            print("Error: Not tag device register")
    
    #Registrar gestion de la base de datos en la app
    from . import db
    db.init_app(app)

    #Registrar espacio de trabajo para login y registro
    from . import auth
    app.register_blueprint(auth.bp)

    #Registrar espacio de tabajo para el index
    from . import index
    app.register_blueprint(index.bp)
    app.add_url_rule('/', endpoint='index')

    #Registrar espacio de tabajo para devices
    from . import device
    app.register_blueprint(device.bp)
    app.add_url_rule('/device', endpoint='index')

    """
    if __name__=="__main__":
        serve(app, host='0.0.0.0',port=5000, url_scheme='https')
    """
        
    return app


