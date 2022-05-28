import json
import mysql.connector
import random

from paho.mqtt import client as mqtt_client


broker = '149.132.182.144'
#broker = "broker.emqx.io"
port = 1883
topic = "/seism/+/events"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
# username = 'emqx'
# password = 'public'


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    client.subscribe(topic)
    client.on_message = on_message

def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

        m_decode=str(msg.payload.decode("utf-8","ignore"))
        m_in=json.loads(m_decode) #decode json data

        topic_parts = msg.topic.split("/")
        sensor_id = topic_parts[2]
        log_earthquake(m_in["frequency"], m_in["magnitude"], m_in["mercalli"], sensor_id)
        

def log_earthquake(frequency, magnitude, mercalli, sensor_id):
    try:
        connection = mysql.connector.connect(host='149.132.178.180',
                                             database='sbenitozzi',
                                             user='sbenitozzi',
                                             password='iot889407')
        cursor = connection.cursor()
        mySql_insert_query = """INSERT INTO earthquake_detection (frequency, magnitude, mercalli, sensor_id) 
                                VALUES (%s, %s, %s, %s)"""

        record = (frequency, magnitude, mercalli, sensor_id)
        cursor.execute(mySql_insert_query, record)
        connection.commit()
        print("Record inserted successfully into earthquake_detection table")

    except mysql.connector.Error as error:
        print("Failed to insert into MySQL table\n\t{}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()