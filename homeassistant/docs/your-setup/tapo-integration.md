# Tapo Integration Documentation

This document covers your Tapo device integration with Home Assistant, including setup, configuration, and automation possibilities.

## Tapo Integration Overview

Tapo is TP-Link's smart home ecosystem that includes smart plugs, cameras, light bulbs, and other IoT devices. Your Home Assistant setup includes Tapo integration for device discovery and control.

## Current Configuration

### Discovery Settings
Your Home Assistant is configured to discover Tapo devices automatically:

```yaml
# configuration.yaml
discovery:
  enable:
    - tapo

# Enable mDNS discovery for Tapo devices
zeroconf:
```

### Integration Status
- **Discovery:** Enabled
- **mDNS:** Enabled
- **Auto-Configuration:** Active

## Tapo Device Types

### Supported Devices
Tapo integration supports various device types:

#### Smart Plugs
- **Tapo P100** - Basic smart plug
- **Tapo P105** - Smart plug with energy monitoring
- **Tapo P110** - Outdoor smart plug

#### Smart Bulbs
- **Tapo L510** - White smart bulb
- **Tapo L530** - Color smart bulb
- **Tapo L900** - LED strip

#### Smart Cameras
- **Tapo C100** - Indoor camera
- **Tapo C200** - Pan/tilt camera
- **Tapo C310** - Outdoor camera

#### Smart Switches
- **Tapo S200** - Smart switch
- **Tapo S200B** - Smart switch with neutral

## Device Discovery

### Automatic Discovery
Your Home Assistant will automatically discover Tapo devices on your network:

1. **Network Scan:** Home Assistant scans for Tapo devices
2. **Device Detection:** Identifies device type and capabilities
3. **Auto-Configuration:** Creates entities automatically
4. **Entity Creation:** Adds devices to entity registry

### Manual Configuration
If automatic discovery fails, you can manually configure devices:

```yaml
# Example manual configuration
tapo_control:
  host: localhost
  port: 8080
  username: your_tapo_username
  password: your_tapo_password
```

## Entity Types

### Switch Entities
For smart plugs and switches:
- **Entity ID:** `switch.tapo_[device_name]`
- **State:** on/off
- **Attributes:** Power consumption, energy usage

### Light Entities
For smart bulbs and strips:
- **Entity ID:** `light.tapo_[device_name]`
- **State:** on/off
- **Attributes:** Brightness, color, color temperature

### Camera Entities
For smart cameras:
- **Entity ID:** `camera.tapo_[device_name]`
- **State:** Available/unavailable
- **Attributes:** Stream URL, recording status

### Sensor Entities
For energy monitoring:
- **Entity ID:** `sensor.tapo_[device_name]_power`
- **State:** Current power consumption
- **Unit:** Watts

## Automation Possibilities

### Motion-Responsive Lighting
Create automations that respond to motion:

```yaml
# Example automation
automation:
  - alias: "Tapo Motion Light"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion_sensor
        to: 'on'
    action:
      - service: light.turn_on
        entity_id: light.tapo_bedroom_light
```

### Energy Monitoring
Monitor power consumption:

```yaml
# Example automation for high power usage
automation:
  - alias: "High Power Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.tapo_plug_power
        above: 1000
    action:
      - service: notify.mobile_app
        data:
          message: "High power consumption detected"
```

### Scheduled Control
Automate device schedules:

```yaml
# Example automation for scheduled control
automation:
  - alias: "Evening Lights"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: light.turn_on
        entity_id: light.tapo_living_room
```

## Voice Assistant Integration

### Exposed Entities
Tapo devices can be exposed to voice assistant:

```yaml
# Example voice assistant configuration
homeassistant:
  exposed_entities:
    light.tapo_bedroom_light:
      assistants:
        conversation:
          should_expose: true
```

### Voice Commands
With exposed entities, you can use voice commands:
- "Turn on the Tapo light"
- "Set the bedroom light to 50% brightness"
- "Change the living room light to blue"

## Dashboard Integration

### Card Types for Tapo Devices

#### Light Cards
```yaml
# Light control card
type: light
entity: light.tapo_bedroom_light
name: "Bedroom Light"
```

#### Switch Cards
```yaml
# Switch control card
type: entities
entities:
  - switch.tapo_living_room_plug
  - switch.tapo_kitchen_plug
```

#### Energy Monitoring Cards
```yaml
# Energy monitoring card
type: entities
title: "Energy Usage"
entities:
  - sensor.tapo_plug_power
  - sensor.tapo_plug_energy_today
```

## Troubleshooting

### Common Issues

#### Device Not Discovered
- **Check Network:** Ensure device is on same network
- **Check mDNS:** Verify mDNS is working
- **Manual Configuration:** Try manual device addition

#### Connection Issues
- **Check Credentials:** Verify Tapo account credentials
- **Check Network:** Ensure stable network connection
- **Check Firewall:** Verify no firewall blocking

#### Entity Not Working
- **Check Integration:** Verify integration is loaded
- **Check Logs:** Look for error messages
- **Restart Integration:** Try restarting the integration

### Debug Steps
1. **Check Logs:** Look for Tapo-related errors
2. **Test Network:** Ping device IP address
3. **Verify Credentials:** Test with Tapo app
4. **Check Integration:** Verify integration status

## Security Considerations

### Network Security
- **Local Network:** Keep devices on secure network
- **Firewall:** Configure appropriate firewall rules
- **Updates:** Keep device firmware updated

### Privacy
- **Data Collection:** Review Tapo privacy settings
- **Local Control:** Prefer local control over cloud
- **Credentials:** Use strong, unique passwords

## Maintenance

### Regular Tasks
1. **Check Device Status:** Verify all devices are online
2. **Update Firmware:** Keep devices updated
3. **Review Energy Usage:** Monitor power consumption
4. **Test Automations:** Verify automation functionality

### Performance Monitoring
- **Network Latency:** Monitor device response times
- **Power Usage:** Track energy consumption
- **Automation Performance:** Check automation reliability

## Advanced Configuration

### Custom Automations
Create complex automations using Tapo devices:

```yaml
# Example complex automation
automation:
  - alias: "Smart Home Evening Mode"
    trigger:
      - platform: sun
        event: sunset
        offset: "-00:30:00"
    condition:
      - condition: state
        entity_id: person.admin
        state: 'home'
    action:
      - service: light.turn_on
        entity_id: light.tapo_living_room
        data:
          brightness: 128
          color_name: warm_white
      - service: switch.turn_on
        entity_id: switch.tapo_entrance_plug
```

### Integration with Other Systems
Tapo devices can be integrated with:
- **Frigate NVR:** Camera integration
- **DCS-8000LH System:** Motion-triggered lighting
- **Weather Integration:** Weather-based automation

---

*This documentation covers Tapo integration specific to your Home Assistant setup.*
