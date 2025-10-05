# Home Assistant Assist Setup

This guide covers setting up and optimizing Home Assistant Assist (voice assistant) based on the latest [official documentation](https://www.home-assistant.io/docs/voice_control/assist/).

## Assist Overview

Home Assistant Assist is the built-in voice assistant that provides local, private voice control for your smart home. It's designed to work entirely offline, ensuring your conversations stay private.

## Current Configuration

### Your Assist Setup
Based on your current configuration:

```json
{
  "conversation_engine": "conversation.home_assistant",
  "conversation_language": "en",
  "language": "en",
  "name": "Home Assistant",
  "stt_engine": null,
  "stt_language": null,
  "tts_engine": "google_translate",
  "tts_language": "en-us",
  "tts_voice": null,
  "wake_word_entity": null,
  "wake_word_id": null,
  "prefer_local_intents": false
}
```

### Configured Components
- **TTS Engine**: Google Translate
- **TTS Language**: English (en-us)
- **Conversation Engine**: Home Assistant
- **Language**: English

## Getting Started with Assist

### Basic Setup

1. **Access Assist Settings**
   - Go to **Configuration** → **Voice Assistants**
   - Click **Add Voice Assistant**

2. **Configure Basic Settings**
   ```yaml
   name: "Home Assistant"
   language: "en"
   conversation_engine: "conversation.home_assistant"
   ```

3. **Configure TTS (Text-to-Speech)**
   ```yaml
   tts_engine: "google_translate"
   tts_language: "en-us"
   ```

### Advanced Configuration

#### Speech-to-Text (STT) Setup
```yaml
# For local STT
stt_engine: "whisper"
stt_language: "en"

# For cloud STT
stt_engine: "google_cloud"
stt_language: "en-US"
```

#### Wake Word Configuration
```yaml
# For local wake word detection
wake_word_entity: "wake_word.your_wake_word"
wake_word_id: "your_wake_word_id"

# For cloud wake word
wake_word_entity: "wake_word.cloud_wake_word"
```

## Entity Exposure Best Practices

### Exposing Entities to Assist

Based on the [official best practices](https://www.home-assistant.io/voice_control/best_practices/), only expose entities that users will actually control via voice:

#### Your Current Exposed Entities
```yaml
# Motion sensors are exposed for voice control
binary_sensor.dcs_8000lh_motion:
  assistants:
    conversation:
      should_expose: true

binary_sensor.dcs_8000lh_motion_1:
  assistants:
    conversation:
      should_expose: true

binary_sensor.dcs_8000lh_motion_2:
  assistants:
    conversation:
      should_expose: true
```

#### Recommended Entity Exposure
```yaml
# Expose only essential entities
homeassistant:
  exposed_entities:
    # Lights
    light.living_room:
      assistants:
        conversation:
          should_expose: true
    
    # Switches
    switch.tapo_plug:
      assistants:
        conversation:
          should_expose: true
    
    # Sensors (for status queries)
    sensor.temperature:
      assistants:
        conversation:
          should_expose: true
```

### Naming Conventions

#### Entity Names
Use clear, descriptive names:
```yaml
# Good examples
light.living_room_light
switch.kitchen_plug
sensor.bedroom_temperature

# Avoid unclear names
light.light1
switch.switch1
sensor.sensor1
```

#### Aliases
Create aliases for different ways users might refer to devices:
```yaml
# Example with aliases
light.living_room_light:
  friendly_name: "Living Room Light"
  aliases:
    - "living room lamp"
    - "main light"
    - "room light"
```

## Voice Commands

### Basic Commands

#### Light Control
- "Turn on the living room light"
- "Turn off the kitchen light"
- "Set the bedroom light to 50%"
- "Change the living room light to blue"

#### Switch Control
- "Turn on the smart plug"
- "Turn off the kitchen switch"
- "Toggle the living room switch"

#### Status Queries
- "Is the motion sensor active?"
- "What's the temperature?"
- "How many people are detected?"

### Advanced Commands

#### Conditional Commands
- "Turn on the lights if motion is detected"
- "Set the temperature to 22 degrees if someone is home"

#### Scene Commands
- "Activate movie mode"
- "Set bedtime scene"
- "Turn on all lights"

## Custom Sentences

### Creating Custom Sentences

Based on the [custom sentences documentation](https://www.home-assistant.io/docs/voice_control/custom_sentences/):

```yaml
# Example custom sentences
intents:
  - sentences:
      - "Turn on the {name} light"
      - "Switch on the {name} light"
      - "Activate the {name} light"
    action:
      service: light.turn_on
      target:
        entity_id: "light.{name}"
```

### Language-Specific Considerations

#### English (en)
```yaml
# English-specific sentences
intents:
  - sentences:
      - "Turn on the {name}"
      - "Switch on the {name}"
      - "Activate the {name}"
```

#### Arabic (ar) - For Kuwait
```yaml
# Arabic sentences for Kuwait
intents:
  - sentences:
      - "شغل ال{name}"
      - "افتح ال{name}"
      - "تشغيل ال{name}"
```

## Troubleshooting Assist

### Common Issues

#### Assist Not Responding
1. **Check Microphone Access**
   - Ensure browser has microphone permissions
   - Test microphone in other applications

2. **Check TTS Configuration**
   - Verify TTS engine is working
   - Test TTS with a simple command

3. **Check Entity Exposure**
   - Verify entities are exposed to conversation
   - Check entity states

#### Commands Not Working
1. **Check Entity Names**
   - Use exact entity names in commands
   - Verify entity is available

2. **Check Service Calls**
   - Test service calls manually
   - Verify service parameters

3. **Check Logs**
   - Review conversation logs
   - Look for error messages

### Debug Tools

#### Developer Tools
1. **Services Tab**
   - Test `conversation.process` service
   - Test TTS services

2. **States Tab**
   - Check entity states
   - Verify entity availability

3. **Events Tab**
   - Monitor conversation events
   - Check for errors

#### Log Analysis
```yaml
# Enable conversation logging
logger:
  default: info
  logs:
    homeassistant.components.conversation: debug
    homeassistant.components.tts: debug
```

## Performance Optimization

### Reducing Processing Time

1. **Limit Exposed Entities**
   - Only expose necessary entities
   - Remove unused entities from exposure

2. **Optimize Entity Names**
   - Use short, clear names
   - Avoid complex naming patterns

3. **Use Local Processing**
   - Enable local intents when possible
   - Use local TTS engines

### Memory Optimization

```yaml
# Configuration for better performance
conversation:
  intents:
    HomeAssistant:
      sentences:
        - "Turn on the {name}"
        - "Turn off the {name}"
```

## Integration with Your Setup

### DCS-8000LH Camera Integration

```yaml
# Voice commands for camera system
intents:
  - sentences:
      - "Is there motion detected?"
      - "How many people are in the camera?"
      - "Show me the camera"
    action:
      service: camera.turn_on
      target:
        entity_id: camera.dcs_8000lh_camera
```

### Tapo Device Integration

```yaml
# Voice commands for Tapo devices
intents:
  - sentences:
      - "Turn on the smart plug"
      - "Turn off the smart plug"
      - "What's the power consumption?"
```

### Frigate NVR Integration

```yaml
# Voice commands for Frigate
intents:
  - sentences:
      - "Start recording"
      - "Stop recording"
      - "Show me the recordings"
```

## Advanced Features

### Custom Intents

Create custom intents for specific use cases:

```yaml
# Example custom intent
intents:
  - sentences:
      - "Activate security mode"
      - "Enable security system"
    action:
      service: input_boolean.turn_on
      target:
        entity_id: input_boolean.security_mode
```

### Multi-Language Support

Configure multiple languages:

```yaml
# Multi-language configuration
conversation:
  intents:
    HomeAssistant:
      sentences:
        - "Turn on the {name}"  # English
        - "شغل ال{name}"        # Arabic
```

## Security Considerations

### Privacy Protection

1. **Local Processing**
   - Use local TTS engines
   - Enable local intents
   - Avoid cloud-based services

2. **Data Minimization**
   - Only expose necessary entities
   - Limit conversation history
   - Regular cleanup of logs

### Access Control

```yaml
# Restrict voice assistant access
homeassistant:
  auth_providers:
    - type: homeassistant
      users:
        - username: admin
          password: strong_password
          system_generated: false
```

---

*This guide is based on Home Assistant 2025.10.0 Assist documentation and best practices.*
