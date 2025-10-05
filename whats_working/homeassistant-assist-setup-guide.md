# Home Assistant Assist Local Voice Assistant Setup Guide

## Overview
Complete guide for setting up Home Assistant's built-in Assist voice assistant for completely local voice control without any external service dependencies.

## Prerequisites

### Hardware Requirements
- **Home Assistant OS** (not Docker) - Required for local voice processing
- **Raspberry Pi 4** (4GB RAM minimum, 8GB recommended)
- **USB Microphone** (array recommended for better recognition)
- **Speaker or Headphones** (for voice feedback)
- **32GB+ microSD card** (64GB recommended)
- **Power supply** (official Raspberry Pi 4 power supply recommended)

### Software Requirements
- **Home Assistant OS** (latest version)
- **Compatible audio hardware** (USB microphone and speaker)
- **Stable network connection** (for initial setup)

## Step 1: Hardware Setup

### 1.1 Install Home Assistant OS
```bash
# Download Home Assistant OS image
wget https://github.com/home-assistant/operating-system/releases/latest/download/haos_rpi4-64-11.0.img.xz

# Flash to microSD card
sudo dd if=haos_rpi4-64-11.0.img.xz of=/dev/sdX bs=4M status=progress
```

### 1.2 Connect Audio Hardware
1. **Connect USB microphone** to Raspberry Pi 4
2. **Connect speaker** to Raspberry Pi 4
3. **Power on** the Raspberry Pi 4
4. **Wait for Home Assistant** to boot (5-10 minutes)

### 1.3 Initial Home Assistant Setup
1. **Access Home Assistant** at `http://homeassistant.local:8123`
2. **Create admin account**
3. **Complete onboarding** process
4. **Configure location** and timezone

## Step 2: Audio Configuration

### 2.1 Test Audio Hardware
```bash
# SSH into Home Assistant
ssh root@homeassistant.local

# Check audio devices
arecord -l
aplay -l

# Test microphone
arecord -f cd -d 5 test.wav
aplay test.wav
```

### 2.2 Configure Audio Settings
1. **Go to Settings > System > Hardware**
2. **Check audio device recognition**
3. **Test microphone input**
4. **Test speaker output**

## Step 3: Install Voice Assistant Components

### 3.1 Install Speech-to-Text Engine
1. **Go to Settings > Add-ons**
2. **Install "Whisper" add-on** (for advanced users)
   - **Alternative:** Use "Speech-to-Phrase" (for beginners)
3. **Configure add-on settings**
4. **Start the add-on**

### 3.2 Install Text-to-Speech Engine
1. **Install "Piper" add-on**
2. **Configure language settings**
3. **Start the add-on**

### 3.3 Install Wake Word Detection
1. **Install "Porcupine" add-on** (for wake word detection)
2. **Configure wake word** (e.g., "Hey Home Assistant")
3. **Start the add-on**

## Step 4: Configure Assist

### 4.1 Create Voice Assistant
1. **Go to Settings > Voice Assistants**
2. **Click "Add Assistant"**
3. **Configure basic settings:**
   - **Name:** "Home Assistant"
   - **Language:** English (or your preferred language)
   - **Wake Word:** "Hey Home Assistant"

### 4.2 Configure Speech-to-Text
1. **Select Speech-to-Text engine:**
   - **Speech-to-Phrase:** Fast, limited commands
   - **Whisper:** Natural language, slower processing
2. **Configure language settings**
3. **Test speech recognition**

### 4.3 Configure Text-to-Speech
1. **Select Piper TTS engine**
2. **Configure voice settings**
3. **Test text-to-speech output**

### 4.4 Configure Wake Word
1. **Select Porcupine wake word detection**
2. **Configure wake word sensitivity**
3. **Test wake word detection**

## Step 5: Entity Exposure

### 5.1 Expose Entities to Assist
1. **Go to Settings > Voice Assistants**
2. **Select your assistant**
3. **Go to "Expose" tab**
4. **Select entities to expose:**
   - **Lights:** All light entities
   - **Switches:** All switch entities
   - **Climate:** All climate entities
   - **Scenes:** All scene entities
   - **Scripts:** All script entities

### 5.2 Configure Entity Names
```yaml
# customize.yaml
light.living_room:
  friendly_name: "Living Room Light"
  alexa_name: "Living Room Light"

switch.coffee_maker:
  friendly_name: "Coffee Maker"
  alexa_name: "Coffee Maker"

climate.bedroom:
  friendly_name: "Bedroom Temperature"
  alexa_name: "Bedroom Temperature"
```

## Step 6: Test Voice Commands

### 6.1 Basic Voice Commands
Test these commands to verify functionality:

- **"Hey Home Assistant, turn on the living room light"**
- **"Hey Home Assistant, turn off the coffee maker"**
- **"Hey Home Assistant, set the bedroom temperature to 22 degrees"**
- **"Hey Home Assistant, what's the status of the living room light?"**

### 6.2 Advanced Voice Commands
Test more complex commands:

- **"Hey Home Assistant, turn on all lights"**
- **"Hey Home Assistant, set the house to night mode"**
- **"Hey Home Assistant, start the morning routine"**
- **"Hey Home Assistant, what's the weather like?"**

### 6.3 Troubleshooting Voice Commands
If commands don't work:
1. **Check entity exposure** in Voice Assistants settings
2. **Verify entity names** are clear and simple
3. **Test microphone** input levels
4. **Check Home Assistant logs** for errors

## Step 7: Advanced Configuration

