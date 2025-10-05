# Echo Dot 5th Gen Optimization Guide

## Overview
Complete guide for optimizing your Echo Dot 5th generation as a "dumb" microphone and speaker device, with Home Assistant being the core brain that processes everything locally.

## Understanding the Goal

### What You Want to Achieve
- **Echo Dot as Hardware Only:** Use only the microphone and speaker hardware
- **Home Assistant as Brain:** All voice processing happens in Home Assistant
- **No AWS Dependencies:** Eliminate all cloud connections
- **Local Processing:** Complete privacy and local control
- **Custom Wake Words:** Set your own wake words
- **Custom Commands:** Train your own voice commands

### Limitations of Echo Dot 5th Gen
- **No Local Processing:** Cannot process voice commands locally
- **Cloud Dependency:** Requires internet for all functionality
- **No Direct Home Assistant Integration:** No native local integration
- **Hardware Limitations:** Cannot be easily modified for local use

## Solution Options

### Option 1: Bluetooth Audio Output (RECOMMENDED)

#### Overview
Use Echo Dot as a Bluetooth speaker for Home Assistant's local voice assistant, while using a separate microphone for input.

#### Setup Process
1. **Pair Echo Dot as Bluetooth Speaker**
2. **Set up Home Assistant local voice assistant**
3. **Configure audio routing to Echo Dot**
4. **Use separate microphone for voice input**

#### Implementation
```bash
# Enable Bluetooth pairing on Echo Dot
# Say: "Alexa, pair" or "Alexa, Bluetooth pairing"

# Pair from Mac Mini M4
bluetoothctl
scan on
pair [MAC_ADDRESS]
trust [MAC_ADDRESS]
connect [MAC_ADDRESS]
```

#### Home Assistant Configuration
```yaml
# configuration.yaml
assist_pipeline:
  - language: en
    name: "Local Voice Assistant"
    wake_word: "hey_home_assistant"
    stt_engine: "whisper"
    tts_engine: "piper"
    wake_word_engine: "openwakeword"

# Media player for Echo Dot
media_player:
  - platform: bluetooth
    device: "Echo Dot-XXX"
```

### Option 2: Hardware Modification (ADVANCED)

#### Overview
Modify Echo Dot hardware to bypass Amazon's firmware and use it as a local device.

#### Warning
- **Voids Warranty:** Hardware modification voids warranty
- **Risk of Damage:** May render device inoperable
- **Technical Complexity:** Requires advanced technical skills
- **No Official Support:** No official documentation

#### Process
1. **Root the Echo Dot**
2. **Install custom firmware**
3. **Configure local voice processing**
4. **Integrate with Home Assistant**

### Option 3: Hybrid Approach (PRACTICAL)

#### Overview
Use Echo Dot for basic audio output while implementing a complete local voice assistant system.

#### Setup
1. **Keep Echo Dot for audio output only**
2. **Implement Home Assistant local voice assistant**
3. **Use separate microphone for voice input**
4. **Route all processing through Home Assistant**

## Recommended Implementation: Option 1

### Hardware Setup

#### Required Hardware
- **Echo Dot 5th Gen:** For audio output only
- **USB Microphone:** For voice input (separate from Echo Dot)
- **Mac Mini M4:** For Home Assistant and voice processing
- **Speaker (Optional):** Backup audio output

#### Audio Configuration
```bash
# Check available audio devices
system_profiler SPAudioDataType

# Test microphone
ffmpeg -f avfoundation -i ":0" -t 5 test.wav

# Test Echo Dot audio output
aplay test.wav
```

### Home Assistant Setup

#### Local Voice Assistant Configuration
```yaml
# configuration.yaml
assist_pipeline:
  - language: en
    name: "Local Voice Assistant"
    wake_word: "hey_home_assistant"
    stt_engine: "whisper"
    tts_engine: "piper"
    wake_word_engine: "openwakeword"

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

  SetTemperature:
    action:
      - service: climate.set_temperature
        entity_id: climate.bedroom
        data:
          temperature: "{{ temperature }}"
    speech:
      text: "Setting bedroom temperature to {{ temperature }} degrees"
```

#### Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
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
          memory: 4G
          cpus: '4.0'

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
          memory: 2G
          cpus: '2.0'

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
```

### Audio Routing Configuration

#### Bluetooth Audio Setup
```bash
# Install Bluetooth audio tools
brew install bluealsa

# Configure Bluetooth audio
sudo bluealsa -p a2dp-sink &

# Set Echo Dot as default audio output
sudo pacmd set-default-sink bluealsa
```

#### Home Assistant Audio Configuration
```yaml
# configuration.yaml
tts:
  - platform: piper
    url: "http://localhost:10201"
    voice: "en-us-libritts-high"

