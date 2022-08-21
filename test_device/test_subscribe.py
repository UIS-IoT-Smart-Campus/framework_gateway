import random

import paho.mqtt.client as mqtt

global contador
contador = 0

def contar():
    contador +=1
    print("Mensaje"+str(contador))

def on_connect(client, userdata, flags, rc):
    print("Se conecto con mqtt " + str(rc))
    client.subscribe("test_topic")


def on_message(client, userdata, msg):
    #if msg.topic == "test_topic":
    #    print(f"El mensaje es {str(msg.payload)}")
    print(msg.topic + " " + str(msg.payload))
    print(str(userdata))
    

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_forever()