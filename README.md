# Framework IoT gateway
It's a python framework gateway for IoT based on Flask framework and MQTT broker.

## Built with
- Python 3.7.3
- Flask 1.1.2
- paho-mqtt 1.5.1
- SQLite3
- TinyDB 4.4.0
- Eclipse Mosquitto

## Important: Create database

Inside the folder flaskr enter on python shell and execute the following commands: 

- from app import db
- db.create_all()

## For run on development enviroment

Create the next temporal enviroment variables:

- export FLASK_APP=app
- export FLASK_ENV=development
- export FLASK_DEBUG=0

Inside the folder flaskr run the following comand:

flask run -h 0.0.0.0 -p 5000

You can remplace the port in -p XXXX. 