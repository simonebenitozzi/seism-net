#include <MPU9255.h>
#include <MQTT.h>
#include <ArduinoJson.h>
#include <SPI.h>
#include <WiFi101.h>
#include "conf.h"
#define ACC_SAMPLE_SIZE 128
#define ACC_SCALE 16384.0
#define ACC_SAMPLE_FREQ_HZ 40

#define SCL_INDEX 0x00
#define SCL_TIME 0x01
#define SCL_FREQUENCY 0x02
#define SCL_PLOT 0x03

MPU9255 mpu;

volatile double peak_frequency;
volatile double peak_magnitude;
volatile bool new_sample = false;

#define MQTT_BUFFER_SIZE 256
#define MQTT_TOPIC_PEAKS "/seism/" MQTT_CLIENTID "/events"
#define MQTT_TOPIC_RAW "/seism/" MQTT_CLIENTID "/raw"
#define MQTT_TOPIC_STATUS "/status/" MQTT_CLIENTID

WiFiClient wifiClient;
MQTTClient mqttClient(MQTT_BUFFER_SIZE); // handles the MQTT communication protocol

// void IRAM_ATTR timer_handler()
// {
//     static int current_sample = 0;
//     mpu.read_acc();
//     float ay = mpu.ay;
//     vReal[current_sample] = ay / ACC_SCALE;
//     vImg[current_sample] = 0;
//     if (current_sample == ACC_SAMPLE_SIZE)
//     {
//         compute_vibration(vReal, vImg, ACC_SAMPLE_SIZE);
//         double peak_f, peak_m;
//         bool peak_found = find_peak(vReal,
//                                          ACC_SAMPLE_SIZE, ACC_SAMPLE_FREQ_HZ,
//                                          peak_f, peak_m);
//         peak_frequency = peak_f;
//         peak_magnitude = peak_m;
//         new_sample = true;
//         current_sample = -1;
//     }
//     current_sample += 1;
// }

char mqtt_buffer[MQTT_BUFFER_SIZE];
bool send_mqtt_quake(double, double);
bool send_mqtt_raw(double);

int wifi_setup()
{
    int result = 0;
    WiFi.begin(SSID, AP_PASSWORD);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(1000);
        Serial.print(".");
        WiFi.begin(SSID, AP_PASSWORD);
    }
    Serial.print("IP Address is: ");
    Serial.println(WiFi.localIP());
    return result;
}

void connectToMQTTBroker()
{
    mqttClient.begin(MQTT_BROKERIP, 1883, wifiClient);
    mqttClient.setTimeout(10000);
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
void setup()
{
    Serial.begin(115200);
    pinMode(0, INPUT);
    Wire.begin();
    if (mpu.init())
    {
        Serial.println("ACC working");
    }
    else
    {
        Serial.println("ACC not working");
    }

    wifi_setup();

    mpu.set_motion_threshold_level(125 / 4);       // set motion threshold level to 800 mg (4 mg per LSB)
    mpu.enable_motion_interrupt();                 // enable motion interrupt
    mpu.enable_interrupt_output(motion_interrupt); // enable motion interrupt to propagate throught INT pin
    mpu.set_acc_scale(scale_2g);
    mpu.set_acc_bandwidth(acc_5Hz);
    mpu.set_gyro_bandwidth(gyro_5Hz);
    adjust_offset(mpu);
    Serial.println("Setup completed!");

    mqttClient.begin(MQTT_BROKERIP, 1883, wifiClient);
    mqttClient.setTimeout(10000);
    //Set LWT
    StaticJsonDocument<JSON_OBJECT_SIZE(1)> doc;
    doc["online"] = false;
    size_t n = serializeJson(doc, mqtt_buffer);
    mqttClient.setWill(MQTT_TOPIC_STATUS, mqtt_buffer, true, 2);

    connectToMQTTBroker();

    doc["online"] = true;
    n = serializeJson(doc, mqtt_buffer);
    mqttClient.publish(MQTT_TOPIC_STATUS, mqtt_buffer, n, true, 2);
}

double vReal[ACC_SAMPLE_SIZE] = {0.0};
double vImg[ACC_SAMPLE_SIZE] = {0.0};

long last_read = 0;
long last_raw_send = 0;
void loop()
{

    mqttClient.loop();
    static int current_sample = 0;
    if (millis() - last_read >= 25)
    {
        mpu.read_acc();
        vReal[current_sample] = mpu.ay / ACC_SCALE;
        vImg[current_sample] = 0;
        current_sample++;
        last_read = millis();
    }
    if(millis() - last_raw_send >= 100){
        mpu.read_acc();
        send_mqtt_raw(mpu.ay / ACC_SCALE);
        last_raw_send = millis();
    }

    if (current_sample == ACC_SAMPLE_SIZE)
    {
        compute_vibration(vReal, vImg, ACC_SAMPLE_SIZE);
        double peak_f, peak_m;
        bool peak_found = find_peak(vReal,
                                    ACC_SAMPLE_SIZE, ACC_SAMPLE_FREQ_HZ,
                                    peak_f, peak_m);
        if (peak_found)
        {
            // PrintVector(vReal, ACC_SAMPLE_SIZE, SCL_FREQUENCY, 40);
            send_mqtt_quake(peak_f, peak_m);
        }
        current_sample = 0;
        
    }
    delay(1);
}

const int PEAK_MESSAGE_CAPACITY = JSON_OBJECT_SIZE(3);
StaticJsonDocument<PEAK_MESSAGE_CAPACITY> peak_message_doc;

bool send_mqtt_quake(double freq, double mag)
{
    peak_message_doc["frequency"] = freq;
    peak_message_doc["magnitude"] = mag;
    peak_message_doc["mercalli"] = g_to_mercalli(mag);
    size_t n = serializeJson(peak_message_doc, mqtt_buffer);
    return mqttClient.publish(MQTT_TOPIC_PEAKS, mqtt_buffer, n, 0);
}

StaticJsonDocument<JSON_OBJECT_SIZE(1)> raw_read_message_doc;

bool send_mqtt_raw(double raw){
    raw_read_message_doc["reading_g"] = raw;
    size_t n = serializeJson(raw_read_message_doc, mqtt_buffer);
    return mqttClient.publish(MQTT_TOPIC_RAW, mqtt_buffer, n, 0);
}

void PrintVector(double *vData, uint16_t bufferSize, uint8_t scaleType, double sample_freq)
{
  for (uint16_t i = 0; i < bufferSize; i++)
  {
    double abscissa;
    /* Print abscissa value */
    switch (scaleType)
    {
    case SCL_INDEX:
      abscissa = (i * 1.0);
      break;
    case SCL_TIME:
      abscissa = ((i * 1.0) / sample_freq);
      break;
    case SCL_FREQUENCY:
      abscissa = ((i * 1.0 * sample_freq) / ACC_SAMPLE_SIZE);
      break;
    }
    Serial.print(abscissa, 6);
    if (scaleType == SCL_FREQUENCY)
      Serial.print("Hz");
    Serial.print(" ");
    Serial.println(vData[i], 4);
  }
  Serial.println();
}
