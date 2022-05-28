#include <ArduinoJson.h>
#include <MQTT.h>
#include <WiFi101.h>

#define MQTT_BUFFER_SIZE 256
#define MQTT_TOPIC_PEAKS "/seism/%s/events"
#define MQTT_TOPIC_RAW "/seism/%s/raw"
#define MQTT_TOPIC_STATUS "/status/%s"
MQTTClient mqttClient(MQTT_BUFFER_SIZE); // handles the MQTT communication protocol
char mqtt_buffer[MQTT_BUFFER_SIZE];

String formatted_mac();

const int PEAK_MESSAGE_CAPACITY = JSON_OBJECT_SIZE(3);
StaticJsonDocument<PEAK_MESSAGE_CAPACITY> peak_message_doc;

void connectToMQTTBroker(WiFiClient& client)
{
    mqttClient.begin(MQTT_BROKERIP, 1883, client);
    mqttClient.setTimeout(1000);
    if (!mqttClient.connected())
    { // not connected
        Serial.print(F("\nConnecting to MQTT broker..."));
        while (!mqttClient.connect(MQTT_CLIENTID, MQTT_USERNAME, MQTT_PASSWORD))
        {
            Serial.print(F("."));
            delay(1000);
        }
        Serial.println(F("\nConnected!"));
    }
}

bool mqtt_init(WiFiClient &wiClient)
{
    connectToMQTTBroker(wiClient);
    StaticJsonDocument<JSON_OBJECT_SIZE(1)> doc;
    doc["online"] = false;

    char topic[64];
    String mac = formatted_mac();
    snprintf(topic, 64, MQTT_TOPIC_STATUS, mac.c_str());
    size_t n = serializeJson(doc, mqtt_buffer);
    mqttClient.setWill(topic, mqtt_buffer, true, 2);


    doc["online"] = true;
    n = serializeJson(doc, mqtt_buffer);
    mqttClient.publish(topic, mqtt_buffer, n, true, 2);
}
bool send_mqtt_quake(double freq, double mag)
{
    char topic[64];
    snprintf(topic, 64, MQTT_TOPIC_PEAKS, formatted_mac().c_str());
    peak_message_doc["frequency"] = freq;
    peak_message_doc["magnitude"] = mag;
    peak_message_doc["mercalli"] = g_to_mercalli(mag);
    size_t n = serializeJson(peak_message_doc, mqtt_buffer);
    return mqttClient.publish(topic, mqtt_buffer, n, 0);
}

StaticJsonDocument<JSON_OBJECT_SIZE(1)> raw_read_message_doc;

bool send_mqtt_raw(double raw)
{
    char topic[64];
    snprintf(topic, 64, MQTT_TOPIC_RAW, formatted_mac().c_str());
    raw_read_message_doc["reading_g"] = raw;
    size_t n = serializeJson(raw_read_message_doc, mqtt_buffer);
    return mqttClient.publish(topic, mqtt_buffer, n, 0);
}

String formatted_mac()
{
    String result = "";
    byte mac[6];
    WiFi.macAddress(mac);
    for (int i = 5; i > -1; i--)
    {
        result += String(mac[i], HEX);
        if (i > 0)
        {
            result += ":";
        }
    }
    return result;
}