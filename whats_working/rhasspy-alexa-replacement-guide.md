# Rhasspy Alexa Replacement Guide

## Overview
Complete guide for replacing Alexa Echo Dot with Rhasspy container-based voice assistant for Home Assistant, providing Alexa-like experience with complete local processing.

## Why Rhasspy is Best for Alexa Replacement

### Alexa-like Features
- **Wake Word Detection:** Custom wake words like "Hey Alexa"
- **Natural Language Processing:** Advanced speech recognition
- **Intent Training:** Train custom voice commands
- **Multi-language Support:** Extensive language support
- **Home Assistant Integration:** Seamless MQTT communication

### Advantages Over Alexa
- **Complete Privacy:** All processing happens locally
- **No Cloud Dependencies:** Works without internet
- **Custom Wake Words:** Set any wake word you want
- **Intent Training:** Train custom voice commands
- **Home Assistant Integration:** Direct MQTT communication
- **No Subscription Fees:** Completely free

## Mac Mini M4 Optimized Setup

### Hardware Requirements
- **Mac Mini M4:** Already owned ✅
- **USB Microphone:** $20-50 (one-time)
- **Speaker:** $30-100 (one-time)
- **Total:** $50-150 (one-time)

### Software Requirements
- **Docker Desktop:** Free
- **Rhasspy Container:** Free
- **MQTT Broker:** Free
- **Home Assistant:** Free
- **Total:** $0

## Docker Compose Configuration

### Complete Rhasspy Setup
```yaml
# docker-compose.yml
version: '3.8'

services:
  # MQTT Broker
  mqtt:
    image: eclipse-mosquitto:latest
    container_name: rhasspy-mqtt
    restart: unless-stopped
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mqtt/config:/mosquitto/config
      - ./mqtt/data:/mosquitto/data
    networks:
      - voice-assistant

  # Rhasspy Voice Assistant
  rhasspy:
    image: rhasspy/rhasspy:latest
    container_name: rhasspy-voice
    restart: unless-stopped
    ports:
      - "12101:12101"
    volumes:
      - ./rhasspy/profiles:/profiles
      - ./rhasspy/data:/data
      - ./rhasspy/logs:/logs
    environment:
      - RHASSPY_PROFILE=english
      - RHASSPY_LANGUAGE=en
      - RHASSPY_MICROPHONE=ALSA
      - RHASSPY_SPEAKER=ALSA
      - RHASSPY_MQTT_HOST=mqtt
      - RHASSPY_MQTT_PORT=1883
      - RHASSPY_MQTT_USERNAME=rhasspy
      - RHASSPY_MQTT_PASSWORD=your_secure_password
    depends_on:
      - mqtt
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '4.0'
        reservations:
          memory: 2G
          cpus: '2.0'
    networks:
      - voice-assistant

networks:
  voice-assistant:
    driver: bridge
    name: voice-assistant

volumes:
  mqtt_data:
  mqtt_log:
  rhasspy_profiles:
  rhasspy_data:
  rhasspy_logs:
```

## Home Assistant Integration

### MQTT Configuration
```yaml
# configuration.yaml
mqtt:
  broker: localhost
  port: 1883
  username: rhasspy
  password: your_secure_password

# Intent Scripts for Alexa-like Commands
intent_script:
  # Light Control
  TurnOnLight:
    action:
      - service: light.turn_on
        entity_id: light.living_room
    speech:
      text: "Turning on the living room light"

  TurnOffLight:
    action:
      - service: light.turn_off
        entity_id: light.living_room
    speech:
      text: "Turning off the living room light"

  # Temperature Control
  SetTemperature:
    action:
      - service: climate.set_temperature
        entity_id: climate.bedroom
        data:
          temperature: "{{ temperature }}"
    speech:
      text: "Setting bedroom temperature to {{ temperature }} degrees"

  # Scene Control
  StartScene:
    action:
      - service: scene.turn_on
        entity_id: "{{ scene }}"
    speech:
      text: "Starting {{ scene }}"

  # Status Queries
  GetStatus:
    action:
      - service: system_log.write
        data:
          message: "Status requested for {{ entity }}"
    speech:
      text: "The {{ entity }} is currently {{ state }}"
```

