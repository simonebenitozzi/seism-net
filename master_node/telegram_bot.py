import asyncio
import logging
from queue import Queue

from telegram import Update, Bot
import telegram
import telegram.ext
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, MessageHandler, filters

import mysql.connector

from geopy.geocoders import Nominatim


telegram_token = "5512730466:AAF8CiMl8yUz3Kg1og6oPW9f6MoPtBUHhSg"
my_chat_id = "152601730" # for testing

db_host = '149.132.178.180'
db_name = 'sbenitozzi'
db_user = 'sbenitozzi'
db_password = 'iot889407'

geolocator_username = "overlap@group.com"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Converte coordinate da decimali a gradi
def decdeg2dms(dd):
    is_positive = dd >= 0
    dd = abs(dd)
    minutes,seconds = divmod(dd*3600,60)
    degrees,minutes = divmod(minutes,60)
    degrees = degrees if is_positive else -degrees
    return (degrees,minutes,seconds)

async def start_command(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Welcome on the overlap Bot!\nPlease enter your Location and a Radius of your choice, using the apposite commands. /help")

async def help_command(update: Update, context: CallbackContext.DEFAULT_TYPE):
    help_message = f"""I can help you subscribe for Earthquakes updates\n\nYou can control me by sending these commands:\n
/city - Enter your city (must be followed by a city name)
/zipcode - Enter your zipcode (must be followed by a zipcode)
/coordinates - Enter your coordinates (must be followed by latitude and longitude)
/radius - Enter a radius around your location (must be followed by a positive number)
/status - Get info about the information you inserted"""
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_message)


