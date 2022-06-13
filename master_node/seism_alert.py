import asyncio
from dataclasses import dataclass
from typing import List
import aiohttp
import logging
import time
from telegram.ext import Job

@dataclass
class WebSeismicEvent:
    magnitude: float
    time: int
    latitude: float
    longitude: float
    depth: float

    @classmethod
    def from_dict(cls, data):
        return WebSeismicEvent(
            magnitude = float(data['properties']['mag']),
            time = int(data['properties']['time']),
            latitude = float(data['geometry']['coordinates'][1]),
            longitude = float(data['geometry']['coordinates'][0]),
            depth = float(data['geometry']['coordinates'][2])
        )


class SeismAlertWatch:

    def __init__(self, interval_s=60) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.interval_s = interval_s
        self.latest_seism_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
        self.running = False
        self.latest_seism_retrieved_time = time.time() * 1000
        self.running = True
        self.last_poll_time = 0

    def start(self, event_loop: asyncio.BaseEventLoop):
        return event_loop.create_task(self.task())

    async def task(self, ctx):
        async with aiohttp.ClientSession() as session:
            while ctx.application.running:
                if time.time() - self.last_poll_time >= self.interval_s:
                    async with session.get(self.latest_seism_url) as response:
                        if response.status == 200:
                            json_data = await response.json()
                            events: List[WebSeismicEvent] = []
                            latest_time = 0
                            for seism_data in json_data.get('features'):
                                events.append(WebSeismicEvent.from_dict(seism_data))
                                latest_time = max(latest_time, events[-1].time)
                            new_events = filter(
                                lambda x: x.time > self.latest_seism_retrieved_time, events)
                            new_events = list(new_events)
                            self.logger.info(f"Retrieved latest quakes: {new_events}")
                            for ev in new_events:
                                await ctx.job.data['on_alert_callback'](ev)
                            self.latest_seism_retrieved_time = latest_time
                    self.last_poll_time = time.time()
                await asyncio.sleep(3)
        print("Seism alert exiting")

    def cancel(self):
        self.running = False
