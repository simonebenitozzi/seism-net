#include <MPU9255.h>
#include <SPI.h>
#include <WiFi101.h>
#include "conf.h"
#define ACC_SAMPLE_SIZE 64
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

WiFiClient wifiClient;

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

    mpu.set_acc_scale(scale_2g);
    mpu.set_acc_bandwidth(acc_5Hz);
    mpu.set_gyro_bandwidth(gyro_5Hz);
    adjust_offset(mpu);
    mpu.set_acc_bandwidth(acc_20Hz);
    mpu.set_gyro_bandwidth(gyro_20Hz);

    Serial.println("Setup completed!");
    mqtt_init(wifiClient);
}

double vReal[ACC_SAMPLE_SIZE] = {0.0};
double vImg[ACC_SAMPLE_SIZE] = {0.0};

long last_read = 0;
long last_raw_send = 0;
void loop()
{

    static int current_sample = 0;
    if (millis() - last_read >= 25)
    {
        mpu.read_acc();
        double read = sqrt(mpu.ax * mpu.ax + mpu.ay * mpu.ay + mpu.az * mpu.az) / ACC_SCALE;
        vReal[current_sample] = read;
        vImg[current_sample] = 0;
        current_sample++;
        last_read = millis();
    }
    if (millis() - last_raw_send >= 100)
    {
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