async def city_command(update: Update, context: CallbackContext.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text
    if len(text) < 7:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No city inserted")
        return    

    city = text[6:]
    geolocator = Nominatim(user_agent=geolocator_username)
    loc = geolocator.geocode(city)
    
    if log_coordinates(chat_id, loc.latitude, loc.longitude):
        status = get_status(chat_id)
        if status[1]:   #checks if radius is already inserted
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Your Location has been updated!\nYou're ready to receive your updates!")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Your Location has been updated!\nRadius has not been inserted yet")
        
async def zipcode_command(update: Update, context: CallbackContext.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text
    if len(text.split()) < 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No zipcode inserted")
        return    

    zipcode = text.split[2]
    geolocator = Nominatim(user_agent=geolocator_username)
    loc = geolocator.geocode(zipcode)
    
    if log_coordinates(chat_id, loc.latitude, loc.longitude):
        status = get_status(chat_id)
        if status[1]:   #checks if radius is already inserted
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Your Location has been updated!\nYou're ready to receive your updates!")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Your Location has been updated!\nRadius has not been inserted yet")
        
async def coordinates_command(update: Update, context: CallbackContext.DEFAULT_TYPE):
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

    if log_coordinates(chat_id, latitude, longitude):
        status = get_status(chat_id)
        if status[1]:   #checks if radius is already inserted
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Your Location has been updated!\nYou're ready to receive your updates!")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Your Location has been updated!\nRadius has not been inserted yet")
        

async def radius_command(update: Update, context: CallbackContext.DEFAULT_TYPE):
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

    
    if log_radius(chat_id, radius):
        status = get_status(chat_id)
        if status[0]:   #checks if coordinates are already inserted
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Radius has been updated!\nYou're ready to receive your updates!")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Radius has been updated!\nYour Location has not been inserted yet")

async def status_command(update: Update, context: CallbackContext.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    status = get_status(chat_id)
    if status[0] and status[1]:   #checks if coordinates and Radius are already inserted
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You have already inserted Location and Radius.\nYou're ready to receive your updates!")
    elif not status[0] and not status[1]:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You haven't inserted your Location and Radius yet. /help")
    elif not status[0]:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You haven't inserted your Location yet. /help")
    elif not status[1]:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You haven't inserted your Radius yet. /help")

async def unknown_command(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command. /help")

def log_coordinates(chat_id, latitude, longitude):
    try:
        connection = mysql.connector.connect(host=db_host,
                                             database=db_name,
                                             user=db_user,
                                             password=db_password)
        cursor = connection.cursor()
        mySql_insert_query = """INSERT INTO telegram_subs (chat_id, latitude, longitude) VALUES(%s, %s, %s) 
                                ON DUPLICATE KEY UPDATE latitude=%s, longitude=%s"""

        record = (chat_id, latitude, longitude, latitude, longitude)
        cursor.execute(mySql_insert_query, record)
        connection.commit()
        print("Coordinates inserted successfully into telegram_subs table")
        return True

    except mysql.connector.Error as error:
        print("Failed to insert into MySQL table\n\t{}".format(error))
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def log_radius(chat_id, radius):
    try:
        connection = mysql.connector.connect(host=db_host,
                                             database=db_name,
                                             user=db_user,
                                             password=db_password)
        cursor = connection.cursor()
        mySql_insert_query = """INSERT INTO telegram_subs (chat_id, radius) VALUES(%s, %s) 
                                ON DUPLICATE KEY UPDATE radius=%s"""

        record = (chat_id, radius, radius)
        cursor.execute(mySql_insert_query, record)
        connection.commit()
        print("Radius inserted successfully into telegram_subs table")
        return True

    except mysql.connector.Error as error:
        print("Failed to insert into MySQL table\n\t{}".format(error))
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_status(chat_id):
    try:
        connection = mysql.connector.connect(host=db_host,
                                             database=db_name,
                                             user=db_user,
                                             password=db_password)
        cursor = connection.cursor()
        mySql_select_query = """SELECT * FROM telegram_subs WHERE chat_id=%s"""

        cursor.execute(mySql_select_query, (chat_id,))
        row = cursor.fetchone()

        status = [False, False]
        if row == None:
            return status
        status[0] = (row[1] != None) and (row[2] != None)
        status[1] = row[3] != None
        return status

    except mysql.connector.Error as error:
        print("Failed to retrieve from MySQL table\n\t{}".format(error))
        return [False, False]

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def retrieve_all_subs():
    try:
        connection = mysql.connector.connect(host=db_host,
                                             database=db_name,
                                             user=db_user,
                                             password=db_password)
        cursor = connection.cursor()
        mySql_select_query = """SELECT * FROM telegram_subs"""

        cursor.execute(mySql_select_query)
        return cursor.fetchall()

    except mysql.connector.Error as error:
        print("Failed to retrieve from MySQL table\n\t{}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def retrieve_subs_in_radius(latitude, longitude):
    return retrieve_all_subs # Da modificare

def build_app():

    application = ApplicationBuilder().token(telegram_token).build()
    start_handler = CommandHandler('start', start_command)
    help_handler = CommandHandler('help', help_command)

    city_handler = CommandHandler('city', city_command)
    zipcode_handler = CommandHandler('zipcode', zipcode_command)
    coordinates_handler = CommandHandler('coordinates', coordinates_command)
    radius_handler = CommandHandler('radius', radius_command)
    status_handler = CommandHandler('status', status_command)

    text_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), unknown_command)
    unknown_handler = MessageHandler(filters.COMMAND, unknown_command)

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    
    application.add_handler(city_handler)
    application.add_handler(zipcode_handler)
    application.add_handler(coordinates_handler)
    application.add_handler(radius_handler)
    application.add_handler(status_handler)
    
    application.add_handler(text_handler)
    application.add_handler(unknown_handler)
    
    application.run_polling(stop_signals=None)

async def event_updater():
    queue = Queue()
    async with Bot(telegram_token) as test_bot:
        async with telegram.ext.Updater(test_bot, queue) as updater:
            await updater.bot.send_message(chat_id=my_chat_id, text='Hello')

if __name__ == '__main__':
    
    build_app()
    # asyncio.run(event_updater())





    

   

