#!/home/pi/Documents/framework/venv/bin/python
import random
import time
import requests
import json
from datetime import datetime
import pytz
from paho.mqtt import client as mqtt_client


#TEST
broker = 'localhost'
port = 1883
topic = "device/data"
client_id = 'python-mqtt-A001'
#Message Parameter
tag = "A001"
msg_topic = "temp_lebrija"
content = {"temp":0,"feels_like":0,"pressure":0,"humidity":0}
delay_time = 3600

"""
Function to create the message.
"""
def get_message():
    
    tz_Col = pytz.timezone('America/Bogota')
    now = datetime.now(tz_Col)
    current_time = now.strftime("%d-%m-%Y %H:%M:%S")

    msg = {"tag":tag,"topic":msg_topic,"content":content,"time":current_time}

    msg_json = json.dumps(msg)
    return msg_json
    

"""
Function to connect to mqtt broker
"""
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            pass
            #print("Connected to MQTT Broker!")
        else:
            pass
            #print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

"""
Function to publish messages to MQTT broker
"""
def publish(client):
    msg_count = 0
    while True:
        try:
            msg = get_message()
            print(msg)
            result = client.publish(topic, msg)
            # result: [0, 1]
            status = result[0]
            if status == 0:
                pass
                #print(f"Send `{msg}` to topic `{topic}`")
            else:
                pass
                #print(f"Failed to send message to topic {topic}")
            msg_count += 1
        except:
            pass
        time.sleep(delay_time)


def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)

if __name__ == '__main__':
    run()
