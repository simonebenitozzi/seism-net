import aiomysql


class SeismLogger:

    def __init__(self, host, database, username, password) -> None:
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.pool = None

    async def connect(self, event_loop):
        self.pool = await aiomysql.create_pool(host=self.host,
                                               user=self.username,
                                               db = self.database,
                                               password=self.password, loop=event_loop
                                               )
    
    async def log_quake(self, frequency, magnitude, mercalli, sensor_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                mySql_insert_query = """
                    INSERT INTO earthquake_detection (frequency, magnitude, mercalli, sensor_id) 
                    VALUES (%s, %s, %s, %s)
                """

                record = (frequency, magnitude, mercalli, sensor_id)
                print("executing query")
                await cur.execute(mySql_insert_query, record)
                await conn.commit()
                print("executed query")



    async def cancel_task(self):
        if self.pool != None:
            self.pool.close()
            await self.pool.wait_closed()
