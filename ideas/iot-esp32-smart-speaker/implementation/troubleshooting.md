# Troubleshooting Guide

## Common Issues and Solutions

### 1. Hardware Issues

#### ESP32 Not Responding
**Symptoms:**
- No serial output
- LED not blinking
- Upload fails

**Solutions:**
```bash
# Check power supply
- Verify 5V input voltage
- Check current capacity (2A minimum)
- Test with multimeter

# Check connections
- Verify VIN to 5V
- Check GND connections
- Ensure proper breadboard connections

# Reset ESP32
- Press and hold EN button
- Press and release RST button
- Release EN button
```

#### Audio Not Working
**Symptoms:**
- No sound from speaker
- Distorted audio
- Audio cuts out

**Solutions:**
```bash
# Check I2S connections
- Verify BCLK, LRC, DIN pins
- Check power to MAX98357A
- Test with multimeter

# Speaker connections
- Verify speaker polarity
- Check speaker impedance (4-8 ohms)
- Test speaker with multimeter

# Audio settings
- Check sample rate (44100 Hz)
- Verify bit depth (16-bit)
- Test with different audio sources
```

#### Microphone Issues
**Symptoms:**
- No audio input
- Poor voice recognition
- Audio feedback

**Solutions:**
```bash
# I2S microphone connections
- Verify WS, SD, SCK pins
- Check power supply (3.3V)
- Test with oscilloscope

# Audio processing
- Check sample rate settings
- Verify buffer sizes
- Test with different microphones
```

### 2. Software Issues

#### WiFi Connection Problems
**Symptoms:**
- Cannot connect to WiFi
- Intermittent connection
- Slow response

**Solutions:**
```cpp
// WiFi debugging code
void debugWiFi() {
  Serial.println("WiFi Status: " + String(WiFi.status()));
  Serial.println("SSID: " + String(WiFi.SSID()));
  Serial.println("RSSI: " + String(WiFi.RSSI()) + " dBm");
  Serial.println("IP: " + WiFi.localIP().toString());
}

// WiFi reconnection
void reconnectWiFi() {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.disconnect();
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.println("Reconnecting to WiFi...");
    }
  }
}
```

#### Audio Library Issues
**Symptoms:**
- Audio library not found
- Compilation errors
- Runtime crashes

**Solutions:**
```bash
# Install correct library version
1. Go to Library Manager
2. Search "ESP32-audioI2S"
3. Install version 2.5.0 or later
4. Check for conflicts with other libraries

# Library configuration
#include "Audio.h"
Audio audio;

void setup() {
  // Configure I2S pins
  audio.setPinout(26, 25, 27);
  
  // Set audio parameters
  audio.setVolume(15);
  audio.setConnectionTimeout(10000, 1000);
}
```

#### Memory Issues
**Symptoms:**
- Random crashes
- Audio stuttering
- Out of memory errors

**Solutions:**
```cpp
// Memory monitoring
void checkMemory() {
  Serial.println("Free heap: " + String(ESP.getFreeHeap()) + " bytes");
  Serial.println("Free PSRAM: " + String(ESP.getFreePsram()) + " bytes");
  Serial.println("Heap size: " + String(ESP.getHeapSize()) + " bytes");
}

// Memory optimization
void optimizeMemory() {
  // Reduce buffer sizes
  audio.setBufsize(512, 256);
  
  // Close unused connections
  // Free unused variables
  // Use smaller data types
}
```

### 3. Network Issues

#### MQTT Connection Problems
**Symptoms:**
- Cannot connect to MQTT broker
- Messages not received
- Connection drops

**Solutions:**
```cpp
// MQTT debugging
void debugMQTT() {
  Serial.println("MQTT Connected: " + String(client.connected()));
  Serial.println("MQTT Server: " + String(mqtt_server));
  Serial.println("MQTT Port: " + String(1883));
}

// MQTT reconnection
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
```

#### Web Server Issues
**Symptoms:**
- Cannot access web interface
- Pages not loading
- Server crashes

**Solutions:**
```cpp
// Web server debugging
void debugWebServer() {
  Serial.println("Web server running on port 80");
  Serial.println("IP address: " + WiFi.localIP().toString());
}

// Error handling
void handleNotFound() {
  server.send(404, "text/plain", "Not found");
}

// Server monitoring
void monitorWebServer() {
  if (server.hasArg("error")) {
    Serial.println("Web server error: " + server.arg("error"));
  }
}
```

