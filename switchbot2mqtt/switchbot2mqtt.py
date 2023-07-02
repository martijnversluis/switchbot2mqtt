import json
import logging
import random
import time

import json
from paho.mqtt import client as mqtt_client
from switchbotpy import Bot

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

class Config:
  def __init__(self, **config):
    self.broker = config.get("broker")
    self.port = config.get("port", None)
    self.topic_prefix = config.get("topic_prefix")
    self.client_id = config.get("client_id", f'switchbot2mqtt-{random.randint(0, 1000)}')
    self.username = config.get("username", None)
    self.password = config.get("password", None)

class CommandHandler:
  def __init__(self, mac_address):
    self.bot = Bot(mac=mac_address, bot_id="unknown", name=f"switchbot2mqtt_{mac_address}")

  def handle_command(self, command):
    self.handle_press(command)
    self.handle_switch(command)
    self.handle_set_hold_time(command)
    self.handle_set_mode(command)

  def handle_press(self, command):
    if command.get("press"):
      logging.debug("bot.press()")
      self.bot.press()

  def handle_switch(self, command):
    switch = command.get("switch", "").lower()

    if switch == "on":
      logging.debug("bot.switch(True)")
      self.bot.switch(True)
    elif switch == "off":
      logging.debug("bot.switch(False)")
      self.bot.switch(False)

  def handle_set_hold_time(self, command):
    hold_time = command.get("hold_time")

    if hold_time is not None:
      logging.debug(f"bot.set_hold_time({hold_time})")
      self.bot.set_hold_time(hold_time)

  def handle_set_mode(self, command):
    if "dual_state" in command and "inverse" in command:
      logging.debug(f'self.bot.set_mode({command["dual_state"]}, {command["inverse"]})')
      self.bot.set_mode(command["dual_state"], command["inverse"])

class MqttListener:
  def __init__(self, **config):
    self.running = True
    self.config = Config(**config)

  def run(self):
    logging.info("Connecting...")
    self.connect()
    logging.info("Connected! Starting...")
    self.client.loop_forever()

  def connect(self):
    self.client = mqtt_client.Client(self.config.client_id)
    self.client.username_pw_set(self.config.username, self.config.password)
    self.client.on_connect =  self.on_connect
    self.client.on_disconnect =  self.on_disconnect
    self.client.connect(self.config.broker, self.config.port)

  def on_connect(self, client, userdata, flags, rc):
    if rc == 0 and client.is_connected():
      logging.info("Connected to MQTT Broker!")
      client.subscribe(f'{self.config.topic_prefix}/#')
      client.on_message = self.on_message
    else:
      logging.error(f'Failed to connect, return code {rc}')

  def on_disconnect(self, client, userdata, rc):
    logging.info("Disconnected with result code: %s", rc)
    reconnect_count = 0
    reconnect_delay = FIRST_RECONNECT_DELAY

    while reconnect_count < MAX_RECONNECT_COUNT:
      logging.info("Reconnecting in %d seconds...", reconnect_delay)
      time.sleep(reconnect_delay)

      try:
        client.reconnect()
        logging.info("Reconnected successfully!")
        return
      except Exception as err:
        logging.error("%s. Reconnect failed. Retrying...", err)

      reconnect_delay *= RECONNECT_RATE
      reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
      reconnect_count += 1

    logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)
    self.running = False

  def on_message(self, client, userdata, msg):
    payload = msg.payload.decode()
    logging.debug(f"Received `{payload}` from `{msg.topic}` topic")

    command = json.loads(payload)
    mac_address = msg.topic[(len(self.config.topic_prefix)+1):]

    logging.info(f"Execute `{command}` for {mac_address}")
    handler = CommandHandler(mac_address)
    handler.handle_command(command)
