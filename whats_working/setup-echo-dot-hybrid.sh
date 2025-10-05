#!/bin/bash

# Echo Dot 5th Gen Hybrid Setup Script
# Home Assistant as Brain, Echo Dot as Dumb Speaker

set -e

echo "🎯 Setting up Echo Dot 5th Gen as dumb speaker with Home Assistant as brain..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS. Please adapt for your system."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker Desktop first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "✅ Docker and Docker Compose are available"

# Create directory structure
print_status "📁 Creating directory structure..."
mkdir -p voice-assistant/{mqtt,whisper,piper,openwakeword,wyoming,rhasspy}
mkdir -p voice-assistant/mqtt/{config,data}
mkdir -p voice-assistant/whisper/models
mkdir -p voice-assistant/piper/voices
mkdir -p voice-assistant/openwakeword/models
mkdir -p voice-assistant/wyoming/config
mkdir -p voice-assistant/rhasspy/{profiles,data,logs}

# Create MQTT configuration
print_status "🔧 Creating MQTT configuration..."
cat > voice-assistant/mqtt/config/mosquitto.conf << 'EOF'
# MQTT Configuration for Voice Assistant
listener 1883
allow_anonymous true

# WebSocket support
listener 9001
protocol websockets

# Logging
log_dest file /mosquitto/log/mosquitto.log
log_type error
log_type warning
log_type notice
log_type information

# Persistence
persistence true
persistence_location /mosquitto/data/
EOF

# Create Wyoming configuration
print_status "🔧 Creating Wyoming configuration..."
cat > voice-assistant/wyoming/config/wyoming.yaml << 'EOF'
# Wyoming Protocol Configuration
server:
  host: 0.0.0.0
  port: 10400

# Wake word detection
wake_word:
  engine: openwakeword
  uri: tcp://openwakeword:10100

# Speech-to-Text
stt:
  engine: whisper
  uri: tcp://whisper:10300

# Text-to-Speech
tts:
  engine: piper
  uri: tcp://piper:10200

# Audio settings
audio:
  input_device: "default"
  output_device: "default"
  sample_rate: 16000
  channels: 1
EOF

