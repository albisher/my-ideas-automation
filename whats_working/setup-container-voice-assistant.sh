#!/bin/bash

# Container-Based Local Voice Assistant Setup Script
# Compatible with your existing Home Assistant Docker setup

set -e

echo "Setting up Container-Based Local Voice Assistant..."

# Create directory structure
echo "Creating directory structure..."
mkdir -p voice-assistant/{mqtt,rhasspy,whisper,piper,openwakeword,wyoming}/{config,data,logs,models,voices,profiles}

# Create MQTT configuration
echo "Creating MQTT configuration..."
cat > voice-assistant/mqtt/config/mosquitto.conf << EOF
# MQTT Configuration for Voice Assistant
listener 1883
allow_anonymous true

listener 9001
protocol websockets
allow_anonymous true

# Logging
log_dest file /mosquitto/log/mosquitto.log
log_type error
log_type warning
log_type notice
log_type information
EOF

# Create Rhasspy configuration
echo "Creating Rhasspy configuration..."
cat > voice-assistant/rhasspy/profiles/english/profile.json << EOF
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
EOF

# Create Wyoming configuration
echo "Creating Wyoming configuration..."
cat > voice-assistant/wyoming/config/wyoming.yaml << EOF
# Wyoming Server Configuration
server:
  host: "0.0.0.0"
  port: 10400

# Speech-to-Text
stt:
  - name: "whisper"
    url: "http://whisper:10300"
    language: "en"

# Text-to-Speech
tts:
  - name: "piper"
    url: "http://piper:10200"
    language: "en"

# Wake Word
wake_word:
  - name: "openwakeword"
    url: "http://openwakeword:10100"
    model: "hey_jarvis"
EOF

# Create Home Assistant configuration additions
echo "Creating Home Assistant configuration additions..."
cat > voice-assistant/homeassistant-config-additions.yaml << EOF
# Add these to your Home Assistant configuration.yaml

# MQTT Configuration for Voice Assistant
mqtt:
  broker: localhost
  port: 1883
  username: rhasspy
  password: your_secure_password

# Intent Scripts for Voice Commands
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

  StartScene:
    action:
      - service: scene.turn_on
        entity_id: "{{ scene }}"
    speech:
      text: "Starting {{ scene }}"

# Assist Pipeline Configuration
assist_pipeline:
  - language: en
    name: "Local Voice Assistant"
    wake_word: "hey_home_assistant"
    stt_engine: "wyoming"
    tts_engine: "wyoming"
    wake_word_engine: "wyoming"

# Wyoming Protocol Integration
wyoming:
  stt:
    - url: "http://localhost:10301"
  tts:
    - url: "http://localhost:10201"
  wake_word:
    - url: "http://localhost:10101"
EOF

# Create setup instructions
echo "Creating setup instructions..."
cat > voice-assistant/SETUP_INSTRUCTIONS.md << EOF
# Container-Based Local Voice Assistant Setup

## Prerequisites
- Docker and Docker Compose installed
- USB microphone and speaker connected
- Home Assistant running in Docker

## Setup Steps

### 1. Audio Hardware Setup
\`\`\`bash
# Check audio devices
arecord -l
aplay -l

# Test microphone
arecord -f cd -d 5 test.wav
aplay test.wav
\`\`\`

### 2. Start Voice Assistant Services
\`\`\`bash
cd voice-assistant
docker-compose up -d
\`\`\`

### 3. Configure Home Assistant
1. Add the configuration from \`homeassistant-config-additions.yaml\` to your \`configuration.yaml\`
2. Restart Home Assistant
3. Go to Settings > Voice Assistants
4. Configure the local voice assistant

### 4. Configure Rhasspy
1. Access Rhasspy web interface at \`http://localhost:12101\`
2. Configure microphone and speaker
3. Set up wake word detection
4. Train custom sentences

### 5. Test Voice Commands
- "Hey Home Assistant, turn on the living room light"
- "Hey Home Assistant, set the bedroom temperature to 22 degrees"
- "Hey Home Assistant, start the morning routine"

## Troubleshooting

### Audio Issues
\`\`\`bash
# Check container audio
docker exec -it rhasspy-voice-assistant arecord -l
docker exec -it rhasspy-voice-assistant aplay -l
\`\`\`

### Network Issues
\`\`\`bash
# Check container connectivity
docker exec -it rhasspy-voice-assistant ping homeassistant
\`\`\`

### Performance Issues
\`\`\`bash
# Monitor container resources
docker stats
\`\`\`

## Configuration Files
- \`docker-compose.yml\` - Main Docker Compose configuration
- \`mqtt/config/mosquitto.conf\` - MQTT broker configuration
- \`rhasspy/profiles/english/profile.json\` - Rhasspy configuration
- \`wyoming/config/wyoming.yaml\` - Wyoming server configuration
- \`homeassistant-config-additions.yaml\` - Home Assistant configuration additions
EOF

# Set permissions
echo "Setting permissions..."
chmod +x voice-assistant/setup-container-voice-assistant.sh

# Create .env file for sensitive data
echo "Creating environment file..."
cat > voice-assistant/.env << EOF
# Voice Assistant Environment Variables
MQTT_USERNAME=rhasspy
MQTT_PASSWORD=your_secure_password
RHASSPY_LANGUAGE=en
RHASSPY_PROFILE=english
EOF

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Review the configuration files in the voice-assistant directory"
echo "2. Update the .env file with your secure password"
echo "3. Connect your USB microphone and speaker"
echo "4. Run: cd voice-assistant && docker-compose up -d"
echo "5. Follow the setup instructions in SETUP_INSTRUCTIONS.md"
echo ""
echo "Configuration files created:"
echo "- docker-compose-voice-assistant.yml"
echo "- MQTT configuration"
echo "- Rhasspy configuration"
echo "- Wyoming configuration"
echo "- Home Assistant configuration additions"
echo "- Setup instructions"
