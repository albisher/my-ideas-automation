# Container-Based Local Voice Assistant Guide

## Overview
Complete guide for setting up a fully local voice assistant system using Docker containers with Home Assistant, eliminating all external service provider dependencies.

## Prerequisites

### Hardware Requirements
- **Home Assistant** running in Docker (your current setup)
- **Dedicated server** or **Raspberry Pi 4+** for voice processing
- **USB Microphone** (array recommended)
- **Speaker system**
- **Minimum 4GB RAM** (8GB recommended)
- **32GB+ storage**

### Software Requirements
- **Docker** and **Docker Compose**
- **Home Assistant** (your existing setup)
- **Network connectivity** between containers

## Container-Based Solutions

### 1. Rhasspy Container Solution (RECOMMENDED)

#### Overview
Rhasspy provides a complete containerized voice assistant solution that integrates with Home Assistant via MQTT.

#### Features
- **Completely Offline:** No internet connection required
- **Customizable:** Train custom sentences and intents
- **Wake Word Support:** Custom wake word detection
- **MQTT Integration:** Communicates with Home Assistant
- **Multiple Languages:** Extensive language support

#### Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  rhasspy:
    image: rhasspy/rhasspy:latest
    container_name: rhasspy
    restart: unless-stopped
    ports:
      - "12101:12101"
    volumes:
      - ./rhasspy/profiles:/profiles
      - ./rhasspy/data:/data
    environment:
      - RHASSPY_PROFILE=english
      - RHASSPY_LANGUAGE=en
      - RHASSPY_MICROPHONE=ALSA
      - RHASSPY_SPEAKER=ALSA
    devices:
      - /dev/snd:/dev/snd
    privileged: true
    network_mode: host

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
      - ./mqtt/log:/mosquitto/log
    environment:
      - MQTT_USERNAME=rhasspy
      - MQTT_PASSWORD=your_password
```

#### Setup Process
1. **Create directory structure:**
   ```bash
   mkdir -p rhasspy-voice-assistant/{rhasspy,mqtt}/{profiles,data,config,log}
   cd rhasspy-voice-assistant
   ```

2. **Create MQTT configuration:**
   ```bash
   # mqtt/config/mosquitto.conf
   listener 1883
   allow_anonymous true
   
   listener 9001
   protocol websockets
   allow_anonymous true
   ```

3. **Start services:**
   ```bash
   docker-compose up -d
   ```

4. **Configure Rhasspy:**
   - Access Rhasspy web interface at `http://localhost:12101`
   - Configure microphone and speaker
   - Set up wake word detection
   - Train custom sentences

### 2. Wyoming Protocol Solution (ADVANCED)

#### Overview
Wyoming protocol provides modular voice assistant components that can be mixed and matched.

#### Components
- **Whisper (STT):** Speech-to-text processing
- **Piper (TTS):** Text-to-speech synthesis
- **OpenWakeWord:** Wake word detection
- **Wyoming Server:** Protocol server

#### Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  wyoming-server:
    image: rhasspy/wyoming-server:latest
    container_name: wyoming-server
    restart: unless-stopped
    ports:
      - "10400:10400"
    environment:
      - WYOMING_SERVER_PORT=10400
      - WYOMING_SERVER_HOST=0.0.0.0
    volumes:
      - ./wyoming/config:/config
    depends_on:
      - whisper
      - piper
      - openwakeword

  whisper:
    image: rhasspy/wyoming-whisper:latest
    container_name: wyoming-whisper
    restart: unless-stopped
    ports:
      - "10301:10300"
    command: --model small --language en --beam-size 1
    volumes:
      - ./whisper/models:/models

  piper:
    image: rhasspy/wyoming-piper:latest
    container_name: wyoming-piper
    restart: unless-stopped
    ports:
      - "10201:10200"
    command: --voice en-us-libritts-high
    volumes:
      - ./piper/voices:/voices

  openwakeword:
    image: rhasspy/wyoming-openwakeword:latest
    container_name: wyoming-openwakeword
    restart: unless-stopped
    ports:
      - "10101:10100"
    command: --model hey_jarvis
    volumes:
      - ./openwakeword/models:/models

  mqtt:
    image: eclipse-mosquitto:latest
    container_name: wyoming-mqtt
    restart: unless-stopped
    ports:
      - "1883:1883"
    volumes:
      - ./mqtt/config:/mosquitto/config
```

### 3. Home Assistant Add-on Containers

#### Overview
Use Home Assistant's add-on system to run voice assistant components in containers.

#### Available Add-ons
- **Whisper:** Speech-to-text processing
- **Piper:** Text-to-speech synthesis
- **Porcupine:** Wake word detection
- **Wyoming Server:** Protocol server

#### Configuration
```yaml
# configuration.yaml
assist_pipeline:
  - language: en
    name: "Local Voice Assistant"
    wake_word: "hey_home_assistant"
    stt_engine: "whisper"
    tts_engine: "piper"
    wake_word_engine: "porcupine"
```

## Integration with Home Assistant

### 1. MQTT Integration (Rhasspy)
```yaml
# configuration.yaml
mqtt:
  broker: localhost
  port: 1883
  username: rhasspy
  password: your_password

# Intent handling
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

  SetTemperature:
    action:
      - service: climate.set_temperature
        entity_id: climate.bedroom
        data:
          temperature: "{{ temperature }}"
    speech:
      text: "Setting bedroom temperature to {{ temperature }} degrees"
