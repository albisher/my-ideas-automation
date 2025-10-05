# Complete Code Examples

## 1. Basic Audio Player

### Simple Audio Test
```cpp
#include "Audio.h"

Audio audio;

void setup() {
  Serial.begin(115200);
  
  // Configure I2S pins
  audio.setPinout(26, 25, 27);
  audio.setVolume(15);
  
  // Play test audio
  audio.connecttohost("http://www.soundjay.com/misc/sounds/bell-ringing-05.wav");
}

void loop() {
  audio.loop();
  
  if (audio.isRunning()) {
    Serial.println("Audio playing...");
  }
}
```

### Audio with Controls
```cpp
#include "Audio.h"
#include <WiFi.h>
#include <WebServer.h>

Audio audio;
WebServer server(80);

void setup() {
  Serial.begin(115200);
  
  // WiFi setup
  WiFi.begin("YourWiFi", "YourPassword");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  
  // Audio setup
  audio.setPinout(26, 25, 27);
  audio.setVolume(15);
  
  // Web server setup
  server.on("/", handleRoot);
  server.on("/play", handlePlay);
  server.on("/stop", handleStop);
  server.on("/volume", handleVolume);
  server.begin();
  
  Serial.println("Server started");
}

void loop() {
  audio.loop();
  server.handleClient();
}

void handleRoot() {
  String html = "<!DOCTYPE html><html><head><title>ESP32 Speaker</title></head>";
  html += "<body><h1>ESP32 Smart Speaker</h1>";
  html += "<button onclick='play()'>Play</button>";
  html += "<button onclick='stop()'>Stop</button>";
  html += "<input type='range' id='volume' min='0' max='21' value='15'>";
  html += "<script>function play(){fetch('/play')} function stop(){fetch('/stop')}</script>";
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

void handlePlay() {
  audio.connecttohost("http://stream.url");
  server.send(200, "text/plain", "Playing");
}

void handleStop() {
  audio.stopSong();
  server.send(200, "text/plain", "Stopped");
}

void handleVolume() {
  if (server.hasArg("volume")) {
    int volume = server.arg("volume").toInt();
    audio.setVolume(volume);
    server.send(200, "text/plain", "Volume set to " + String(volume));
  }
}
```

## 2. Voice Command System

### Basic Voice Recognition
```cpp
#include "Audio.h"
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

Audio audio;
WebServer server(80);

// Voice command keywords
String wakeWords[] = {"hey", "speaker", "assistant"};
String playCommands[] = {"play", "start", "begin"};
String stopCommands[] = {"stop", "pause", "end"};
String volumeCommands[] = {"volume", "louder", "quieter"};

void setup() {
  Serial.begin(115200);
  
  // WiFi setup
  WiFi.begin("YourWiFi", "YourPassword");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  
  // Audio setup
  audio.setPinout(26, 25, 27);
  audio.setVolume(15);
  
  // Web server setup
  server.on("/", handleRoot);
  server.on("/voice", handleVoice);
  server.begin();
  
  Serial.println("Voice-controlled speaker ready!");
}

void loop() {
  audio.loop();
  server.handleClient();
}

void handleRoot() {
  String html = "<!DOCTYPE html><html><head><title>Voice Speaker</title></head>";
  html += "<body><h1>Voice-Controlled Speaker</h1>";
  html += "<button onclick='startListening()'>Start Listening</button>";
  html += "<div id='status'>Ready</div>";
  html += "<script>";
  html += "function startListening(){";
  html += "  document.getElementById('status').innerHTML='Listening...';";
  html += "  // Voice recognition code here";
  html += "}";
  html += "</script>";
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

void handleVoice() {
  if (server.hasArg("command")) {
    String command = server.arg("command");
    processVoiceCommand(command);
    server.send(200, "text/plain", "Command processed");
  }
}

void processVoiceCommand(String command) {
  command.toLowerCase();
  
  // Check for wake words
  bool isWakeWord = false;
  for (String word : wakeWords) {
    if (command.indexOf(word) >= 0) {
      isWakeWord = true;
      break;
    }
  }
  
  if (!isWakeWord) return;
  
  // Process play commands
  for (String cmd : playCommands) {
    if (command.indexOf(cmd) >= 0) {
      if (command.indexOf("music") >= 0) {
        playMusic();
      } else if (command.indexOf("radio") >= 0) {
        playRadio();
      }
      return;
    }
  }
  
  // Process stop commands
  for (String cmd : stopCommands) {
    if (command.indexOf(cmd) >= 0) {
      audio.stopSong();
      return;
    }
  }
  
  // Process volume commands
  for (String cmd : volumeCommands) {
    if (command.indexOf(cmd) >= 0) {
      int volume = extractVolume(command);
      audio.setVolume(volume);
      return;
    }
  }
}

int extractVolume(String command) {
  int start = command.indexOf("volume") + 7;
  int end = command.indexOf(" ", start);
  if (end == -1) end = command.length();
  
  String volumeStr = command.substring(start, end);
  return volumeStr.toInt();
}

void playMusic() {
  audio.connecttohost("http://stream.url");
}

void playRadio() {
  audio.connecttohost("http://radio.url");
}
```

## 3. MQTT IoT Integration

