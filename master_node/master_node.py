import asyncio
from dataclasses import dataclass
import json
from queue import Queue
import random

from paho.mqtt.client import Client

broker = 'localhost'
port = 1883
topic = "/seism/+/events"
client_id = f'python-mqtt-{random.randint(0, 100)}'

@dataclass
class SeismicEvent:
    magnitude: float
    frequency: float
    mercalli: int
    time: int
    latitude: float
    longitude: float
    depth: float
    sensor_id: str
    @classmethod
    def from_dict(cls, data):
        return SeismicEvent(
            magnitude = float(data['properties']['mag']),
            time = int(data['properties']['time']),
            latitude = float(data['geometry']['coordinates'][1]),
            longitude = float(data['geometry']['coordinates'][0]),
            depth = float(data['geometry']['coordinates'][2]),
            mercalli = None,
            sensor_id= data['properties']['net'],
            frequency=None,
        )


class MQTTApplication:

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
                print(ev)
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
            print(data)
            event = SeismicEvent(
                magnitude=float(data['magnitude']),
                frequency=float(data['frequency']),
                mercalli=int(data['mercalli']),
                time=int(data['ts_s']),
                latitude=float(data['lat']),
                longitude=float(data['lng']),
                sensor_id=sensor_id,
                depth = str('NA'))
            self.__event_queue.put(event)