### 4. Performance Issues

#### Audio Quality Problems
**Symptoms:**
- Audio distortion
- Dropouts
- Poor quality

**Solutions:**
```cpp
// Audio quality optimization
void optimizeAudio() {
  // Increase buffer sizes
  audio.setBufsize(1024, 512);
  
  // Optimize I2S settings
  audio.setI2SCommFMT_LSB(true);
  
  // Reduce CPU usage
  audio.setConnectionTimeout(5000, 1000);
}
```

#### System Performance
**Symptoms:**
- Slow response
- High CPU usage
- System crashes

**Solutions:**
```cpp
// Performance monitoring
void monitorPerformance() {
  Serial.println("Free heap: " + String(ESP.getFreeHeap()));
  Serial.println("CPU frequency: " + String(ESP.getCpuFreqMHz()) + " MHz");
  Serial.println("Uptime: " + String(millis() / 1000) + " seconds");
}

// Performance optimization
void optimizePerformance() {
  // Reduce task priorities
  // Use smaller data types
  // Minimize string operations
  // Optimize loop timing
}
```

### 5. Debugging Tools

#### Serial Debugging
```cpp
// Comprehensive debugging
void debugSystem() {
  Serial.println("=== System Debug Info ===");
  Serial.println("Free heap: " + String(ESP.getFreeHeap()) + " bytes");
  Serial.println("WiFi status: " + String(WiFi.status()));
  Serial.println("WiFi RSSI: " + String(WiFi.RSSI()) + " dBm");
  Serial.println("Audio status: " + String(audio.isRunning() ? "Playing" : "Stopped"));
  Serial.println("MQTT connected: " + String(client.connected()));
  Serial.println("Uptime: " + String(millis() / 1000) + " seconds");
}
```

#### LED Status Indicators
```cpp
// Status LED system
void setupStatusLEDs() {
  pinMode(2, OUTPUT);  // WiFi status
  pinMode(4, OUTPUT);  // Audio status
}

void updateStatusLEDs() {
  // WiFi status LED
  digitalWrite(2, WiFi.status() == WL_CONNECTED ? HIGH : LOW);
  
  // Audio status LED
  digitalWrite(4, audio.isRunning() ? HIGH : LOW);
}
```

#### Error Logging
```cpp
// Error logging system
void logError(String error) {
  Serial.println("ERROR: " + error);
  // Send to MQTT broker
  client.publish("speaker/errors", error.c_str());
}

// System health check
void healthCheck() {
  if (ESP.getFreeHeap() < 10000) {
    logError("Low memory: " + String(ESP.getFreeHeap()));
  }
  
  if (WiFi.status() != WL_CONNECTED) {
    logError("WiFi disconnected");
  }
  
  if (!client.connected()) {
    logError("MQTT disconnected");
  }
}
```

### 6. Testing Procedures

#### Hardware Testing
```cpp
// Pin testing
void testPins() {
  // Test I2S pins
  pinMode(26, OUTPUT);
  digitalWrite(26, HIGH);
  delay(100);
  digitalWrite(26, LOW);
  
  // Test GPIO pins
  for (int pin = 2; pin <= 4; pin++) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, HIGH);
    delay(100);
    digitalWrite(pin, LOW);
  }
}
```

#### Audio Testing
```cpp
// Audio system test
void testAudio() {
  // Test I2S configuration
  audio.setPinout(26, 25, 27);
  audio.setVolume(10);
  
  // Test with simple tone
  audio.connecttohost("http://www.soundjay.com/misc/sounds/bell-ringing-05.wav");
  
  // Monitor audio status
  if (audio.isRunning()) {
    Serial.println("Audio test passed");
  } else {
    Serial.println("Audio test failed");
  }
}
```

#### Network Testing
```cpp
// Network connectivity test
void testNetwork() {
  // Test WiFi
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WiFi test passed");
  } else {
    Serial.println("WiFi test failed");
  }
  
  // Test MQTT
  if (client.connected()) {
    Serial.println("MQTT test passed");
  } else {
    Serial.println("MQTT test failed");
  }
}
```

This troubleshooting guide covers the most common issues you might encounter when building and programming your ESP32 smart speaker project.
