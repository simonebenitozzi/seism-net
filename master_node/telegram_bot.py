import asyncio
import logging
from queue import Queue

from telegram import Update, Bot
import telegram
import telegram.ext
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from seism_alert import SeismAlertWatch

from geopy.geocoders import Nominatim

from db import SeismEventSubscriptionMapper, DBPool, DBConnectionInfo, SeismEventMapper
from master_node import SeismicEvent, NewMQTTApplication


telegram_token = "5512730466:AAF8CiMl8yUz3Kg1og6oPW9f6MoPtBUHhSg"
my_chat_id = "152601730"  # for testing

db_host = '149.132.178.180'
db_name = 'sbenitozzi'
db_user = 'sbenitozzi'
db_password = 'iot889407'


geolocator_username = "overlap@group.com"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

connection_info = DBConnectionInfo(
    host=db_host, database=db_name, username=db_user, password=db_password)
DBPool.get_instance(connection_info, asyncio.get_event_loop())


# Converte coordinate da decimali a gradi
def decdeg2dms(dd):
    is_positive = dd >= 0
    dd = abs(dd)
    minutes, seconds = divmod(dd*3600, 60)
    degrees, minutes = divmod(minutes, 60)
    degrees = degrees if is_positive else -degrees
    return (degrees, minutes, seconds)


async def event_updater():
    queue = Queue()
    async with Bot(telegram_token) as test_bot:
        async with telegram.ext.Updater(test_bot, queue) as updater:
            await updater.bot.send_message(chat_id=my_chat_id, text='Hello')


