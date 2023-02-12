#!/usr/bin/env python3

import json
import logging
import os
import paho.mqtt.client as mqtt
import requests
import time
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

API_URL = "https://api.txtlocal.com"

MQTT_HOST = os.environ.get("MQTT_HOST")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))
MQTT_USER = os.environ.get("MQTT_USER")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD")
MQTT_TOPIC_PREFIX = os.environ.get("MQTT_TOPIC_PREFIX", "sms2mqtt")
POLL_INTERVAL = int(os.environ.get("TEXTLOCAL_POLL_INTERVAL", 300))
API_KEY = os.environ.get("TEXTLOCAL_API_KEY")
INBOX_ID = os.environ.get("TEXTLOCAL_INBOX_ID")
INBOX_KEYWORD = os.environ.get("TEXTLOCAL_INBOX_KEYWORD")

last_poll_time = 0

# WLBG8 on 60777


def on_mqtt_connect(client, userdata, flags, rc):
    print("CONNECT")
    logger.info(f"mqtt:connect rc={str(rc)}")


def on_mqtt_message(client, userdata, msg):
    topic, payload = msg.topic, str(msg.payload)
    logger.info(f"mqtt:message topic={topic} payload={payload}")


mqtt_client = mqtt.Client()
if MQTT_USER is not None:
    mqtt_client.username_pw_set(MQTT_USER, password=MQTT_PASSWORD)
mqtt_client.on_connect = on_mqtt_connect
mqtt_client.on_message = on_mqtt_message
mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)


def get_inboxes(api_key):
    url = f"{API_URL}/get_inboxes/?"
    payload = dict(apikey=api_key)
    logger.info(f"get_inboxes api_key={api_key}")
    try:
        r = requests.post(url, data=payload)
        return json.loads(r)
    except:
        return None


def get_messages(api_key, inbox_id):
    global last_poll_time
    url = f"{API_URL}/get_messages/?"
    payload = dict(apikey=api_key, inbox_id=inbox_id, min_time=last_poll_time)
    logger.info(f"get_messages api_key={api_key} inbox_id={inbox_id}")
    try:
        r = requests.post(url, data=payload)
        response = json.loads(r.text)
        if len(response.get("errors", [])):
            return None
        messages, last_message_time = response.get("messages"), response.get("max_time")
        if last_message_time:
            last_poll_time = last_message_time
        return messages
    except Exception as e:
        logger.error(e)
        return None


def build_topic(number):
    return f"{MQTT_TOPIC_PREFIX}/{str(number)}"


def clean_message(text: str):
    if INBOX_KEYWORD:
        text = text.replace(INBOX_KEYWORD, "")
    return str(" ".join(text.split(" "))).strip()


while True:
    messages = get_messages(API_KEY, INBOX_ID)
    if messages:
        for msg in messages:
            topic = build_topic(msg.get("number"))
            payload = clean_message(msg.get("message"))
            resp = mqtt_client.publish(topic, payload, qos=2)
            logger.info(f"mqtt:send topic={topic} payload={payload} resp={resp}")
    logger.info(f"poll:sleep interval={POLL_INTERVAL}")
    mqtt_client.loop()
    time.sleep(POLL_INTERVAL)
