# Detailed Setup and Assembly Guide

## Phase 1: Hardware Assembly

### Step 1: Power Supply Setup
```bash
# Required Components:
- 5V 2A power adapter
- AMS1117-3.3V voltage regulator
- 100nF decoupling capacitors
- 10µF electrolytic capacitor
```

**Wiring Steps:**
1. Connect 5V power adapter to breadboard power rail
2. Connect AMS1117-3.3V regulator:
   - Input pin to 5V rail
   - Output pin to 3.3V rail
   - Ground pin to GND rail
3. Add decoupling capacitors:
   - 100nF between 5V and GND
   - 100nF between 3.3V and GND
   - 10µF electrolytic on 3.3V rail

### Step 2: ESP32 Installation
```bash
# ESP32-DevKitC Pinout Reference:
VIN    - 5V input
3.3V   - 3.3V output
GND    - Ground
GPIO   - Digital pins
```

**Installation Steps:**
1. Place ESP32 in center of breadboard
2. Connect VIN to 5V rail
3. Connect GND to GND rail
4. Connect 3.3V to 3.3V rail
5. Add pull-up resistors on GPIO 0 and GPIO 2

### Step 3: Audio Amplifier Connection
```bash
# MAX98357A Pinout:
VCC  - Power (3.3V)
GND  - Ground
BCLK - Bit Clock
LRC  - Left/Right Clock
DIN  - Data Input
OUT+ - Speaker Positive
OUT- - Speaker Negative
```

**Connection Steps:**
1. Place MAX98357A near ESP32
2. Connect power:
   - VCC to 3.3V rail
   - GND to GND rail
3. Connect I2S signals:
   - BCLK to GPIO 26
   - LRC to GPIO 25
   - DIN to GPIO 27
4. Connect speaker:
   - OUT+ to speaker positive
   - OUT- to speaker negative

### Step 4: Microphone Installation
```bash
# INMP441 Pinout:
VDD - Power (3.3V)
GND - Ground
WS  - Word Select
SD  - Serial Data
SCK - Serial Clock
```

**Connection Steps:**
1. Place INMP441 on opposite side of breadboard
2. Connect power:
   - VDD to 3.3V rail
   - GND to GND rail
3. Connect I2S signals:
   - WS to GPIO 25 (shared with amplifier)
   - SD to GPIO 33
   - SCK to GPIO 32

### Step 5: Status Indicators
```bash
# LED Connections:
Status LED: GPIO 4 + 220Ω resistor
WiFi LED:   GPIO 2 + 220Ω resistor
Button:     GPIO 0 to GND
```

**Installation Steps:**
1. Connect status LED:
   - Anode to GPIO 4
   - Cathode through 220Ω resistor to GND
2. Connect WiFi LED:
   - Anode to GPIO 2
   - Cathode through 220Ω resistor to GND
3. Connect push button:
   - One pin to GPIO 0
   - Other pin to GND

## Phase 2: Software Installation

### Step 1: Arduino IDE Setup
```bash
# Install ESP32 Board Support:
1. Open Arduino IDE
2. File → Preferences
3. Additional Board Manager URLs:
   https://dl.espressif.com/dl/package_esp32_index.json
4. Tools → Board → Boards Manager
5. Search "ESP32" → Install "esp32 by Espressif Systems"
```

### Step 2: Required Libraries
```bash
# Install via Library Manager:
- ESP32-audioI2S (by schreibfaul1)
- ArduinoJson (by Benoit Blanchon)
- PubSubClient (by Nick O'Leary)
- WiFiManager (by tzapu)
- WebServer (built-in)
```

### Step 3: Board Configuration
```bash
# Arduino IDE Settings:
Board: "ESP32 Dev Module"
Upload Speed: 115200
CPU Frequency: 240MHz
Flash Frequency: 80MHz
Flash Mode: QIO
Flash Size: 4MB
Partition Scheme: Default 4MB
```

## Phase 3: Initial Testing

### Step 1: Basic ESP32 Test
```cpp
// Test Code: basic_test.ino
void setup() {
  Serial.begin(115200);
  pinMode(2, OUTPUT);
}

void loop() {
  digitalWrite(2, HIGH);
  Serial.println("LED ON");
  delay(1000);
  digitalWrite(2, LOW);
  Serial.println("LED OFF");
  delay(1000);
}
```

**Testing Steps:**
1. Upload code to ESP32
2. Open Serial Monitor (115200 baud)
3. Verify LED blinks and serial output
4. Check for any error messages

