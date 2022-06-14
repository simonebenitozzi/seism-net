#ifndef __MQTT_H__
#define __MQTT_H__
#include <WiFi101.h>

void connectToMQTTBroker(WiFiClient &client);
bool mqtt_init(WiFiClient &wiClient);
bool send_mqtt_quake(double freq, double mag, unsigned long timestamp, double latitude, double longitude);
bool send_mqtt_raw(double raw);

#endif