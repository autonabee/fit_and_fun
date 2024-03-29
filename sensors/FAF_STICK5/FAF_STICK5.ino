/*
* This file is a part of Fit and Fun
*
* Copyright (C) 2023 Inria/Autonabee
*
* This software is governed by the CeCILL license under French law and
* abiding by the rules of distribution of free software.  You can  use, 
* modify and/ or redistribute the software under the terms of the CeCILL
* license as circulated by CEA, CNRS and INRIA at the following URL
* "http://www.cecill.info". 
*
* As a counterpart to the access to the source code and  rights to copy,
* modify and redistribute granted by the license, users are provided only
* with a limited warranty  and the software's author,  the holder of the
* economic rights,  and the successive licensors  have only  limited
* liability.
*/

/*
* Inspired by M5StickC-Plus sample source code
* Visit for more information: https://docs.m5stack.com/en/core/m5stickc_plus
*/


#include "M5StickCPlus.h"
#include <WiFi.h>
#include <PubSubClient.h>

WiFiClient espClient;
PubSubClient client(espClient);

// Configure the name and password of the connected wifi and your MQTT Serve
// host. 
const char* ssid        = "fit_and_fun";
const char* password    = "fun_and_fit";
const char* mqtt_server = "10.42.0.1";

unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE (50)
char msg[MSG_BUFFER_SIZE];
int value = 0;

float gyroX = 0.0F;
float gyroY = 0.0F;
float gyroZ = 0.0F;


void setupWifi();
void callback(char* topic, byte* payload, unsigned int length);
void reConnect();

void setup() {
    M5.begin();
    M5.Lcd.setRotation(3);
    setupWifi();
    M5.Imu.Init();          // Init IMU.  
    client.setServer(mqtt_server,
                     1883);  // Sets the server details.  
    client.setCallback(
        callback);  // Sets the message callback function.
}

void loop() {
    if (!client.connected()) {
        reConnect();
    }
    client.loop();  // This function is called periodically to allow clients to
                    // process incoming messages and maintain connections to the
                    // server.
    M5.IMU.getGyroData(&gyroX, &gyroY, &gyroZ);
    //M5.Lcd.printf("GYRO: %6.2f  %6.2f  %6.2f\n", gyroX, gyroY, gyroZ);
    //snprintf(msg, MSG_BUFFER_SIZE, "%6.2f", (gyroZ+12)*15/600);
    snprintf(msg, MSG_BUFFER_SIZE, "%6.2f", (gyroZ / 360) * 2*PI);
    Serial.println((gyroZ / 360) * 2*PI);
    client.publish("fit_and_fun/speed", msg);
    
    delay(500);
    
/*
    unsigned long now =
        millis();  // Obtain the host startup duration.
    if (now - lastMsg > 2000) {
        lastMsg = now;
        ++value;
        M5.Lcd.printf("GYRO: %6.2f  %6.2f  %6.2f\n", gyroX, gyroY, gyroZ);
        snprintf(msg, MSG_BUFFER_SIZE, "%6.2f",
                 gyroX);  // Format to the specified string and store it in MSG.
        M5.Lcd.print("Publish message: ");
        M5.Lcd.println(msg);
        client.publish("fit_and_fun/speed", msg);  // Publishes a message to the specified
                                         // topic.
        if (value % 7 == 0) {
            M5.Lcd.fillScreen(BLACK);
            M5.Lcd.setCursor(0, 0);
        }
    }
    */
    
}


void setupWifi() {
    delay(10);
    M5.Lcd.printf("Connecting to %s", ssid);
    WiFi.mode(WIFI_STA);  // Set the mode to WiFi station mode.  
    WiFi.begin(ssid);  // Start Wifi connection.

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        M5.Lcd.print(".");
    }
    M5.Lcd.print("\nConnected to the WiFi network");
    M5.Lcd.print("Local ESP32 IP: ");
    M5.Lcd.println(WiFi.localIP());
}


void callback(char* topic, byte* payload, unsigned int length) {
    M5.Lcd.print("Message arrived [");
    M5.Lcd.print(topic);
    M5.Lcd.print("] ");
    for (int i = 0; i < length; i++) {
        M5.Lcd.print((char)payload[i]);
    }
    M5.Lcd.println();
}


void reConnect() {
    while (!client.connected()) {
        M5.Lcd.print("Attempting MQTT connection...");
        // Create a random client ID.  
        String clientId = "M5Stack-";
        clientId += String(random(0xffff), HEX);
        // Attempt to connect. 
        if (client.connect(clientId.c_str())) {
            M5.Lcd.printf("\nSuccess\n");
            // Once connected, publish an announcement to the topic.
            client.publish("fit_and_fun", "M5Stack init");
            // ... and resubscribe.
            client.subscribe("fit_and_fun");
        } else {
            M5.Lcd.print("failed, rc=");
            M5.Lcd.print(client.state());
            M5.Lcd.println("try again in 5 seconds");
            delay(5000);
        }
    }
}
