
/*
*******************************************************************************
* Copyright (c) 2021 by M5Stack
*                  Equipped with M5StickC-Plus sample source code
* Visit for more information: https://docs.m5stack.com/en/core/m5stickc_plus
*
* Describe: MQTT.
* Date: 2021/11/5
*******************************************************************************
*/
#include "M5StickCPlus.h"
#include <WiFi.h>
#include <PubSubClient.h>

WiFiClient espClient;
PubSubClient client(espClient);

const char* ssid        = "fit_and_fun";
const char* password    = "fun_and_fit";

String get_wifi_status(int status){
 
    switch(status){
        case WL_IDLE_STATUS:
        return "WL_IDLE_STATUS";
        case WL_SCAN_COMPLETED:
        return "WL_SCAN_COMPLETED";
        case WL_NO_SSID_AVAIL:
        return "WL_NO_SSID_AVAIL";
        case WL_CONNECT_FAILED:
        return "WL_CONNECT_FAILED";
        case WL_CONNECTION_LOST:
        return "WL_CONNECTION_LOST";
        case WL_CONNECTED:
        return "WL_CONNECTED";
        case WL_DISCONNECTED:
        return "WL_DISCONNECTED";
    }
    return "WL_UNKNOWN";
}

void setupWifi() {

    delay(10);
    M5.Lcd.printf("Connecting to %s", ssid);
    WiFi.mode(WIFI_STA); 
    WiFi.begin(ssid, password);
    M5.Lcd.println("\nConnecting");

    while(WiFi.status() != WL_CONNECTED){
        //M5.lcd.println('.');
        M5.lcd.println(get_wifi_status(WiFi.status()));
        delay(500);
    }

    M5.Lcd.print("\nConnected to the WiFi network");
    M5.Lcd.print("Local ESP32 IP: ");
    M5.Lcd.println(WiFi.localIP());
}

void setup(){
    M5.begin();
    M5.Lcd.setRotation(3);
    setupWifi();
}

void loop() {
    
}
