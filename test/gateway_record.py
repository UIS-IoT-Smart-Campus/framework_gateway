#!/home/pi/Documents/framework/venv/bin/python
import random
import time
import psutil
import json
from datetime import datetime
import pytz
from paho.mqtt import client as mqtt_client

"""
Parameters of publish code from python
Source: https://www.emqx.io/blog/how-to-use-mqtt-in-python
"""


#Conection and broker parameters
broker = 'localhost'
port = 1883
topic = "gateway/record"
client_id = 'python-mqtt-GAT001'
#Message Parameter
keys = ["cpu","ram"]
values = [0,0]
delay_time = 1800



"""
Function to connect to mqtt broker
"""
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

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
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        values = []
        values.append(cpu_usage)
        values.append(memory_usage)
        
        tz_Col = pytz.timezone('America/Bogota')
        now = datetime.now(tz_Col)
        current_time = now.strftime("%d-%m-%Y %H:%M:%S")

        msg = {"keys":keys,"values":values,"time":current_time}
        msg_json = json.dumps(msg)
        result = client.publish(topic, msg_json)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            pass
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            pass
            #print(f"Failed to send message to topic {topic}")
        msg_count += 1
        time.sleep(delay_time)


def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)

if __name__ == '__main__':
    run()
