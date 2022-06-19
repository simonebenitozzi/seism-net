#include <MPU9255.h>
#include <SPI.h>
#include <WiFi101.h>
#include "conf.hpp"
#include "mqtt.h"
#include "fft.h"
#include "offset_cancellation.h"
#include <ArduinoLowPower.h>
#include <RTCZero.h>
#include <WiFiUdp.h>

#define ACC_SAMPLE_SIZE 64
#define ACC_SCALE 16384.0
#define ACC_SAMPLE_FREQ_HZ 40
#define LATITUDE 45.46414679486616 
#define LONGITUDE 9.190254360602433

#define POWER_SLEEP_DURATION_MS 25


#define SCL_INDEX 0x00
#define SCL_TIME 0x01
#define SCL_FREQUENCY 0x02
#define SCL_PLOT 0x03

MPU9255 mpu;

volatile double peak_frequency;
volatile double peak_magnitude;
volatile bool new_sample = false;

WiFiClient wifiClient;

RTCZero rtc;

const char *ntpServerName = "time.nist.gov"; // it.pool.ntp.org";   // NTP server name
const int NTP_PACKET_SIZE = 48;              // NTP time stamp is in the first 48 bytes of the message
byte packetBuffer[NTP_PACKET_SIZE];          // buffer to hold I/O NTP packets
IPAddress timeServerIP;                      // dynamically resolved IP of the NTP server
WiFiUDP udp;                                 // UDP instance to send and receive packets
unsigned int localPort = 2390;

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
    mpu.disable(magnetometer);
    mpu.disable(Gyro_X);
    mpu.disable(Gyro_Y);
    mpu.disable(Gyro_Z);

    mqtt_init(wifiClient);
    udp.begin(localPort);
    unsigned long epoch = sendNTPRequest();
    Serial.println(epoch);
    rtc.begin(0);
    rtc.setEpoch(epoch);

    Serial.println("Setup completed!");
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
            send_mqtt_quake(peak_f, peak_m, rtc.getEpoch(), LATITUDE, LONGITUDE);
        }
        current_sample = 0;
    }
    else
    {
        LowPower.idle(POWER_SLEEP_DURATION_MS);
        last_read -= POWER_SLEEP_DURATION_MS;
        last_raw_send -= POWER_SLEEP_DURATION_MS;
    }
    delay(1);
}

unsigned long sendNTPRequest()
{
    unsigned long result = 0;
    WiFi.hostByName(ntpServerName, timeServerIP); // get NTP server IP from domain name
    sendNTPRequest(timeServerIP);                 // send datetime request
    delay(1000);                                  // allow time for the reply

    Serial.print(F("Internet reachable: "));

    int replySize = udp.parsePacket();
    if (replySize == 0)
    { // No UDP packet received
        result = 0;
    }
    else
    {                                            // UDP packet received
        udp.read(packetBuffer, NTP_PACKET_SIZE); // move the packet into the buffer

        // the timestamp starts at byte 40 of the received packet and is four bytes,
        //  or two words, long. First, extract the two words:

        unsigned long highWord = word(packetBuffer[40], packetBuffer[41]);
        unsigned long lowWord = word(packetBuffer[42], packetBuffer[43]);
        unsigned long secsSince1900 = highWord << 16 | lowWord; // time in seconds since Jan 1 1900
        unsigned long epoch = secsSince1900 - 2208988800UL;     // time in seconds since Jan 1 1970 (UNIX time)

        result = epoch;
    }

    return result;
}

void sendNTPRequest(IPAddress &address)
{
    // Serial.println("1");

    // set all bytes in the buffer to 0

    memset(packetBuffer, 0, NTP_PACKET_SIZE);

    // Initialize values needed to form NTP request

    // (see URL above for details on the packets)

    // Serial.println("2");

    packetBuffer[0] = 0b11100011; // LI, Version, Mode
    packetBuffer[1] = 0;          // Stratum, or type of clock
    packetBuffer[2] = 6;          // Polling Interval
    packetBuffer[3] = 0xEC;       // Peer Clock Precision
    // 8 bytes of zero for Root Delay & Root Dispersion

    packetBuffer[12] = 49;
    packetBuffer[13] = 0x4E;
    packetBuffer[14] = 49;
    packetBuffer[15] = 52;

    // Serial.println("3");

    // all NTP fields have been given values, now

    // you can send a packet requesting a timestamp:

    udp.beginPacket(address, 123); // NTP requests are to port 123

    // Serial.println("4");

    udp.write(packetBuffer, NTP_PACKET_SIZE);

    // Serial.println("5");

    udp.endPacket();

    // Serial.println("6");
}