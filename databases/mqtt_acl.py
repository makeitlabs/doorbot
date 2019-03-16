import paho.mqtt.client as mqtt
import os

broker_address='auth'
broker_port=1883
ssl_ca_cert='/home/pi/ssl/ca.crt'
ssl_client_cert='/home/pi/ssl/client.crt'
ssl_client_key='/home/pi/ssl/client.key'

update_script='/home/pi/doorbot/databases/auto_door_list.sh'

def do_update():
    os.system(update_script)

def on_connect(client, userdata, flags, rc):
    do_update()

def on_message(client, userdata, message):
    if message.topic == 'ratt/control/broadcast/acl/update':
        do_update()


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.tls_set(ca_certs=ssl_ca_cert, certfile=ssl_client_cert, keyfile=ssl_client_key)
client.connect(broker_address, port=broker_port)

client.subscribe('ratt/control/broadcast/#', 2)

client.loop_forever()

    