# Media player for Echo Dot
media_player:
  - platform: bluetooth
    device: "Echo Dot-XXX"
    name: "Echo Dot Speaker"
```

### Voice Command Examples

#### Basic Commands
- **"Hey Home Assistant, turn on the living room light"**
- **"Hey Home Assistant, turn off the coffee maker"**
- **"Hey Home Assistant, set the bedroom temperature to 22 degrees"**
- **"Hey Home Assistant, what's the status of the living room light?"**

#### Advanced Commands
- **"Hey Home Assistant, turn on all lights"**
- **"Hey Home Assistant, set the house to night mode"**
- **"Hey Home Assistant, start the morning routine"**
- **"Hey Home Assistant, what's the weather like?"**

### Custom Wake Word Setup

#### Using "Hey Alexa" Wake Word
```yaml
# configuration.yaml
assist_pipeline:
  - language: en
    name: "Local Voice Assistant"
    wake_word: "hey_alexa"  # Custom wake word
    stt_engine: "whisper"
    tts_engine: "piper"
    wake_word_engine: "openwakeword"
```

#### Custom Wake Word Training
1. **Access Home Assistant Assist settings**
2. **Configure wake word detection**
3. **Set custom wake word** (e.g., "Hey Alexa")
4. **Test wake word detection**
5. **Adjust sensitivity** as needed

## Setup Process

### 1. Hardware Setup (30 minutes)
1. **Connect USB microphone** to Mac Mini M4
2. **Pair Echo Dot** as Bluetooth speaker
3. **Test audio input/output** devices
4. **Configure audio routing**

### 2. Home Assistant Setup (1-2 hours)
1. **Install voice assistant components** (Whisper, Piper, OpenWakeWord)
2. **Configure assist pipeline** in Home Assistant
3. **Set up intent scripts** for voice commands
4. **Test voice recognition** and response

### 3. Audio Integration (30 minutes)
1. **Configure Bluetooth audio** routing
2. **Set Echo Dot as default** audio output
3. **Test audio playback** through Echo Dot
4. **Optimize audio quality** and latency

### 4. Testing and Optimization (30 minutes)
1. **Test voice commands** and responses
2. **Optimize wake word** detection
3. **Fine-tune audio** settings
4. **Configure custom** voice commands

## Troubleshooting

### Common Issues

#### Audio Problems
```bash
# Check audio devices
system_profiler SPAudioDataType

# Test microphone
ffmpeg -f avfoundation -i ":0" -t 5 test.wav

# Test Echo Dot audio
aplay test.wav
```

#### Bluetooth Issues
```bash
# Check Bluetooth connection
bluetoothctl
info [MAC_ADDRESS]

# Reconnect if needed
bluetoothctl
connect [MAC_ADDRESS]
```

#### Voice Recognition Issues
```bash
# Check container logs
docker logs whisper-stt
docker logs piper-tts
docker logs openwakeword

# Test voice recognition
docker exec -it whisper-stt whisper --model small --language en test.wav
```

### Debug Commands
```bash
# Check container status
docker ps -a

# Monitor resources
docker stats

# Check audio system
system_profiler SPAudioDataType
```

## Benefits of This Approach

### Complete Control
- **Home Assistant as Brain:** All processing happens in Home Assistant
- **Local Processing:** No cloud dependencies
- **Custom Commands:** Train your own voice commands
- **Privacy-Focused:** No data leaves your network

### Echo Dot Optimization
- **Hardware Utilization:** Use Echo Dot's speaker hardware
- **No AWS Dependencies:** Eliminate all cloud connections
- **Custom Audio:** Route audio through Home Assistant
- **Local Control:** Complete local control over audio

### Cost Benefits
- **No Subscription Fees:** No ongoing costs
- **Hardware Reuse:** Utilize existing Echo Dot hardware
- **Local Processing:** No cloud service costs
- **Complete Privacy:** No external dependencies

## Conclusion

While the Echo Dot 5th gen cannot be completely "de-smarted" due to its hardware design, you can optimize it as a "dumb" audio device by:

1. **Using it as Bluetooth speaker** for Home Assistant audio output
2. **Implementing local voice assistant** in Home Assistant
3. **Using separate microphone** for voice input
4. **Routing all processing** through Home Assistant

This approach gives you:
- **Complete local control** over voice processing
- **Custom wake words** and commands
- **No cloud dependencies**
- **Maximum privacy** and security
- **Home Assistant as the core brain**

The Echo Dot becomes a "dumb" speaker that only does what Home Assistant tells it to do, with all the intelligence and processing happening locally in your Home Assistant setup.