### Rhasspy Profile Configuration
```json
{
  "language": "en",
  "speech_to_text": {
    "system": "whisper",
    "whisper": {
      "model": "small",
      "language": "en",
      "beam_size": 1
    }
  },
  "text_to_speech": {
    "system": "piper",
    "piper": {
      "voice": "en-us-libritts-high",
      "speed": 1.0
    }
  },
  "wake_word": {
    "system": "porcupine",
    "porcupine": {
      "model": "hey_jarvis",
      "sensitivity": 0.5
    }
  },
  "intent": {
    "system": "fsticuffs",
    "fsticuffs": {
      "intent_graph": "intent.json"
    }
  },
  "microphone": {
    "system": "alsa",
    "alsa": {
      "device": "default"
    }
  },
  "speaker": {
    "system": "alsa",
    "alsa": {
      "device": "default"
    }
  }
}
```

## Custom Wake Word Setup

### Using "Hey Alexa" Wake Word
```yaml
# Rhasspy configuration
wake_word:
  system: porcupine
  porcupine:
    model: hey_jarvis  # Can be customized
    sensitivity: 0.5
```

### Custom Wake Word Training
1. **Access Rhasspy web interface** at `http://localhost:12101`
2. **Go to Wake Word section**
3. **Upload custom wake word model**
4. **Configure sensitivity settings**
5. **Test wake word detection**

## Intent Training

### Basic Intent Examples
```yaml
# Intent training examples
intent_script:
  # Light Control
  TurnOnLight:
    action:
      - service: light.turn_on
        entity_id: "{{ light }}"
    speech:
      text: "Turning on {{ light }}"

  # Temperature Control
  SetTemperature:
    action:
      - service: climate.set_temperature
        entity_id: "{{ climate }}"
        data:
          temperature: "{{ temperature }}"
    speech:
      text: "Setting {{ climate }} to {{ temperature }} degrees"

  # Scene Control
  StartScene:
    action:
      - service: scene.turn_on
        entity_id: "{{ scene }}"
    speech:
      text: "Starting {{ scene }}"
```

### Advanced Intent Training
```yaml
# Complex intent examples
intent_script:
  # Multi-step Commands
  GoodMorning:
    action:
      - service: scene.turn_on
        entity_id: scene.good_morning
      - service: tts.piper_say
        data:
          message: "Good morning! Starting your day."
    speech:
      text: "Good morning! Starting your day."

  # Conditional Commands
  SmartLightControl:
    action:
      - service: >
          {% if state == 'on' %}
            light.turn_off
          {% else %}
            light.turn_on
          {% endif %}
        entity_id: "{{ light }}"
    speech:
      text: "{{ light }} is now {{ state }}"
```

## Voice Command Examples

### Basic Commands (Alexa-like)
- **"Hey Alexa, turn on the living room light"**
- **"Hey Alexa, turn off the coffee maker"**
- **"Hey Alexa, set the bedroom temperature to 22 degrees"**
- **"Hey Alexa, what's the status of the living room light?"**

### Advanced Commands
- **"Hey Alexa, turn on all lights"**
- **"Hey Alexa, set the house to night mode"**
- **"Hey Alexa, start the morning routine"**
- **"Hey Alexa, what's the weather like?"**

### Custom Commands
- **"Hey Alexa, turn on the coffee maker"**
- **"Hey Alexa, set the house to movie mode"**
- **"Hey Alexa, what's the status of all devices?"**

## Setup Process

### 1. Prerequisites (15 minutes)
```bash
# Install Docker Desktop for Mac
# Download from: https://www.docker.com/products/docker-desktop/

# Verify installation
docker --version
docker-compose --version
```

