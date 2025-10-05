# Free Container Voice Assistant Options for Mac Mini M4

## Overview
Complete guide for free, open-source container-based voice assistant solutions that work with Home Assistant on your Mac Mini M4, eliminating all external service provider dependencies.

## Free Container Solutions

### 1. Wyoming Protocol Components (RECOMMENDED)

#### Overview
Modular voice assistant components using the Wyoming protocol, completely free and open-source.

#### Components
- **Whisper** - Speech-to-text processing
- **Piper** - Text-to-speech synthesis  
- **OpenWakeWord** - Wake word detection
- **Wyoming Server** - Protocol server

#### Docker Images (All Free)
```yaml
# Free Docker images
rhasspy/wyoming-whisper:latest    # Speech-to-text
rhasspy/wyoming-piper:latest      # Text-to-speech
rhasspy/wyoming-openwakeword:latest # Wake word detection
rhasspy/wyoming-server:latest     # Protocol server
eclipse-mosquitto:latest          # MQTT broker
```

#### Features
- **Completely Free:** No costs, no subscriptions
- **Modular Design:** Mix and match components
- **Local Processing:** All processing happens locally
- **Privacy-Focused:** No data leaves your network
- **Offline Capable:** Works without internet

### 2. Rhasspy (COMPLETE SOLUTION)

#### Overview
Complete voice assistant solution in a single container, fully open-source.

#### Docker Image
```yaml
# Free Docker image
rhasspy/rhasspy:latest
```

#### Features
- **All-in-One:** Complete voice assistant in one container
- **MQTT Integration:** Communicates with Home Assistant via MQTT
- **Customizable:** Train custom sentences and intents
- **Wake Word Support:** Custom wake word detection
- **Multiple Languages:** Extensive language support

### 3. Mycroft (ALTERNATIVE)

#### Overview
Open-source voice assistant platform with Home Assistant integration.

#### Docker Image
```yaml
# Free Docker image
mycroftai/mycroft-core:latest
```

#### Features
- **Privacy-Focused:** Designed for local processing
- **Skill System:** Extensible with custom skills
- **Home Assistant Integration:** Via MQTT or HTTP
- **Customizable:** Full control over functionality

### 4. OpenVoiceOS (OVOS) (ADVANCED)

#### Overview
Advanced open-source voice assistant platform with extensive customization.

#### Docker Image
```yaml
# Free Docker image
opendatahub/ovos:latest
```

#### Features
- **Advanced Features:** Sophisticated voice processing
- **Plugin System:** Extensive plugin ecosystem
- **Home Assistant Integration:** Multiple integration methods
- **High Customization:** Maximum control over functionality

## Mac Mini M4 Optimized Setup

### Hardware Advantages
- **M4 Chip:** Powerful ARM processor for voice processing
- **Unified Memory:** Efficient memory management
- **Neural Engine:** Hardware acceleration for AI tasks
- **USB-C:** High-speed connectivity for audio devices

### Recommended Configuration
```yaml
# docker-compose.yml for Mac Mini M4
version: '3.8'

services:
  # MQTT Broker
  mqtt:
    image: eclipse-mosquitto:latest
    container_name: voice-mqtt
    restart: unless-stopped
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mqtt/config:/mosquitto/config
      - ./mqtt/data:/mosquitto/data

  # Whisper Speech-to-Text
  whisper:
    image: rhasspy/wyoming-whisper:latest
    container_name: whisper-stt
    restart: unless-stopped
    ports:
      - "10301:10300"
    command: --model small --language en --beam-size 1
    volumes:
      - ./whisper/models:/models
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'

  # Piper Text-to-Speech
  piper:
    image: rhasspy/wyoming-piper:latest
    container_name: piper-tts
    restart: unless-stopped
    ports:
      - "10201:10200"
    command: --voice en-us-libritts-high
    volumes:
      - ./piper/voices:/voices
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'

  # OpenWakeWord
  openwakeword:
    image: rhasspy/wyoming-openwakeword:latest
    container_name: openwakeword
    restart: unless-stopped
    ports:
      - "10101:10100"
    command: --model hey_jarvis
    volumes:
      - ./openwakeword/models:/models

  # Wyoming Server
  wyoming-server:
    image: rhasspy/wyoming-server:latest
    container_name: wyoming-server
    restart: unless-stopped
    ports:
      - "10400:10400"
    environment:
      - WYOMING_SERVER_PORT=10400
      - WYOMING_SERVER_HOST=0.0.0.0
    depends_on:
      - whisper
      - piper
      - openwakeword

  # Rhasspy (Alternative complete solution)
  rhasspy:
    image: rhasspy/rhasspy:latest
    container_name: rhasspy-voice
    restart: unless-stopped
    ports:
      - "12101:12101"
    volumes:
      - ./rhasspy/profiles:/profiles
      - ./rhasspy/data:/data
    environment:
      - RHASSPY_PROFILE=english
      - RHASSPY_LANGUAGE=en
      - RHASSPY_MQTT_HOST=mqtt
      - RHASSPY_MQTT_PORT=1883
    depends_on:
      - mqtt

networks:
  default:
    name: voice-assistant
```