### Step 2: WiFi Connection Test
```cpp
// Test Code: wifi_test.ino
#include <WiFi.h>

const char* ssid = "YourWiFi";
const char* password = "YourPassword";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  
  Serial.println("WiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // WiFi status monitoring
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected!");
    WiFi.reconnect();
  }
  delay(5000);
}
```

### Step 3: Audio System Test
```cpp
// Test Code: audio_test.ino
#include "Audio.h"

Audio audio;

void setup() {
  Serial.begin(115200);
  
  // Configure I2S pins
  audio.setPinout(26, 25, 27);
  audio.setVolume(10);
  
  // Test with simple tone
  audio.connecttohost("http://www.soundjay.com/misc/sounds/bell-ringing-05.wav");
}

void loop() {
  audio.loop();
  
  if (audio.isRunning()) {
    Serial.println("Audio playing...");
  }
}
```

## Phase 4: Advanced Configuration

### Step 1: Audio Quality Optimization
```cpp
// Audio Configuration
void setupAudio() {
  audio.setPinout(26, 25, 27);
  audio.setVolume(15);
  audio.setConnectionTimeout(10000, 1000);
  
  // Audio quality settings
  audio.setBufsize(1024, 512);
  audio.setI2SCommFMT_LSB(true);
}
```

### Step 2: WiFi Manager Setup
```cpp
// WiFi Manager Configuration
#include <WiFiManager.h>

WiFiManager wm;

void setupWiFiManager() {
  wm.setConfigPortalTimeout(180);
  wm.setAPCallback(configModeCallback);
  
  if (!wm.autoConnect("ESP32-Speaker")) {
    Serial.println("Failed to connect");
    ESP.restart();
  }
}

void configModeCallback(WiFiManager *myWiFiManager) {
  Serial.println("Entered config mode");
  Serial.println(WiFi.softAPIP());
}
```

### Step 3: MQTT Configuration
```cpp
// MQTT Setup
#include <PubSubClient.h>

WiFiClient espClient;
PubSubClient client(espClient);

void setupMQTT() {
  client.setServer("your-mqtt-broker.com", 1883);
  client.setCallback(mqttCallback);
  client.setBufferSize(1024);
}

void reconnectMQTT() {
  while (!client.connected()) {
    if (client.connect("ESP32-Speaker", "username", "password")) {
      client.subscribe("speaker/control");
      client.publish("speaker/status", "online");
    } else {
      delay(5000);
    }
  }
}
```

## Phase 5: Enclosure Design

### Step 1: 3D Design Considerations
```bash
# Enclosure Requirements:
- Speaker mounting holes
- Ventilation for heat dissipation
- Access to USB port
- LED visibility
- Button accessibility
- Cable management
```

### Step 2: Component Layout
```bash
# Internal Layout:
- ESP32: Center position
- Audio amplifier: Near speaker
- Microphone: Front-facing
- Power supply: Bottom
- Cables: Organized routing
```

### Step 3: Assembly Steps
1. **Print enclosure parts**
2. **Mount speaker** in front panel
3. **Install ESP32** on mounting posts
4. **Route cables** through channels
5. **Secure components** with screws
6. **Test functionality** before final assembly

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. Audio Not Working
```bash
# Check:
- I2S pin connections
- Power supply voltage
- Speaker connections
- Audio library installation
```

#### 2. WiFi Connection Issues
```bash
# Solutions:
- Check SSID and password
- Verify WiFi signal strength
- Reset WiFi settings
- Check antenna connections
```

#### 3. Microphone Problems
```bash
# Troubleshooting:
- Verify I2S connections
- Check microphone power
- Test with different sample rates
- Verify I2S configuration
```

#### 4. Power Issues
```bash
# Power Problems:
- Check voltage levels
- Verify current capacity
- Add decoupling capacitors
- Check for short circuits
```

### Debug Tools
```cpp
// System Information
void printSystemInfo() {
  Serial.println("=== System Info ===");
  Serial.printf("Free heap: %d bytes\n", ESP.getFreeHeap());
  Serial.printf("WiFi RSSI: %d dBm\n", WiFi.RSSI());
  Serial.printf("Uptime: %d seconds\n", millis() / 1000);
  Serial.printf("Audio status: %s\n", audio.isRunning() ? "Playing" : "Stopped");
}
```

This detailed setup guide provides step-by-step instructions for building and programming your ESP32 smart speaker project.