### 7.1 Custom Wake Words
```yaml
# configuration.yaml
assist_pipeline:
  - language: en
    name: "Home Assistant"
    wake_word: "hey_home_assistant"
    stt_engine: "whisper"
    tts_engine: "piper"
```

### 7.2 Custom Voice Commands
```yaml
# automations.yaml
- alias: "Voice Command - Good Morning"
  trigger:
    platform: assist
    event: "Good Morning"
  action:
    - service: scene.turn_on
      entity_id: scene.good_morning
    - service: tts.piper_say
      data:
        message: "Good morning! Starting your day."

- alias: "Voice Command - Good Night"
  trigger:
    platform: assist
    event: "Good Night"
  action:
    - service: scene.turn_on
      entity_id: scene.good_night
    - service: tts.piper_say
      data:
        message: "Good night! Sleep well."
```

### 7.3 Scene Configuration
```yaml
# scenes.yaml
- name: "Good Morning"
  entities:
    light.living_room: "on"
    light.bedroom: "on"
    switch.coffee_maker: "on"
    climate.bedroom:
      temperature: 22
      hvac_mode: "heat"

- name: "Good Night"
  entities:
    light.living_room: "off"
    light.bedroom: "off"
    switch.coffee_maker: "off"
    climate.bedroom:
      temperature: 18
      hvac_mode: "cool"
```

## Step 8: Performance Optimization

### 8.1 Hardware Optimization
- **Use high-quality USB microphone** for better recognition
- **Position microphone** away from speakers to avoid feedback
- **Use dedicated audio interface** for professional setup
- **Ensure adequate power supply** for stable operation

### 8.2 Software Optimization
- **Choose appropriate speech-to-text engine:**
  - **Speech-to-Phrase:** Faster, limited commands
  - **Whisper:** Slower, natural language
- **Optimize wake word sensitivity**
- **Configure appropriate language models**
- **Monitor system resources**

### 8.3 Network Optimization
- **Use wired Ethernet** for stable connection
- **Optimize WiFi settings** if using wireless
- **Monitor network latency**
- **Use dedicated network** for voice processing

## Step 9: Troubleshooting

### 9.1 Common Issues

#### Audio Hardware Problems
```bash
# Check audio devices
arecord -l
aplay -l

# Test microphone
arecord -f cd -d 5 test.wav
aplay test.wav

# Check audio levels
alsamixer
```

#### Voice Recognition Issues
1. **Check microphone positioning**
2. **Verify audio input levels**
3. **Test in quiet environment**
4. **Check language settings**
5. **Verify entity exposure**

#### Performance Issues
1. **Check system resources**
2. **Monitor CPU usage**
3. **Verify memory availability**
4. **Check storage space**
5. **Optimize speech-to-text engine**

### 9.2 Debug Commands
```bash
# Check Home Assistant logs
docker logs homeassistant

# Check audio system
systemctl status alsa-state

# Check add-on logs
docker logs addon_whisper
docker logs addon_piper
docker logs addon_porcupine
```

### 9.3 Performance Monitoring
```bash
# Monitor system resources
htop

# Check audio processes
ps aux | grep audio

# Monitor network usage
iftop
```

## Step 10: Security Configuration

### 10.1 Network Security
- **Use local network only** for voice processing
- **Configure firewall rules** if needed
- **Monitor network traffic**
- **Use VPN** for remote access only

### 10.2 Data Privacy
- **All voice processing** happens locally
- **No data transmission** to external servers
- **Local storage** of voice data only
- **No tracking** or analytics

### 10.3 Access Control
- **Secure Home Assistant** with strong passwords
- **Enable two-factor authentication**
- **Regular security updates**
- **Monitor access logs**

## Benefits of Local Voice Assistant

### Privacy Advantages
- **Complete Privacy:** No voice data leaves your network
- **Local Processing:** All voice recognition happens locally
- **No Tracking:** No external tracking or analytics
- **Data Control:** Complete control over voice data

### Security Benefits
- **Network Isolation:** Voice processing on local network only
- **No External Dependencies:** No reliance on external services
- **Custom Security:** Full control over security measures
- **Audit Trail:** Complete control over data logging

### Performance Benefits
- **Fast Response:** No network latency for voice processing
- **Reliable Operation:** No dependency on internet connection
- **Customizable:** Full control over voice commands and responses
- **Scalable:** Can be expanded with additional hardware

## Cost Analysis

### Hardware Costs
- **Raspberry Pi 4 (8GB):** $75
- **USB Microphone Array:** $50
- **Speaker System:** $30
- **microSD Card (64GB):** $20
- **Power Supply:** $15
- **Total:** $190

### Software Costs
- **Home Assistant OS:** Free
- **Voice Assistant Components:** Free
- **Total:** $0

### Ongoing Costs
- **No subscription fees**
- **No cloud service costs**
- **No external dependencies**
- **Total:** $0

## Conclusion

Setting up Home Assistant Assist provides a completely local voice assistant solution that eliminates all external service dependencies. The setup requires some technical expertise but provides significant benefits in terms of privacy, security, and independence.

**Key Benefits:**
- Complete local operation
- No external service dependencies
- Maximum privacy and security
- Customizable voice commands
- No ongoing costs

**Recommended for:**
- Privacy-conscious users
- Users wanting complete control
- Users with technical expertise
- Users wanting to eliminate external dependencies

The setup process takes 2-4 hours depending on technical expertise, but results in a fully functional local voice assistant that operates independently of any external service providers.