### 2. Create Project Directory
```bash
mkdir rhasspy-alexa-replacement
cd rhasspy-alexa-replacement
```

### 3. Create Configuration Files
```bash
# Create directory structure
mkdir -p {mqtt,rhasspy}/{config,data,logs,profiles}

# Create docker-compose.yml (use configuration above)
# Create Home Assistant configuration additions
```

### 4. Start Services
```bash
# Start all services
docker-compose up -d

# Check status
docker ps

# View logs
docker-compose logs -f
```

### 5. Configure Rhasspy
1. **Access Rhasspy web interface** at `http://localhost:12101`
2. **Configure microphone and speaker**
3. **Set up wake word detection**
4. **Train custom sentences and intents**

### 6. Configure Home Assistant
1. **Add MQTT configuration** to Home Assistant
2. **Add intent scripts** for voice commands
3. **Test voice commands** and functionality

## Performance Optimization for Mac Mini M4

### Resource Allocation
```yaml
# Optimize for M4 chip
services:
  rhasspy:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '4.0'
        reservations:
          memory: 2G
          cpus: '2.0'
```

### Audio Configuration
```bash
# Check audio devices
system_profiler SPAudioDataType

# Test microphone
ffmpeg -f avfoundation -i ":0" -t 5 test.wav
aplay test.wav
```

## Troubleshooting

### Common Issues
1. **Audio Hardware Problems**
   ```bash
   # Check audio devices
   system_profiler SPAudioDataType
   
   # Test microphone
   ffmpeg -f avfoundation -i ":0" -t 5 test.wav
   ```

2. **Container Issues**
   ```bash
   # Check container status
   docker ps -a
   
   # Check logs
   docker logs rhasspy-voice
   ```

3. **MQTT Issues**
   ```bash
   # Check MQTT connection
   docker exec -it rhasspy-voice mosquitto_pub -h mqtt -t test -m "hello"
   ```

### Debug Commands
```bash
# Check container status
docker ps -a

# Check logs
docker logs rhasspy-voice
docker logs rhasspy-mqtt

# Monitor resources
docker stats
```

## Security and Privacy Benefits

### Complete Privacy
- **No Cloud Dependencies:** All processing happens locally
- **No Data Transmission:** Voice data never leaves your network
- **Local Storage:** All data stored on your Mac Mini
- **No Tracking:** No external tracking or analytics

### Security Advantages
- **Container Isolation:** Voice processing in isolated containers
- **Network Isolation:** Voice processing on local network only
- **No External Dependencies:** No reliance on external services
- **Custom Security:** Full control over security measures

## Cost Analysis

### Hardware Costs
- **Mac Mini M4:** Already owned ✅
- **USB Microphone:** $20-50 (one-time)
- **Speaker:** $30-100 (one-time)
- **Total:** $50-150 (one-time)

### Software Costs
- **Docker Desktop:** Free
- **Rhasspy:** Free
- **MQTT Broker:** Free
- **Home Assistant:** Free
- **Total:** $0

### Ongoing Costs
- **No subscription fees**
- **No cloud service costs**
- **No external dependencies**
- **Total:** $0/month

## Conclusion

Rhasspy provides the best Alexa replacement solution for Home Assistant with:

- **Alexa-like Experience:** Complete voice assistant functionality
- **Complete Privacy:** All processing happens locally
- **No Cloud Dependencies:** Works without internet
- **Custom Wake Words:** Set any wake word you want
- **Intent Training:** Train custom voice commands
- **Home Assistant Integration:** Seamless MQTT communication
- **Zero Cost:** Completely free and open-source

**Recommended Implementation:**
1. **Start with basic Rhasspy setup** for immediate results
2. **Configure custom wake words** like "Hey Alexa"
3. **Train custom intents** for Alexa-like commands
4. **Optimize performance** for Mac Mini M4
5. **Gradually replace Alexa functionality** with local solutions

The implementation provides a complete Alexa replacement with better privacy, security, and control over your smart home system.
