# ESP32 Smart Speaker Programming Guide

## Development Environment Setup

### 1. Arduino IDE Configuration
```bash
# Install ESP32 Board Support
1. Open Arduino IDE
2. Go to File → Preferences
3. Add URL: https://dl.espressif.com/dl/package_esp32_index.json
4. Go to Tools → Board → Boards Manager
5. Search "ESP32" and install "esp32 by Espressif Systems"
```

### 2. Required Libraries
```cpp
// Install these libraries via Library Manager:
#include "Audio.h"           // ESP32-audioI2S
#include <WiFi.h>           // Built-in
#include <WebServer.h>      // Built-in
#include <ArduinoJson.h>    // ArduinoJson
#include <PubSubClient.h>   // PubSubClient
#include <WiFiManager.h>    // WiFiManager
```

## Basic Audio Setup

### 1. I2S Audio Configuration
```cpp
#include "Audio.h"

Audio audio;

void setup() {
  Serial.begin(115200);
  
  // Configure I2S pins
  audio.setPinout(I2S_BCLK, I2S_LRC, I2S_DOUT);
  
  // Set audio parameters
  audio.setVolume(21);  // Volume 0-21
  audio.setConnectionTimeout(10000, 1000);
  
  // Test with local file or stream
  audio.connecttohost("http://stream.url");
}

void loop() {
  audio.loop();
}
```

### 2. I2S Microphone Setup
```cpp
#include "driver/i2s.h"

#define I2S_WS 25
#define I2S_SD 33
#define I2S_SCK 32
#define I2S_PORT I2S_NUM_0

void setupI2SMic() {
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = 44100,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4,
    .dma_buf_len = 1024
  };
  
  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD
  };
  
  i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_PORT, &pin_config);
}
```

## WiFi and Network Setup

### 1. WiFi Connection
```cpp
#include <WiFi.h>
#include <WiFiManager.h>

WiFiManager wm;

void setupWiFi() {
  // WiFiManager for easy configuration
  wm.setConfigPortalTimeout(180);
  
  if (!wm.autoConnect("ESP32-Speaker")) {
    Serial.println("Failed to connect");
    ESP.restart();
  }
  
  Serial.println("WiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}
```

### 2. Web Server Setup
```cpp
#include <WebServer.h>

WebServer server(80);

void setupWebServer() {
  server.on("/", handleRoot);
  server.on("/control", handleControl);
  server.on("/volume", handleVolume);
  server.on("/play", handlePlay);
  server.on("/stop", handleStop);
  
  server.begin();
  Serial.println("Web server started");
}

void handleRoot() {
  String html = "<!DOCTYPE html><html><head><title>ESP32 Speaker</title></head>";
  html += "<body><h1>ESP32 Smart Speaker</h1>";
  html += "<button onclick='play()'>Play</button>";
  html += "<button onclick='stop()'>Stop</button>";
  html += "<input type='range' id='volume' min='0' max='21' value='10'>";
  html += "<script>function play(){fetch('/play')} function stop(){fetch('/stop')}</script>";
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

void handleControl() {
  if (server.hasArg("volume")) {
    int volume = server.arg("volume").toInt();
    audio.setVolume(volume);
    server.send(200, "text/plain", "Volume set to " + String(volume));
  }
}
```

## Voice Command Processing

### 1. Basic Voice Recognition
```cpp
#include "esp_sr_iface.h"
#include "esp_wn_iface.h"

// Wake word detection
void setupWakeWord() {
  // Initialize wake word engine
  esp_sr_iface_t *wake_word_engine = esp_sr_create_model(&WAKE_WORD_MODEL);
  
  if (wake_word_engine) {
    Serial.println("Wake word engine initialized");
  }
}

void processVoiceCommand(String command) {
  command.toLowerCase();
  
  if (command.indexOf("play") >= 0) {
    if (command.indexOf("music") >= 0) {
      playMusic();
    } else if (command.indexOf("radio") >= 0) {
      playRadio();
    }
  } else if (command.indexOf("stop") >= 0) {
    audio.stopSong();
  } else if (command.indexOf("volume") >= 0) {
    int volume = extractVolume(command);
    audio.setVolume(volume);
  } else if (command.indexOf("next") >= 0) {
    nextTrack();
  } else if (command.indexOf("previous") >= 0) {
    previousTrack();
  }
}

int extractVolume(String command) {
  // Extract volume number from command
  int start = command.indexOf("volume") + 7;
  int end = command.indexOf(" ", start);
  if (end == -1) end = command.length();
  
  String volumeStr = command.substring(start, end);
  return volumeStr.toInt();
}
```

