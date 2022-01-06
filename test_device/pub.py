import random
import time
import requests
import json
from datetime import datetime
import pytz
from paho.mqtt import client as mqtt_client



#Conection and broker parameters
broker = '192.168.0.125'
port = 1883
topic = "device/message"
client_id = 'python-mqtt-test'

#Message Parameter
device_tag = "A001"
keys = ["temp","feels_like","pressure","humidity"]
values = [0,0,0,0]
device_topic = "temp_lebrija"
delay_time = 1



"""
Function to create the message.
"""
def get_message():
    resp = requests.get('http://api.openweathermap.org/data/2.5/weather?q=Lebrija,co&APPID=d205eb86c19c0897cf10319745ce283d&units=metric')
    if resp.status_code != 200:
        # This means something went wrong.
        values = [0,0,0,0]
        pass
    else:
        temp= resp.json()["main"]["temp"]
        feels_like = resp.json()["main"]["feels_like"]
        pressure = resp.json()["main"]["pressure"]
        humidity = resp.json()["main"]["humidity"]
        values = []
        values.append(temp)
        values.append(feels_like)
        values.append(pressure)
        values.append(humidity)
    
    tz_Col = pytz.timezone('America/Bogota')
    now = datetime.now(tz_Col)
    current_time = now.strftime("%d-%m-%Y %H:%M:%S")

    msg = {"tag":device_tag,"topic":device_topic,"keys":keys,"values":values,"time":current_time}
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
    while msg_count<1:
        try:
            msg = get_message()
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