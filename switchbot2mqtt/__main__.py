import logging
from switchbot2mqtt import MqttListener

if __name__ == '__main__':
  logging.info("Starting listener")
  listener = MqttListener(
    broker="xx.xx.xx.xx",
    port=1883,
    username="xxxx",
    password="xxxx",
    topic_prefix="switchbot2mqtt"
  )
  listener.run()
