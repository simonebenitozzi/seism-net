#include <MPU9255.h>
#include <SAMDTimerInterrupt.h>
#include <MQTT.h>
#include <ArduinoJson.h>
#include <SPI.h>
#include <WiFi101.h>
#include "conf.h"

#define ACC_SAMPLE_SIZE 128
#define ACC_SCALE 16384
#define ACC_SAMPLE_FREQ_HZ 40

MPU9255 mpu;

SAMDTimer ITimer0(TIMER_TC4);

double vReal[ACC_SAMPLE_SIZE] = {0.0};
double vImg[ACC_SAMPLE_SIZE] = {0.0};

volatile double peak_frequency;
volatile double peak_magnitude;
volatile bool new_sample = false;

#define MQTT_BUFFER_SIZE 128
#define MQTT_TOPIC_PEAKS "/quake/peaks"


WiFiClient wifiClient;
MQTTClient mqttClient(MQTT_BUFFER_SIZE); // handles the MQTT communication protocol

void timer_handler()
{
    static int current_sample = 0;
    mpu.read_acc();
    float ay = mpu.ay;
    vReal[current_sample] = ay / ACC_SCALE;
    vImg[current_sample] = 0;
    if (current_sample == ACC_SAMPLE_SIZE)
    {
        compute_vibration(vReal, vImg, ACC_SAMPLE_SIZE);
        double peak_f, peak_m;
        bool peak_found = find_peak(vReal,
                                         ACC_SAMPLE_SIZE, ACC_SAMPLE_FREQ_HZ,
                                         peak_f, peak_m);
        peak_frequency = peak_f;
        peak_magnitude = peak_m;
        new_sample = true;
        current_sample = -1;
    }
    current_sample += 1;
}

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
    Serial.println("HERE");
    if (!mqttClient.connected())
    { // not connected
        Serial.print(F("\nConnecting to MQTT broker..."));
        while (!mqttClient.connect(MQTT_CLIENTID, MQTT_USERNAME, MQTT_PASSWORD))
        {
            Serial.print(F("."));
            delay(1000);
        }
        Serial.println(F("\nConnected!"));
    }else{
        Serial.println("MQTT: Already connected");
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
    mqttClient.begin(MQTT_BROKERIP, 1883, wifiClient);
    mqttClient.setTimeout(10000);
    connectToMQTTBroker();

    mpu.set_motion_threshold_level(125 / 4);       // set motion threshold level to 800 mg (4 mg per LSB)
    mpu.enable_motion_interrupt();                 // enable motion interrupt
    mpu.enable_interrupt_output(motion_interrupt); // enable motion interrupt to propagate throught INT pin
    mpu.set_acc_scale(scale_2g);
    mpu.set_acc_bandwidth(acc_5Hz);
    mpu.set_gyro_bandwidth(gyro_5Hz);
    // TODO: Compute interrupt timer from sample frequency parameter
    ITimer0.attachInterruptInterval_MS(25, timer_handler);
    Serial.println("Setup completed!");
}

void loop()
{
    // if (new_sample)
    // {
        Serial.println("Sending new sample");
        const int PEAK_MESSAGE_CAPACITY = JSON_OBJECT_SIZE(2);
        StaticJsonDocument<PEAK_MESSAGE_CAPACITY> peak_message_doc;
        char mqtt_buffer[MQTT_BUFFER_SIZE];
        peak_message_doc["frequency"] = "1";
        peak_message_doc["magnitude"] = "1";
        size_t n = serializeJson(peak_message_doc, mqtt_buffer);
        // connectToMQTTBroker();
        Serial.println(mqtt_buffer);
        mqttClient.publish(MQTT_TOPIC_PEAKS, mqtt_buffer, n, 0);
        Serial.println("Sent");
        new_sample = false;
    // }
    delay(1000);
}