### MQTT Audio Controller
```cpp
#include "Audio.h"
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

Audio audio;
WiFiClient espClient;
PubSubClient client(espClient);

const char* mqtt_server = "your-mqtt-broker.com";
const char* mqtt_user = "username";
const char* mqtt_password = "password";

void setup() {
  Serial.begin(115200);
  
  // WiFi setup
  WiFi.begin("YourWiFi", "YourPassword");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  
  // Audio setup
  audio.setPinout(26, 25, 27);
  audio.setVolume(15);
  
  // MQTT setup
  client.setServer(mqtt_server, 1883);
  client.setCallback(mqttCallback);
  
  Serial.println("MQTT Audio Controller ready!");
}

void loop() {
  audio.loop();
  
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();
  
  // Publish status periodically
  static unsigned long lastStatus = 0;
  if (millis() - lastStatus > 30000) {
    publishStatus();
    lastStatus = millis();
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  Serial.println("Received: " + message);
  
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
    publishStatus();
  } else if (action == "stop") {
    audio.stopSong();
    publishStatus();
  } else if (action == "volume") {
    int volume = doc["volume"];
    audio.setVolume(volume);
    publishStatus();
  } else if (action == "pause") {
    audio.pauseResume();
    publishStatus();
  }
}

void reconnectMQTT() {
  while (!client.connected()) {
    if (client.connect("ESP32-Speaker", mqtt_user, mqtt_password)) {
      client.subscribe("speaker/control");
      client.publish("speaker/status", "online");
    } else {
      delay(5000);
    }
  }
}

void publishStatus() {
  DynamicJsonDocument doc(1024);
  doc["status"] = audio.isRunning() ? "playing" : "stopped";
  doc["volume"] = audio.getVolume();
  doc["current_track"] = audio.getCurrentTrack();
  doc["uptime"] = millis() / 1000;
  
  String payload;
  serializeJson(doc, payload);
  client.publish("speaker/status", payload.c_str());
}
```

## 4. Home Assistant Integration

### Home Assistant Media Player
```cpp
#include "Audio.h"
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

Audio audio;
WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  
  // WiFi setup
  WiFi.begin("YourWiFi", "YourPassword");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  
  // Audio setup
  audio.setPinout(26, 25, 27);
  audio.setVolume(15);
  
  // MQTT setup
  client.setServer("your-mqtt-broker.com", 1883);
  client.setCallback(mqttCallback);
  
  // Publish Home Assistant discovery
  publishHADiscovery();
  
  Serial.println("Home Assistant integration ready!");
}

void loop() {
  audio.loop();
  
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();
}

void publishHADiscovery() {
  DynamicJsonDocument config(1024);
  config["name"] = "ESP32 Smart Speaker";
  config["unique_id"] = "esp32_speaker_001";
  config["device_class"] = "speaker";
  config["state_topic"] = "homeassistant/media_player/esp32_speaker/state";
  config["command_topic"] = "homeassistant/media_player/esp32_speaker/set";
  config["volume_state_topic"] = "homeassistant/media_player/esp32_speaker/volume";
  config["volume_command_topic"] = "homeassistant/media_player/esp32_speaker/volume/set";
  
  String configPayload;
  serializeJson(config, configPayload);
  client.publish("homeassistant/media_player/esp32_speaker/config", configPayload.c_str());
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  if (String(topic) == "homeassistant/media_player/esp32_speaker/set") {
    processHACommand(message);
  } else if (String(topic) == "homeassistant/media_player/esp32_speaker/volume/set") {
    int volume = message.toInt();
    audio.setVolume(volume);
    publishHAState();
  }
}

void processHACommand(String command) {
  if (command == "PLAY") {
    audio.connecttohost("http://stream.url");
  } else if (command == "PAUSE") {
    audio.pauseResume();
  } else if (command == "STOP") {
    audio.stopSong();
  }
  
  publishHAState();
}

void publishHAState() {
  DynamicJsonDocument doc(1024);
  doc["state"] = audio.isRunning() ? "playing" : "stopped";
  doc["volume"] = audio.getVolume();
  doc["current_track"] = audio.getCurrentTrack();
  
  String payload;
  serializeJson(doc, payload);
  client.publish("homeassistant/media_player/esp32_speaker/state", payload.c_str());
}
```

## 5. Advanced Features

### Multi-Room Audio System
```cpp
#include "Audio.h"
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

Audio audio;
WiFiClient espClient;
PubSubClient client(espClient);

String roomName = "living_room";
String groupName = "downstairs";

void setup() {
  Serial.begin(115200);
  
  // WiFi setup
  WiFi.begin("YourWiFi", "YourPassword");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  
  // Audio setup
  audio.setPinout(26, 25, 27);
  audio.setVolume(15);
  
  // MQTT setup
  client.setServer("your-mqtt-broker.com", 1883);
  client.setCallback(mqttCallback);
  
  // Subscribe to room and group topics
  client.subscribe("speaker/" + roomName + "/control");
  client.subscribe("speaker/group/" + groupName + "/control");
  client.subscribe("speaker/all/control");
  
  Serial.println("Multi-room audio system ready!");
}

void loop() {
  audio.loop();
  
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  if (String(topic) == "speaker/" + roomName + "/control") {
    processRoomCommand(message);
  } else if (String(topic) == "speaker/group/" + groupName + "/control") {
    processGroupCommand(message);
  } else if (String(topic) == "speaker/all/control") {
    processAllCommand(message);
  }
}

void processRoomCommand(String command) {
  // Process commands for this specific room
  processAudioCommand(command);
}

void processGroupCommand(String command) {
  // Process commands for the group
  processAudioCommand(command);
}

void processAllCommand(String command) {
  // Process commands for all speakers
  processAudioCommand(command);
}

void processAudioCommand(String command) {
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

These code examples provide a complete foundation for building your ESP32 smart speaker with various features and integrations.
