import os

from flask import Flask

def create_app(test_config=None):
    #Create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    #Set app configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        SQLALCHEMY_DATABASE_URI='sqlite:////tmp/test.db',
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
    from . import mqtt
    mqtt.init_app(app)
    
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
        
    return app