## Home Assistant Integration

### Wyoming Protocol Integration
```yaml
# configuration.yaml
wyoming:
  stt:
    - url: "http://localhost:10301"
  tts:
    - url: "http://localhost:10201"
  wake_word:
    - url: "http://localhost:10101"

# Assist Pipeline
assist_pipeline:
  - language: en
    name: "Local Voice Assistant"
    wake_word: "hey_home_assistant"
    stt_engine: "wyoming"
    tts_engine: "wyoming"
    wake_word_engine: "wyoming"
```

### Rhasspy Integration
```yaml
# configuration.yaml
mqtt:
  broker: localhost
  port: 1883
  username: rhasspy
  password: your_password

# Intent Scripts
intent_script:
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
```

## Setup Instructions

### 1. Prerequisites
```bash
# Install Docker Desktop for Mac
# Download from: https://www.docker.com/products/docker-desktop/

# Verify installation
docker --version
docker-compose --version
```

### 2. Create Project Directory
```bash
mkdir voice-assistant
cd voice-assistant
```

### 3. Create Configuration Files
```bash
# Create directory structure
mkdir -p {mqtt,whisper,piper,openwakeword,rhasspy}/{config,data,models,voices,profiles}

# Create docker-compose.yml (use the configuration above)
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

### 5. Configure Home Assistant
1. Add Wyoming protocol integrations
2. Configure Assist pipeline
3. Test voice commands

## Performance Optimization for Mac Mini M4

### Resource Allocation
```yaml
# Optimize for M4 chip
services:
  whisper:
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
```

## Cost Analysis

### Hardware Costs
- **Mac Mini M4:** Already owned ✅
- **USB Microphone:** $20-50 (one-time)
- **Speaker:** $30-100 (one-time)
- **Total:** $50-150 (one-time)

### Software Costs
- **Docker Desktop:** Free
- **All Voice Assistant Components:** Free
- **Home Assistant:** Free
- **Total:** $0

### Ongoing Costs
- **No subscription fees**
- **No cloud service costs**
- **No external dependencies**
- **Total:** $0/month

## Voice Command Examples

### Basic Commands
- **"Hey Home Assistant, turn on the living room light"**
- **"Hey Home Assistant, turn off the coffee maker"**
- **"Hey Home Assistant, set the bedroom temperature to 22 degrees"**
- **"Hey Home Assistant, what's the status of the living room light?"**

### Advanced Commands
- **"Hey Home Assistant, turn on all lights"**
- **"Hey Home Assistant, set the house to night mode"**
- **"Hey Home Assistant, start the morning routine"**
- **"Hey Home Assistant, what's the weather like?"**

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
   docker logs whisper-stt
   docker logs piper-tts
   ```

3. **Performance Issues**
   ```bash
   # Monitor resources
   docker stats
   
   # Check system resources
   top
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

## Recommendations

### For Beginners
**Wyoming Protocol Components** - Modular and well-documented

### For Complete Solution
**Rhasspy** - All-in-one voice assistant

### For Advanced Users
**OpenVoiceOS** - Maximum customization

### For Mac Mini M4
**Wyoming Protocol** - Optimized for M4 chip performance

## Conclusion

All container-based voice assistant solutions are completely free and open-source, providing:

- **Zero Cost:** No subscription fees or ongoing costs
- **Complete Privacy:** All processing happens locally
- **Offline Capable:** Works without internet connection
- **Mac Mini M4 Optimized:** Leverages M4 chip performance
- **Home Assistant Integration:** Seamless integration with your existing setup

The recommended approach is to start with **Wyoming Protocol Components** for modularity and ease of setup, then consider **Rhasspy** for a complete all-in-one solution.