class EarthquakeTelegramBot:

    def __init__(self) -> None:

        self.logger = logging.getLogger(self.__class__.__name__)
        self.application = ApplicationBuilder().token(telegram_token).build()
        self.start_handler = CommandHandler('start', self.start_command)
        self.help_handler = CommandHandler('help', self.help_command)

        self.city_handler = CommandHandler('city', self.city_command)
        self.zipcode_handler = CommandHandler('zipcode', self.zipcode_command)
        self.coordinates_handler = CommandHandler(
            'coordinates', self.coordinates_command)
        self.radius_handler = CommandHandler('radius', self.radius_command)
        self.status_handler = CommandHandler('status', self.status_command)

        self.text_handler = MessageHandler(
            filters.TEXT & (~filters.COMMAND), self.unknown_command)
        self.unknown_handler = MessageHandler(
            filters.COMMAND, self.unknown_command)

        self.application.add_handler(self.start_handler)
        self.application.add_handler(self.help_handler)

        self.application.add_handler(self.city_handler)
        self.application.add_handler(self.zipcode_handler)
        self.application.add_handler(self.coordinates_handler)
        self.application.add_handler(self.radius_handler)
        self.application.add_handler(self.status_handler)

        self.application.add_handler(self.text_handler)
        self.application.add_handler(self.unknown_handler)

        self.seism_alert_watch = SeismAlertWatch(60)

        self.mqtt_app = NewMQTTApplication(
            'localhost', 1883, 'master_node')
        self.mqtt_app.connect()
        self.seismic_event_mapper = SeismEventMapper()
        self.seism_subscription_mapper = SeismEventSubscriptionMapper()

        self.application.post_init = self.schedule_auxiliary_tasks
        self.application.run_polling(stop_signals=None, close_loop=False)
        asyncio.run(DBPool.get_instance().close())
        asyncio.run(self.mqtt_app.stop())

    async def schedule_auxiliary_tasks(self, args):
        self.application.job_queue.run_custom(self.seism_alert_watch.task, {}, data={
            'on_alert_callback': self.on_seism_api_event
        })
        self.application.job_queue.run_custom(self.mqtt_app.loop, {}, data={
            'on_event_callback': self.on_mqtt_event
        })

    async def alert_users(self, event: SeismicEvent):
        to_alert_users = await self.seism_subscription_mapper.get_all_subs_in_radius(event.latitude, event.longitude)
        geolocator = Nominatim(user_agent=geolocator_username)
        event_location_name = geolocator.reverse(
            f"{event.latitude},{event.longitude}", exactly_one=True)
        text = f"""
There has been an earthquake in range of your selection:
Location: {event_location_name.address}
Magnitude: {event.magnitude}
Latitude: {event.latitude}
Longitude: {event.longitude}
        """
        for to_alert in to_alert_users:
            await self.application.updater.bot.send_message(to_alert['chat_id'], text)

    async def on_mqtt_event(self, event: SeismicEvent):
        self.logger.info('Received seismic event')
        await self.seismic_event_mapper.log_quake(event)
        await self.alert_users(event)

    async def on_seism_api_event(self, event: SeismicEvent):
        await self.alert_users(event)

    async def start_command(self, update: Update, context):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Welcome on the overlap Bot!\nPlease enter your Location and a Radius of your choice, using the apposite commands. /help")

    async def help_command(self, update: Update, context):
        help_message = f"""I can help you subscribe for Earthquakes updates\n\nYou can control me by sending these commands:\n
    /city - Enter your city (must be followed by a city name)
    /zipcode - Enter your zipcode (must be followed by a zipcode)
    /coordinates - Enter your coordinates (must be followed by latitude and longitude)
    /radius - Enter a radius around your location in kilometers (must be followed by a positive number)
    /status - Get info about the information you inserted"""
        await context.bot.send_message(chat_id=update.effective_chat.id, text=help_message)

    async def city_command(self, update: Update, context):
        chat_id = update.effective_chat.id
        text = update.message.text
        if len(text) < 7:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="No city inserted")
            return

        city = text[6:]
        geolocator = Nominatim(user_agent=geolocator_username)
        loc = geolocator.geocode(city)

        if loc == None:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Error: your city was not found")
        else:
            await self.seism_subscription_mapper.insert_coordinates(chat_id, loc.latitude, loc.longitude)
            status = await self.seism_subscription_mapper.get_status(chat_id)
            if status['radius']:  # checks if radius is already inserted
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text="Your Location has been updated!\nYou're ready to receive your updates!")
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text="Your Location has been updated!\nRadius has not been inserted yet")

    async def zipcode_command(self, update: Update, context):
        chat_id = update.effective_chat.id
        text = update.message.text
        if len(text.split()) < 2:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="No zipcode inserted")
            return

        zipcode = text.split[2]
        geolocator = Nominatim(user_agent=geolocator_username)
        loc = geolocator.geocode(zipcode)
        if loc == None:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text="The zipcode you entered was not found.")
        else:
            await self.seism_subscription_mapper.insert_coordinates(chat_id, loc.latitude, loc.longitude)
            status = await self.seism_subscription_mapper.get_status(chat_id)
            if status['radius']:  # checks if radius is already inserted
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Your Location has been updated!\nYou're ready to receive your updates!")
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Your Location has been updated!\nRadius has not been inserted yet")

    async def coordinates_command(self, update: Update, context):
        chat_id = update.effective_chat.id
        text = update.message.text

        if len(text.split()) < 3:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Not enough parameters: please enter both Latitude and Longitude")
            return

        try:
            latitude = float(text.split()[1])
            longitude = float(text.split()[2])
        except ValueError:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid input: Latitude and Longitude must be numeric values")
            return

        if abs(latitude) > 90:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Latitude not valid: please insert a number between -90 and 90")
            return

        if abs(longitude) > 180:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Longitude not valid: please insert a number between -180 and 180")
            return

        if self.seism_subscription_mapper.log_coordinates(chat_id, latitude, longitude):
            status = await self.seism_subscription_mapper.get_status(chat_id)
            if status['radius']:  # checks if radius is already inserted
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Your Location has been updated!\nYou're ready to receive your updates!")
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Your Location has been updated!\nRadius has not been inserted yet")

    async def radius_command(self, update: Update, context):
        chat_id = update.effective_chat.id
        text = update.message.text

        if len(text.split()) < 2:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Radius not inserted")
            return

        try:
            radius = float(text.split()[1])
        except ValueError:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid input: Radius must be a numeric value")
            return

        if radius < 0:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Radius not valid: please insert a positive number")
            return

        if await self.seism_subscription_mapper.insert_radius(chat_id, radius):
            status = await self.seism_subscription_mapper.get_status(chat_id)
            if status['coordinates']:  # checks if coordinates are already inserted
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Radius has been updated!\nYou're ready to receive your updates!")
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Radius has been updated!\nYour Location has not been inserted yet")

    async def status_command(self, update: Update, context):
        chat_id = update.effective_chat.id

        status = await self.seism_subscription_mapper.get_status(chat_id)
        # checks if coordinates and Radius are already inserted
        if status['coordinates'] and status['radius']:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You have already inserted Location and Radius.\nYou're ready to receive your updates!")
        elif not status['coordinates'] and not status['radius']:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You haven't inserted your Location and Radius yet. /help")
        elif not status['coordinates']:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You haven't inserted your Location yet. /help")
        elif not status['radius']:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You haven't inserted your Radius yet. /help")

    async def unknown_command(self, update: Update, context):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command. /help")


if __name__ == '__main__':

    bot = EarthquakeTelegramBot()

    # asyncio.run(bot.start())
