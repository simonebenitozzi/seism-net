import asyncio
from dataclasses import dataclass
import aiomysql
from master_node import MQTTSeismicEvent
from seism_alert import WebSeismicEvent

@dataclass
class DBConnectionInfo:
    host: str
    database: str
    username: str
    password: str


class DBPool:

    instance = None
    connection_info: DBConnectionInfo = None

    def __init__(self, connection_info: DBConnectionInfo) -> None:
        if not DBPool.instance == None:
            raise Exception("This is a singleton class")
        self.connection_info = connection_info
        self.pool = None

    async def connect(self, event_loop):
        self.pool = await aiomysql.create_pool(host=self.connection_info.host,
                                               user=self.connection_info.username,
                                               password=self.connection_info.password,
                                               db=self.connection_info.database,
                                               loop=event_loop)

    def get_pool(self):
        return self.pool

    async def close(self):
        self.pool.close()
        await self.pool.wait_closed()

    @classmethod
    def get_instance(cls, connection_info: DBConnectionInfo = None,
                     event_loop: asyncio.BaseEventLoop = None):
        if DBPool.instance == None:
            assert not connection_info == None
            assert not event_loop == None
            DBPool.instance = DBPool(connection_info)
            event_loop.run_until_complete(DBPool.instance.connect(event_loop))
        return DBPool.instance


class SeismEventMapper:

    def __init__(self) -> None:
        self.pool = DBPool.get_instance().get_pool()

    async def log_quake(self, seismic_event: MQTTSeismicEvent):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                mySql_insert_query = """
                    INSERT INTO earthquake_detection (frequency, magnitude, mercalli, sensor_id) 
                    VALUES (%s, %s, %s, %s)
                """

                record = (seismic_event.frequency, seismic_event.magnitude,
                          seismic_event.mercalli, seismic_event.sensor_id)
                print("executing query")
                await cur.execute(mySql_insert_query, record)
                await conn.commit()
                print("executed query")

    async def cancel_task(self):
        if self.pool != None:
            self.pool.close()
            await self.pool.wait_closed()


class SeismEventSubscriptionMapper:

    def __init__(self) -> None:
        self.pool = DBPool.get_instance().get_pool()

    async def run_select_query(self, query, params: tuple):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, params)
                rows = await cur.fetchall()
                return rows

    async def run_insert_query(self, query, params: tuple):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                await conn.commit()

    async def insert_coordinates(self, chat_id, latitude, longitude):
        query = """INSERT INTO telegram_subs (chat_id, latitude, longitude)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE latitude=%s, longitude=%s"""
        params = (chat_id, latitude, longitude, latitude, longitude)
        await self.run_insert_query(query, params)
        return True

    async def insert_radius(self, chat_id, radius):
        query = """INSERT INTO telegram_subs (chat_id, radius) VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE radius=%s
                """
        params = (chat_id, radius, radius)
        await self.run_insert_query(query, params)
        return True

    async def get_status(self, chat_id):
        query = """SELECT * FROM telegram_subs WHERE chat_id=%s"""
        params = (chat_id,)
        row = (await self.run_select_query(query, params))[0]
        result = {
            'coordinates': not row['latitude'] == None and not row
            ['longitude'] == None, 'radius': not row['radius'] == None}
        return result

    async def get_all_subs_in_radius(self, latitude, longitude):
        query = """SELECT chat_id, radius, latitude, longitude, 111.045 * DEGREES(ACOS(COS(RADIANS(%s))
                * COS(RADIANS(latitude))
                * COS(RADIANS(longitude) - RADIANS(%s))
                + SIN(RADIANS(%s))
                * SIN(RADIANS(latitude))))
                AS distance_in_km
                FROM telegram_subs
                having distance_in_km <= radius
                """
        params = (latitude, longitude, latitude)
        return await self.run_select_query(query, params)
        
        
