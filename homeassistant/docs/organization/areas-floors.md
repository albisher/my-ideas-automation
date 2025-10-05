# Areas and Floors Organization

This guide covers organizing your Home Assistant setup using areas and floors, based on the latest [official documentation](https://www.home-assistant.io/docs/configuration/areas/).

## Your Current Areas

### Existing Areas
Based on your current configuration, you have the following areas defined:

1. **Living Room**
   - **ID**: `living_room`
   - **Created**: 2025-09-25T17:02:06.919016+00:00
   - **Icon**: Not specified (default)

2. **Kitchen**
   - **ID**: `kitchen`
   - **Created**: 2025-09-25T17:02:06.919061+00:00
   - **Icon**: Not specified (default)

3. **Bedroom**
   - **ID**: `bedroom`
   - **Created**: 2025-09-25T17:02:06.919072+00:00
   - **Icon**: Not specified (default)

## Areas Configuration

### Creating Areas

#### Via UI (Recommended)
1. Go to **Configuration** → **Areas & Floors**
2. Click **Add Area**
3. Enter area name and select icon
4. Click **Save**

#### Via YAML (Advanced)
```yaml
# configuration.yaml
areas:
  - name: "Living Room"
    icon: mdi:sofa
  - name: "Kitchen"
    icon: mdi:chef-hat
  - name: "Bedroom"
    icon: mdi:bed
  - name: "Bathroom"
    icon: mdi:shower
  - name: "Garage"
    icon: mdi:garage
```

### Area Icons

#### Recommended Icons for Your Setup
```yaml
# Living Room
icon: mdi:sofa

# Kitchen
icon: mdi:chef-hat

# Bedroom
icon: mdi:bed

# Bathroom
icon: mdi:shower

# Garage
icon: mdi:garage

# Outdoor
icon: mdi:tree

# Office
icon: mdi:desk
```

## Floors Configuration

### Creating Floors

Based on the [floors documentation](https://www.home-assistant.io/docs/configuration/floors/), you can organize areas by floors:

#### Single Floor (Ground Level)
```yaml
# For single-story homes
floors:
  - name: "Ground Floor"
    level: 0
    icon: mdi:home
```

#### Multi-Floor Setup
```yaml
# For multi-story homes
floors:
  - name: "Basement"
    level: -1
    icon: mdi:stairs-down
  - name: "Ground Floor"
    level: 0
    icon: mdi:home
  - name: "First Floor"
    level: 1
    icon: mdi:stairs-up
  - name: "Second Floor"
    level: 2
    icon: mdi:stairs-up
```

### Assigning Areas to Floors

```yaml
# Example floor assignment
areas:
  - name: "Living Room"
    floor_id: "ground_floor"
    icon: mdi:sofa
  - name: "Kitchen"
    floor_id: "ground_floor"
    icon: mdi:chef-hat
  - name: "Master Bedroom"
    floor_id: "first_floor"
    icon: mdi:bed
```

## Device Organization

### Assigning Devices to Areas

#### Via UI
1. Go to **Configuration** → **Devices & Services**
2. Click on a device
3. Select the appropriate area
4. Click **Update**

#### Via YAML
```yaml
# Example device configuration
device_registry:
  - identifiers:
      - [tapo, "device_id"]
    name: "Living Room Smart Plug"
    area_id: living_room
    labels:
      - energy_monitoring
      - smart_plug
```

### Your Device Assignments

Based on your current setup, consider assigning:

#### DCS-8000LH Camera System
```yaml
# Camera system devices
device_registry:
  - identifiers:
      - [frigate, "dcs8000lh"]
    name: "DCS-8000LH Camera System"
    area_id: living_room  # or outdoor
    labels:
      - security
      - camera
      - motion_detection
```

#### Tapo Devices
```yaml
# Tapo smart plugs
device_registry:
  - identifiers:
      - [tapo, "plug_id"]
    name: "Living Room Smart Plug"
    area_id: living_room
    labels:
      - energy_monitoring
      - smart_plug
```

## Labels and Categories

### Using Labels

Labels help organize devices by function:

```yaml
# Example labels for your setup
labels:
  # Security
  - security
  - camera
  - motion_detection
  
  # Energy
  - energy_monitoring
  - smart_plug
  
  # Lighting
  - smart_light
  - dimmer
  
  # Climate
  - temperature
  - humidity
```

### Device Categories

```yaml
# Example categories
categories:
  # Security devices
  security:
    - camera.dcs_8000lh_camera
    - binary_sensor.dcs_8000lh_motion
  
  # Energy devices
  energy:
    - sensor.tapo_plug_power
    - sensor.tapo_plug_energy_today
  
  # Lighting devices
  lighting:
    - light.living_room_light
    - switch.kitchen_light
```

## Dashboard Integration

### Area-Based Views

Create dashboard views for each area:

```yaml
# ui-lovelace.yaml
views:
  - title: "Living Room"
    path: living-room
    cards:
      - type: entities
        title: "Living Room Devices"
        entities:
          - camera.dcs_8000lh_camera
          - binary_sensor.dcs_8000lh_motion
          - sensor.dcs_8000lh_person_count
  
  - title: "Kitchen"
    path: kitchen
    cards:
      - type: entities
        title: "Kitchen Devices"
        entities:
          - switch.tapo_kitchen_plug
          - sensor.tapo_kitchen_power
```

### Floor-Based Views

```yaml
# Floor-based organization
views:
  - title: "Ground Floor"
    path: ground-floor
    cards:
      - type: entities
        title: "Ground Floor Devices"
        entities:
          - area.living_room
          - area.kitchen
  
  - title: "First Floor"
    path: first-floor
    cards:
      - type: entities
        title: "First Floor Devices"
        entities:
          - area.bedroom
          - area.bathroom
```

## Automation Integration

### Area-Based Automations

```yaml
# Example area-based automation
automation:
  - alias: "Living Room Motion Light"
    trigger:
      - platform: state
        entity_id: binary_sensor.dcs_8000lh_motion
        to: 'on'
    condition:
      - condition: state
        entity_id: sun.sun
        state: 'below_horizon'
    action:
      - service: light.turn_on
        target:
          area_id: living_room
```

### Floor-Based Automations

```yaml
# Example floor-based automation
automation:
  - alias: "Night Mode - Ground Floor"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: light.turn_off
        target:
          area_id: 
            - living_room
            - kitchen
```

## Voice Assistant Integration

### Area-Based Voice Commands

```yaml
# Voice commands for areas
intents:
  - sentences:
      - "Turn on the lights in the {area}"
      - "Turn off the lights in the {area}"
      - "What's the temperature in the {area}?"
    action:
      service: light.turn_on
      target:
        area_id: "{{ area }}"
```

### Floor-Based Voice Commands

```yaml
# Voice commands for floors
intents:
  - sentences:
      - "Turn on all lights on the {floor}"
      - "Turn off all lights on the {floor}"
    action:
      service: light.turn_on
      target:
        floor_id: "{{ floor }}"
```

## Best Practices

### Naming Conventions

#### Area Names
- Use clear, descriptive names
- Avoid abbreviations
- Use consistent naming patterns

```yaml
# Good examples
- "Living Room"
- "Master Bedroom"
- "Guest Bathroom"

# Avoid
- "LR"
- "MBR"
- "GB"
```

#### Floor Names
- Use logical floor names
- Consider accessibility
- Use consistent numbering

```yaml
# Good examples
- "Basement"
- "Ground Floor"
- "First Floor"
- "Second Floor"

# Avoid
- "Floor 1"
- "Floor 2"
- "Level A"
```

### Organization Tips

1. **Logical Grouping**
   - Group related devices by area
   - Use consistent labeling
   - Create meaningful categories

2. **Scalability**
   - Plan for future devices
   - Use consistent naming
   - Document your organization

3. **Accessibility**
   - Use clear, descriptive names
   - Consider voice assistant usage
   - Test with different users

## Troubleshooting

### Common Issues

#### Areas Not Showing
1. Check area configuration
2. Verify device assignments
3. Check for YAML syntax errors

#### Devices Not Appearing in Areas
1. Verify device area assignment
2. Check device configuration
3. Restart Home Assistant

#### Floor Organization Issues
1. Check floor configuration
2. Verify area assignments
3. Test floor-based automations

### Debug Tools

#### Developer Tools
1. **States Tab**
   - Check area entities
   - Verify device states

2. **Services Tab**
   - Test area-based services
   - Verify floor assignments

3. **Events Tab**
   - Monitor area events
   - Check for errors

---

*This guide is based on Home Assistant 2025.10.0 organization documentation and best practices.*
