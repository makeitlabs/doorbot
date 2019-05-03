import paho.mqtt.client as mqtt
import os
import datetime
import sys
sys.path.insert(0, '../')
import qsetup
from qsetup import botlog

def do_update(message):
    now = datetime.datetime.now()
    botlog.info(message)
    os.system(qsetup.acl_update_script)

def on_connect(client, userdata, flags, rc):
    do_update("MQTT ACL updater connected, updating")

def on_message(client, userdata, message):
    if message.topic == qsetup.mqtt_acl_update_topic:
        do_update("MQTT ACL updater triggered, updating")


botlog.info("MQTT ACL updater starting")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.tls_set(ca_certs=qsetup.mqtt_ssl_ca_cert, certfile=qsetup.mqtt_ssl_client_cert, keyfile=qsetup.mqtt_ssl_client_key)
client.connect(qsetup.mqtt_broker_address, port=qsetup.mqtt_broker_port)

client.subscribe(qsetup.mqtt_listen_topic, 2)

client.loop_forever()

botlog.info("MQTT ACL updater exiting")


