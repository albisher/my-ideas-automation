# Google Home Integration with Home Assistant

This guide covers integrating Google Home devices with Home Assistant for centralized control and automation.

## Overview

Google Home integration in Home Assistant provides:
- **Google Cast**: Control Google Home speakers, displays, and Chromecast devices
- **Google Assistant**: Voice control of Home Assistant entities
- **Device Discovery**: Automatic discovery of Google Home devices on your network

## Prerequisites

- Google Home devices connected to your network
- Home Assistant running and accessible
- All devices on the same network segment

## Configuration

### 1. Basic Integration Setup

The following integrations are configured in `configuration.yaml`:

```yaml
# Discovery Configuration for Google Home devices
discovery:
  enable:
    - google_cast

# Google Cast integration for Google Home devices
google_cast:

# Google Assistant integration for voice control
google_assistant:
```

### 2. Google Cast Integration

The Google Cast integration automatically discovers and controls:
- Google Home speakers
- Google Nest Hub displays
- Chromecast devices
- Android TV devices with Google Cast

**Features:**
- Volume control
- Media playback control
- Display control for Nest Hub devices
- Group management

### 3. Google Assistant Integration

For voice control of Home Assistant entities:

#### Option A: Home Assistant Cloud (Recommended)
1. Go to **Settings > Voice Assistant** in Home Assistant
2. Enable **Google Assistant**
3. Expose desired entities
4. In Google Home app: **Add > Set up device > Works with Google**
5. Search for **Home Assistant Cloud by Nabu Casa**

#### Option B: Manual Setup
1. Create a project in [Google Developer Console](https://console.developers.google.com/)
2. Enable Google Assistant API
3. Create OAuth 2.0 credentials
4. Configure the integration in Home Assistant

## Device Management

### Viewing Google Home Devices

After configuration, Google Home devices will appear in:
- **Settings > Devices & Services > Google Cast**
- **Settings > Devices & Services > Google Assistant**

### Device Categories

**Google Cast Devices:**
- `media_player.google_home_mini` - Google Home Mini
- `media_player.google_nest_hub` - Nest Hub
- `media_player.chromecast` - Chromecast

**Control Examples:**
```yaml
# Turn on Google Home
service: media_player.turn_on
target:
  entity_id: media_player.google_home_mini

# Set volume
service: media_player.volume_set
target:
  entity_id: media_player.google_home_mini
data:
  volume_level: 0.5

# Play media
service: media_player.play_media
target:
  entity_id: media_player.google_home_mini
data:
  media_content_id: "https://example.com/audio.mp3"
  media_content_type: "music"
```

## Automation Examples

### 1. Morning Routine
```yaml
automation:
  - alias: "Morning Announcement"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: media_player.play_media
        target:
          entity_id: media_player.google_home_mini
        data:
          media_content_id: "Good morning! It's time to start your day."
          media_content_type: "music"
```

### 2. Doorbell Integration
```yaml
automation:
  - alias: "Doorbell Announcement"
    trigger:
      - platform: state
        entity_id: binary_sensor.doorbell
        to: "on"
    action:
      - service: media_player.play_media
        target:
          entity_id: media_player.google_home_mini
        data:
          media_content_id: "Someone is at the door!"
          media_content_type: "music"
```

### 3. Weather Updates
```yaml
automation:
  - alias: "Weather Update"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: media_player.play_media
        target:
          entity_id: media_player.google_home_mini
        data:
          media_content_id: "Today's weather is {{ states('weather.home') }}"
          media_content_type: "music"
```

## Dashboard Cards

### Media Player Card
```yaml
type: media-control
entity: media_player.google_home_mini
```

### Cast Card
```yaml
type: cast
entity: media_player.google_home_mini
```

## Troubleshooting

### Common Issues

1. **Devices Not Discovered**
   - Ensure devices are on the same network
   - Check firewall settings
   - Restart Home Assistant

2. **Voice Commands Not Working**
   - Verify Google Assistant integration is properly configured
   - Check entity exposure settings
   - Test with simple commands first

3. **Media Playback Issues**
   - Verify network connectivity
   - Check device compatibility
   - Update device firmware

### Debug Steps

1. Check logs: **Settings > System > Logs**
2. Verify network connectivity
3. Test with Home Assistant mobile app
4. Check device status in **Settings > Devices & Services**

## Advanced Configuration

### Custom Device Names
```yaml
# In customize.yaml
media_player.google_home_mini:
  friendly_name: "Living Room Speaker"
  icon: mdi:google-home
```

### Group Management
```yaml
# Create speaker groups
group:
  google_speakers:
    name: "Google Speakers"
    entities:
      - media_player.google_home_mini
      - media_player.google_nest_hub
```

### Scene Integration
```yaml
scene:
  - name: "Movie Night"
    entities:
      media_player.google_home_mini:
        state: "on"
        volume_level: 0.3
      light.living_room:
        state: "on"
        brightness: 50
```

## Security Considerations

- Use HTTPS for Home Assistant access
- Keep devices updated
- Use strong network passwords
- Consider VLAN separation for IoT devices

## Next Steps

1. Test basic device control
2. Set up voice commands
3. Create automation routines
4. Configure dashboard cards
5. Explore advanced features

For more information, refer to the [Home Assistant Google Cast documentation](https://www.home-assistant.io/integrations/google_cast/) and [Google Assistant integration guide](https://www.home-assistant.io/integrations/google_assistant/).