```

### 2. Wyoming Protocol Integration
```yaml
# configuration.yaml
wyoming:
  stt:
    - url: "http://localhost:10301"
  tts:
    - url: "http://localhost:10201"
  wake_word:
    - url: "http://localhost:10101"
```

### 3. Assist Pipeline Configuration
```yaml
# configuration.yaml
assist_pipeline:
  - language: en
    name: "Local Voice Assistant"
    wake_word: "hey_home_assistant"
    stt_engine: "wyoming"
    tts_engine: "wyoming"
    wake_word_engine: "wyoming"
```

## Hardware Setup

### Audio Configuration
```bash
# Check audio devices
arecord -l
aplay -l

# Test microphone
arecord -f cd -d 5 test.wav
aplay test.wav

# Configure audio in containers
docker run --rm -it --device /dev/snd rhasspy/rhasspy:latest
```

### Network Configuration
```bash
# Create network for voice assistant
docker network create voice-assistant

# Connect containers to network
docker network connect voice-assistant homeassistant
docker network connect voice-assistant rhasspy
```

## Performance Optimization

### Hardware Requirements
- **Minimum:** Raspberry Pi 4 (4GB RAM)
- **Recommended:** Raspberry Pi 4 (8GB RAM) or better
- **Optimal:** Intel Core i5 or better

### Container Resource Limits
```yaml
# docker-compose.yml
services:
  rhasspy:
    image: rhasspy/rhasspy:latest
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

### Performance Tuning
```yaml
# Rhasspy configuration
rhasspy:
  speech_to_text:
    system: whisper
    whisper:
      model: small
      language: en
      beam_size: 1
  
  text_to_speech:
    system: piper
    piper:
      voice: en-us-libritts-high
      speed: 1.0
  
  wake_word:
    system: porcupine
    porcupine:
      model: hey_jarvis
      sensitivity: 0.5
```

## Troubleshooting

### Common Issues

#### Audio Problems
```bash
# Check audio devices
arecord -l
aplay -l

# Test microphone
arecord -f cd -d 5 test.wav
aplay test.wav

# Check container audio
docker exec -it rhasspy arecord -l
```

#### Network Issues
```bash
# Check container connectivity
docker exec -it rhasspy ping homeassistant
docker exec -it homeassistant ping rhasspy

# Check MQTT connection
docker exec -it rhasspy mosquitto_pub -h localhost -t test -m "hello"
```

#### Performance Issues
```bash
# Monitor container resources
docker stats

# Check container logs
docker logs rhasspy
docker logs wyoming-server
```

### Debug Commands
```bash
# Check container status
docker ps -a

# Check container logs
docker logs rhasspy
docker logs wyoming-server

# Check network connectivity
docker network ls
docker network inspect voice-assistant

# Check volume mounts
docker volume ls
```

## Security Considerations

### Network Security
```yaml
# docker-compose.yml
services:
  rhasspy:
    image: rhasspy/rhasspy:latest
    networks:
      - voice-assistant
    ports:
      - "127.0.0.1:12101:12101"  # Bind to localhost only
```

### Data Privacy
- **Local Processing:** All voice processing happens locally
- **No External Dependencies:** No data sent to external servers
- **Container Isolation:** Voice processing in isolated containers
- **Local Storage:** All data stored locally

## Cost Analysis

### Hardware Costs
- **Raspberry Pi 4 (8GB):** $75
- **USB Microphone Array:** $50
- **Speaker System:** $30
- **microSD Card (64GB):** $20
- **Total:** $175

### Software Costs
- **Docker:** Free
- **Rhasspy:** Free
- **Whisper:** Free
- **Piper:** Free
- **Total:** $0

### Ongoing Costs
- **No subscription fees**
- **No cloud service costs**
- **No external dependencies**
- **Total:** $0/month

## Implementation Timeline

### Phase 1: Setup (2-3 hours)
1. **Install Docker** and Docker Compose
2. **Configure audio hardware**
3. **Set up container services**
4. **Test basic functionality**

### Phase 2: Integration (1-2 hours)
1. **Configure Home Assistant integration**
2. **Set up MQTT communication**
3. **Configure voice commands**
4. **Test voice control**

### Phase 3: Optimization (1-2 hours)
1. **Tune performance settings**
2. **Optimize voice recognition**
3. **Configure custom commands**
4. **Test and refine**

## Benefits of Container Solution

### Advantages
- **Modular Design:** Mix and match components
- **Easy Updates:** Update individual components
- **Resource Isolation:** Isolated processing
- **Scalability:** Easy to scale components
- **Maintenance:** Easy to maintain and debug

### Disadvantages
- **Complexity:** More complex setup
- **Resource Usage:** Higher resource requirements
- **Network Dependencies:** Container communication required
- **Debugging:** More complex debugging

## Conclusion

Container-based local voice assistant solutions provide a flexible and scalable approach to creating a completely local voice control system for Home Assistant. The choice between Rhasspy and Wyoming protocol depends on your specific needs and technical expertise.

**Recommended Path:**
1. **Start with Rhasspy** for complete solution
2. **Consider Wyoming protocol** for modular approach
3. **Use Home Assistant add-ons** for integrated solution

All solutions provide complete local operation without any dependency on external service providers, ensuring maximum privacy and security for your smart home system.