### 2. Audio Recording and Processing
```cpp
#define AUDIO_BUFFER_SIZE 1024
int16_t audioBuffer[AUDIO_BUFFER_SIZE];

void recordAudio() {
  size_t bytesRead;
  i2s_read(I2S_PORT, audioBuffer, AUDIO_BUFFER_SIZE * sizeof(int16_t), &bytesRead, portMAX_DELAY);
  
  // Process audio buffer
  processAudioBuffer(audioBuffer, bytesRead / sizeof(int16_t));
}

void processAudioBuffer(int16_t* buffer, size_t length) {
  // Apply noise reduction
  applyNoiseReduction(buffer, length);
  
  // Detect voice activity
  if (detectVoiceActivity(buffer, length)) {
    // Send to voice recognition
    sendToVoiceRecognition(buffer, length);
  }
}
```

## IoT Integration

### 1. MQTT Client Setup
```cpp
#include <PubSubClient.h>

WiFiClient espClient;
PubSubClient client(espClient);

const char* mqtt_server = "your-mqtt-broker.com";
const char* mqtt_user = "username";
const char* mqtt_password = "password";

void setupMQTT() {
  client.setServer(mqtt_server, 1883);
  client.setCallback(mqttCallback);
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  if (String(topic) == "speaker/control") {
    processMQTTCommand(message);
  }
}

void processMQTTCommand(String command) {
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, command);
  
  String action = doc["action"];
  if (action == "play") {
    String url = doc["url"];
    audio.connecttohost(url);
  } else if (action == "stop") {
    audio.stopSong();
  } else if (action == "volume") {
    int volume = doc["volume"];
    audio.setVolume(volume);
  }
}
```

### 2. Home Assistant Integration
```cpp
void publishStatus() {
  DynamicJsonDocument doc(1024);
  doc["status"] = audio.isRunning() ? "playing" : "stopped";
  doc["volume"] = audio.getVolume();
  doc["current_track"] = audio.getCurrentTrack();
  
  String payload;
  serializeJson(doc, payload);
  client.publish("speaker/status", payload.c_str());
}

void setupHomeAssistant() {
  // Publish device discovery
  DynamicJsonDocument config(1024);
  config["name"] = "ESP32 Smart Speaker";
  config["unique_id"] = "esp32_speaker_001";
  config["device_class"] = "speaker";
  
  String configPayload;
  serializeJson(config, configPayload);
  client.publish("homeassistant/media_player/esp32_speaker/config", configPayload.c_str());
}
```

## Advanced Features

### 1. OTA Updates
```cpp
#include <ArduinoOTA.h>

void setupOTA() {
  ArduinoOTA.setHostname("ESP32-Speaker");
  ArduinoOTA.setPassword("your_password");
  
  ArduinoOTA.onStart([]() {
    Serial.println("OTA Update Started");
    audio.stopSong();
  });
  
  ArduinoOTA.onEnd([]() {
    Serial.println("OTA Update Complete");
  });
  
  ArduinoOTA.begin();
}

void loop() {
  ArduinoOTA.handle();
  // ... other code
}
```

### 2. Audio Streaming
```cpp
void setupAudioStreaming() {
  // HTTP audio streaming
  audio.connecttohost("http://ice1.somafm.com/groovesalad-128-mp3");
  
  // Bluetooth audio (if supported)
  // audio.connecttoBluetooth();
  
  // Local file playback
  // audio.connecttoFS(SPIFFS, "/music/song.mp3");
}

void handleAudioEvents() {
  if (audio.isRunning()) {
    if (audio.getAudioFileDuration() > 0) {
      Serial.printf("Duration: %d seconds\n", audio.getAudioFileDuration());
    }
  }
}
```

## Error Handling and Debugging

### 1. Error Handling
```cpp
void handleAudioErrors() {
  if (audio.getAudioFileDuration() == 0) {
    Serial.println("Audio file error");
    // Retry or switch to next track
  }
  
  if (!audio.isRunning()) {
    Serial.println("Audio stopped unexpectedly");
    // Attempt to restart
  }
}

void handleWiFiErrors() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected, reconnecting...");
    WiFi.reconnect();
  }
}
```

### 2. Debugging Tools
```cpp
void printSystemInfo() {
  Serial.println("=== System Info ===");
  Serial.printf("Free heap: %d bytes\n", ESP.getFreeHeap());
  Serial.printf("WiFi RSSI: %d dBm\n", WiFi.RSSI());
  Serial.printf("Uptime: %d seconds\n", millis() / 1000);
  Serial.printf("Audio status: %s\n", audio.isRunning() ? "Playing" : "Stopped");
}
```

## Complete Example Code

```cpp
#include "Audio.h"
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>

Audio audio;
WebServer server(80);
WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  
  setupWiFi();
  setupAudio();
  setupWebServer();
  setupMQTT();
  
  Serial.println("ESP32 Smart Speaker Ready!");
}

void loop() {
  audio.loop();
  server.handleClient();
  
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();
  
  handleAudioEvents();
  delay(10);
}
```

This comprehensive programming guide covers all aspects of ESP32 smart speaker development, from basic setup to advanced IoT integration.