# Create Rhasspy profile
print_status "🔧 Creating Rhasspy profile..."
mkdir -p voice-assistant/rhasspy/profiles/english
cat > voice-assistant/rhasspy/profiles/english/profile.json << 'EOF'
{
  "language": "en",
  "speech_to_text": {
    "system": "whisper",
    "whisper": {
      "model": "small",
      "language": "en"
    }
  },
  "text_to_speech": {
    "system": "piper",
    "piper": {
      "voice": "en-us-libritts-high"
    }
  },
  "wake_word": {
    "system": "openwakeword",
    "openwakeword": {
      "model": "hey_jarvis"
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

# Create Home Assistant configuration
print_status "🔧 Creating Home Assistant voice assistant configuration..."
cat > voice-assistant/homeassistant-voice-config.yaml << 'EOF'
# Home Assistant Voice Assistant Configuration
# Add this to your Home Assistant configuration.yaml

# Assist Pipeline Configuration
assist_pipeline:
  - language: en
    name: "Local Voice Assistant"
    wake_word: "hey_home_assistant"
    stt_engine: "whisper"
    tts_engine: "piper"
    wake_word_engine: "openwakeword"

# Text-to-Speech Configuration
tts:
  - platform: piper
    url: "http://localhost:10201"
    voice: "en-us-libritts-high"

# Media Player for Echo Dot (Bluetooth)
media_player:
  - platform: bluetooth
    device: "Echo Dot-XXX"  # Replace with your Echo Dot's Bluetooth name
    name: "Echo Dot Speaker"

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

  GetStatus:
    action:
      - service: system_log.write
        data:
          message: "Status requested"
    speech:
      text: "All systems are operational"

# Automation for Voice Commands
automation:
  - alias: "Voice Assistant Wake Word"
    trigger:
      - platform: event
        event_type: assist_pipeline.wake_word_detected
    action:
      - service: system_log.write
        data:
          message: "Wake word detected"

  - alias: "Voice Assistant Intent"
    trigger:
      - platform: event
        event_type: assist_pipeline.intent_started
    action:
      - service: system_log.write
        data:
          message: "Intent processing started"
EOF

# Create setup instructions
print_status "📝 Creating setup instructions..."
cat > voice-assistant/SETUP_INSTRUCTIONS.md << 'EOF'
# Echo Dot 5th Gen Hybrid Setup Instructions

## Overview
This setup makes Home Assistant the brain and Echo Dot 5th gen a "dumb" speaker device.

## Hardware Setup

### 1. Echo Dot Configuration
1. **Put Echo Dot in pairing mode:**
   - Say: "Alexa, pair" or "Alexa, Bluetooth pairing"
   - LED should start blinking blue

2. **Pair with Mac Mini M4:**
   - Open System Preferences > Bluetooth
   - Find "Echo Dot-XXX" in available devices
   - Click "Connect"
   - Confirm pairing

3. **Test audio output:**
   - Play a test sound to verify Echo Dot receives audio
   - Check System Preferences > Sound > Output
   - Select Echo Dot as output device

### 2. Microphone Setup
1. **Connect USB microphone** to Mac Mini M4
2. **Test microphone:**
   - Open System Preferences > Sound > Input
   - Select your USB microphone
   - Test recording to verify it works

## Software Setup

### 1. Start Voice Assistant Services
```bash
cd voice-assistant
docker-compose up -d
```

### 2. Configure Home Assistant
1. **Add voice assistant configuration** to your Home Assistant
2. **Copy the configuration** from homeassistant-voice-config.yaml
3. **Restart Home Assistant** to apply changes

### 3. Test Voice Assistant
1. **Say wake word:** "Hey Home Assistant"
2. **Give voice command:** "Turn on the living room light"
3. **Verify response** through Echo Dot speaker

## Troubleshooting

### Audio Issues
- Check Bluetooth connection: System Preferences > Bluetooth
- Test audio output: Play test sound
- Verify microphone: System Preferences > Sound > Input

### Voice Recognition Issues
- Check container logs: `docker logs whisper-stt`
- Test microphone: Record test audio
- Verify wake word detection: Check Home Assistant logs

### Bluetooth Issues
- Reconnect Echo Dot: System Preferences > Bluetooth
- Check device status: Bluetooth menu
- Restart Bluetooth: System Preferences > Bluetooth > Advanced

## Customization

### Wake Words
- Change wake word in Home Assistant configuration
- Train custom wake words in Home Assistant Assist settings
- Test wake word detection sensitivity

### Voice Commands
- Add new intent scripts in Home Assistant
- Create custom automations for voice commands
- Test voice command recognition

### Audio Quality
- Adjust audio settings in System Preferences
- Optimize Bluetooth audio quality
- Configure audio routing for best performance

## Benefits

### Complete Control
- Home Assistant processes all voice commands
- No cloud dependencies for voice processing
- Custom wake words and commands
- Complete privacy and local control

### Echo Dot Optimization
- Use Echo Dot hardware for audio output
- Eliminate AWS dependencies
- Local audio routing through Home Assistant
- Custom audio processing and responses

### Cost Benefits
- No subscription fees for voice processing
- Reuse existing Echo Dot hardware
- Local processing eliminates cloud costs
- Complete privacy and security
EOF

# Create Docker Compose file
print_status "🐳 Creating Docker Compose configuration..."
cp echo-dot-hybrid-setup.yml voice-assistant/docker-compose.yml

# Set permissions
print_status "🔐 Setting permissions..."
chmod +x voice-assistant/setup-echo-dot-hybrid.sh
chmod 755 voice-assistant/mqtt/config/mosquitto.conf
chmod 755 voice-assistant/wyoming/config/wyoming.yaml
chmod 755 voice-assistant/rhasspy/profiles/english/profile.json

# Create startup script
print_status "🚀 Creating startup script..."
cat > voice-assistant/start-voice-assistant.sh << 'EOF'
#!/bin/bash

echo "🎯 Starting Echo Dot Hybrid Voice Assistant..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Start voice assistant services
echo "🐳 Starting voice assistant containers..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "📊 Checking service status..."
docker-compose ps

# Show logs
echo "📝 Showing recent logs..."
docker-compose logs --tail=20

echo "✅ Voice assistant services started!"
echo "🔧 Next steps:"
echo "1. Configure Home Assistant with voice assistant settings"
echo "2. Pair Echo Dot as Bluetooth speaker"
echo "3. Test voice commands"
echo "4. Check SETUP_INSTRUCTIONS.md for detailed setup"
EOF

chmod +x voice-assistant/start-voice-assistant.sh

# Create stop script
print_status "🛑 Creating stop script..."
cat > voice-assistant/stop-voice-assistant.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping Echo Dot Hybrid Voice Assistant..."

# Stop voice assistant services
docker-compose down

echo "✅ Voice assistant services stopped!"
EOF

chmod +x voice-assistant/stop-voice-assistant.sh

# Create test script
print_status "🧪 Creating test script..."
cat > voice-assistant/test-voice-assistant.sh << 'EOF'
#!/bin/bash

echo "🧪 Testing Echo Dot Hybrid Voice Assistant..."

# Test MQTT connection
echo "📡 Testing MQTT connection..."
if docker exec voice-mqtt mosquitto_pub -h localhost -t "test/topic" -m "test message"; then
    echo "✅ MQTT connection successful"
else
    echo "❌ MQTT connection failed"
fi

# Test Whisper STT
echo "🎤 Testing Whisper STT..."
if curl -s http://localhost:10301/health > /dev/null; then
    echo "✅ Whisper STT service running"
else
    echo "❌ Whisper STT service not responding"
fi

# Test Piper TTS
echo "🔊 Testing Piper TTS..."
if curl -s http://localhost:10201/health > /dev/null; then
    echo "✅ Piper TTS service running"
else
    echo "❌ Piper TTS service not responding"
fi

# Test OpenWakeWord
echo "👂 Testing OpenWakeWord..."
if curl -s http://localhost:10101/health > /dev/null; then
    echo "✅ OpenWakeWord service running"
else
    echo "❌ OpenWakeWord service not responding"
fi

# Test Wyoming Server
echo "🌐 Testing Wyoming Server..."
if curl -s http://localhost:10400/health > /dev/null; then
    echo "✅ Wyoming Server running"
else
    echo "❌ Wyoming Server not responding"
fi

echo "🧪 Voice assistant testing complete!"
EOF

chmod +x voice-assistant/test-voice-assistant.sh

print_success "✅ Echo Dot hybrid setup complete!"
print_status "📁 Files created in: voice-assistant/"
print_status "📖 Read SETUP_INSTRUCTIONS.md for detailed setup"
print_status "🚀 Run: cd voice-assistant && ./start-voice-assistant.sh"
print_status "🧪 Test: cd voice-assistant && ./test-voice-assistant.sh"

echo ""
print_status "🎯 Next steps:"
echo "1. Configure Echo Dot as Bluetooth speaker"
echo "2. Set up USB microphone for voice input"
echo "3. Configure Home Assistant with voice assistant settings"
echo "4. Test voice commands and responses"
echo "5. Customize wake words and voice commands"

print_success "🎉 Echo Dot optimization setup complete!"
