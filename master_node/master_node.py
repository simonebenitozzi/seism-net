import asyncio
from dataclasses import dataclass
import json
from queue import Queue
import random

from paho.mqtt.client import Client

broker = 'localhost'
#broker = "broker.emqx.io"
port = 1883
topic = "/seism/+/events"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
# username = 'emqx'
# password = 'public'


@dataclass
class MQTTSeismicEvent:
    magnitude: float
    frequency: float
    mercalli: int
    sensor_id: str


class NewMQTTApplication:

    def __init__(self, host, port, client_id) -> None:
        self.host = host
        self.port = port
        self.client_id = client_id
        self.client = Client(client_id=self.client_id)
        self.client.on_connect = self.__subscribe
        self.client.on_message = self.__handle_message
        self.__event_queue = Queue()

    def connect(self):
        self.client.connect(host=self.host,
                            port=self.port)

    async def stop(self):
        self.client.disconnect()

    async def loop(self, ctx):
        while ctx.application.running:
            self.client.loop()
            while not self.__event_queue.empty():
                ev = self.__event_queue.get()
                await ctx.job.data['on_event_callback'](ev)
            await asyncio.sleep(3)
        print("MQTT Exiting")

    def __subscribe(self, client, userdata, flags, rc):
        self.client.subscribe("/seism/+/events")

    def __handle_message(self, client, userdata, msg):
        topic = msg.topic
        topic_parts = topic.split("/")
        if topic_parts[1] == "seism" and topic_parts[-1] == "events":
            sensor_id = topic_parts[2]
            data = json.loads(msg.payload.decode('ascii'))
            event = MQTTSeismicEvent(
                magnitude=float(data['magnitude']),
                frequency=float(data['frequency']),
                mercalli=int(data['mercalli']),
                sensor_id=sensor_id)
            self.__event_queue.put(event)


# class MQTTAppplication:

#     def __init__(self, host, port, client_id) -> None:
#         self.host = host
#         self.port = port
#         self.client_id = client_id
#         self.client = Client(self.host, port=self.port,
#                              client_id=self.client_id)
#         self.events_topic = "/seism/+/events"

#     def start(self, event_loop: asyncio.BaseEventLoop, seism_logger):
#         pass
#         # task = event_loop.create_task(
#         #     self.handle_seismic_event_msg(messages, seism_logger))
#         # tasks.add(task)

#     async def stop(self):
#         print("done")
#         await self.client.disconnect()
#         print("done")
#         await self.client.force_disconnect()

#     async def handle_seismic_event_msg(self, ctx):
#         message_generator = self.client.filtered_messages(self.events_topic)
#         await self.client.connect()
#         await self.client.subscribe(self.events_topic)
#         async with message_generator as messages:
#             async for message in messages:
#                 data = json.loads(message.payload.decode())
#                 sensor_id = message.topic.split("/")[2]
#                 event = MQTTSeismicEvent(
#                     magnitude=float(data['magnitude']),
#                     frequency=float(data['frequency']),
#                     mercalli=int(data['mercalli']),
#                     sensor_id=sensor_id)
#                 await ctx.job.data['on_event_callback'](event)
#                 # await self.seism_logger.log_quake(frequency=data['frequency'],
#                 #                                   magnitude=data['magnitude'],
#                 #                                   mercalli=data['mercalli'],
#                 #                                   sensor_id=sensor_id)


# # async def main():
# #     seism_watch = SeismAlertWatch(60)
# #     logger = SeismLogger(host="149.132.178.180", database='sbenitozzi',
# #                          username="sbenitozzi", password="iot889407")
# #     await logger.connect(asyncio.get_event_loop())
# #     app = MQTTAppplication(broker, port, 'master_node')
# #     await asyncio.gather(*await app.start(asyncio.get_event_loop(), logger), seism_watch.start(asyncio.get_event_loop()))

# # if __name__ == "__main__":
# #     asyncio.run(main())
