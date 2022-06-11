import asyncio
import json
import random
from asyncio_mqtt import Client
from db import SeismLogger


broker = 'localhost'
#broker = "broker.emqx.io"
port = 1883
topic = "/seism/+/events"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
# username = 'emqx'
# password = 'public'


class MQTTAppplication:

    def __init__(self, host, port, client_id) -> None:
        self.host = host
        self.port = port
        self.client_id = client_id
        self.client = Client(self.host, port=self.port,
                             client_id=self.client_id)

    async def start(self, event_loop: asyncio.BaseEventLoop, seism_logger):
        tasks = set()
        topic = "/seism/+/events"

        messages = self.client.filtered_messages(topic)
        task = event_loop.create_task(
            self.handle_seismic_event_msg(messages, seism_logger))
        tasks.add(task)
        await self.client.connect()
        await self.client.subscribe(topic)

        return tasks

    async def handle_seismic_event_msg(self, message_generator, logger: SeismLogger):
        async with message_generator as messages:
            async for message in messages:
                data = json.loads(message.payload.decode())
                sensor_id = message.topic.split("/")[2]
                print(f'{sensor_id}:{data}')
                await logger.log_quake(frequency=data['frequency'],
                                       magnitude=data['magnitude'],
                                       mercalli=data['mercalli'],
                                       sensor_id=sensor_id)


async def main():
    logger = SeismLogger(host="149.132.178.180", database='sbenitozzi',
                         username="sbenitozzi", password="iot889407")
    await logger.connect(asyncio.get_event_loop())
    app = MQTTAppplication(broker, port, 'master_node')
    await asyncio.gather(*await app.start(asyncio.get_event_loop(), logger))

if __name__ == "__main__":
    asyncio.run(main())
