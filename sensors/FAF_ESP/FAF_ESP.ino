#include <WiFi.h>
#include <PubSubClient.h>
#include <Adafruit_Sensor.h>                                                    
#include <Adafruit_BNO055.h>   

WiFiClient espClient;
PubSubClient client(espClient);

const char* ssid        = "fit_and_fun";
const char* password    = "fun_and_fit";
const char* mqtt_server = "10.42.0.1";

const int buttonSelectPin = 14;
const int buttonDownPin = 15;
int buttonSelectState = 0;
int buttonDownState = 0;

const int ledPin =  13;      // the number of the LED pin

#define MSG_BUFFER_SIZE (10)
char msg[MSG_BUFFER_SIZE];
float value = 51.0;

/* Set the delay between fresh samples */                                       
uint16_t BNO055_SAMPLERATE_DELAY_MS = 100;                                      
/* Check I2C device address */                                                          
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28); 


void setupWifi();
void reConnect();

void setupWifi() {
    delay(10);
    Serial.print("Connecting to ");
    Serial.println(ssid);
    //WiFi.begin(ssid, password);  // Start Wifi connection.
    WiFi.begin(ssid);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("Connected to the WiFi network");
    Serial.print("Local ESP32 IP: ");
    Serial.println(WiFi.localIP());
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200); 
  setupWifi(); 
  client.setServer(mqtt_server, 1883); 
  
  /* Initialise the sensor */                                                   
  if (!bno.begin())                                                             
  {                                                                             
    /* There was a problem detecting the BNO055 ... check your connections */   
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!"\
);                                                                              
    while (1);                                                                  
  }       

  pinMode(buttonSelectPin, INPUT_PULLUP);
  pinMode(buttonDownPin, INPUT_PULLUP);
  pinMode(ledPin, OUTPUT);
  
  delay(1000);                                                                                   
                  
}

void loop() {
  if (!client.connected()) {
        reConnect();
    }
  client.loop(); 
  
  /* Get a new sensor event */
  sensors_event_t event;
  bno.getEvent(&event, Adafruit_BNO055::VECTOR_GYROSCOPE);
  Serial.print(F("Gyro: "));
  Serial.print((float)event.gyro.x);
  Serial.print(F(" "));
  Serial.print((float)event.gyro.y);
  Serial.print(F(" "));
  Serial.print((float)event.gyro.z);
  Serial.println(F(""));

  /* Creation and sending of a speed message */
  snprintf(msg, MSG_BUFFER_SIZE, "%6.2f", (float)event.gyro.z);
  client.publish("fit_and_fun/speed", msg);
  Serial.print("mqtt publish speed: ");
  Serial.println(msg);

  /* Creation and sending of a select button message */
  buttonSelectState = digitalRead(buttonSelectPin);
  snprintf(msg, MSG_BUFFER_SIZE, "%s", buttonSelectState == HIGH ? "false" : "true");
  client.publish("fit_and_fun/select", msg);
  Serial.print("mqtt publish select: ");
  Serial.println(msg);
  
  /* Creation and sending of a down button message */
  buttonDownState = digitalRead(buttonDownPin);  
  snprintf(msg, MSG_BUFFER_SIZE, "%s", buttonDownState == HIGH ? "false" : "true");
  client.publish("fit_and_fun/down", msg);
  Serial.print("mqtt publish down: ");
  Serial.println(msg);
  
  delay(BNO055_SAMPLERATE_DELAY_MS);
}

void reConnect() {
    while (!client.connected()) {
        Serial.print("Attempting MQTT connection...");
        // Create a random client ID.  
        String clientId = "M5Stack-";
        clientId += String(random(0xffff), HEX);
        // Attempt to connect. 
        if (client.connect(clientId.c_str())) {
            Serial.println("\nSuccess\n");
            // Once connected, publish an announcement to the topic.
            client.publish("fit_and_fun", "M5Stack init");
            // ... and resubscribe.
            client.subscribe("fit_and_fun");
        } else {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println("try again in 5 seconds");
            delay(5000);
        }
    }
}
