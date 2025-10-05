# Automation Basics

This guide covers the fundamentals of Home Assistant automations, including triggers, conditions, actions, and best practices.

## What are Automations?

Automations are rules that automatically trigger actions based on specific conditions. They allow you to create intelligent behaviors for your smart home without manual intervention.

## Automation Components

### 1. Triggers
Triggers define when an automation should run. Common trigger types:

#### State Triggers
```yaml
trigger:
  - platform: state
    entity_id: binary_sensor.motion_sensor
    to: 'on'
```

#### Time Triggers
```yaml
trigger:
  - platform: time
    at: "08:00:00"
```

#### Sun Triggers
```yaml
trigger:
  - platform: sun
    event: sunset
```

#### Device Triggers
```yaml
trigger:
  - platform: device
    device_id: your_device_id
    domain: light
    type: turned_on
```

### 2. Conditions
Conditions determine if an automation should continue after being triggered:

#### State Conditions
```yaml
condition:
  - condition: state
    entity_id: person.admin
    state: 'home'
```

#### Time Conditions
```yaml
condition:
  - condition: time
    after: "18:00:00"
    before: "22:00:00"
```

#### Numeric State Conditions
```yaml
condition:
  - condition: numeric_state
    entity_id: sensor.temperature
    above: 25
```

### 3. Actions
Actions define what happens when an automation runs:

#### Service Calls
```yaml
action:
  - service: light.turn_on
    entity_id: light.living_room
    data:
      brightness: 128
      color_name: warm_white
```

#### Delays
```yaml
action:
  - delay: "00:05:00"  # 5 minutes
```

#### Wait for Trigger
```yaml
action:
  - wait_for_trigger:
      - platform: state
        entity_id: binary_sensor.motion_sensor
        to: 'off'
```

## Your Current Automations

### Motion Detection Automations

#### DCS-8000LH Motion Detected
```yaml
automation:
  - alias: "DCS-8000LH Motion Detected"
    trigger:
      - platform: state
        entity_id: binary_sensor.dcs_8000lh_motion
        to: 'on'
    action:
      - service: script.motion_alert
```

#### Person Detection Alert
```yaml
automation:
  - alias: "Person Detection Alert"
    trigger:
      - platform: state
        entity_id: sensor.dcs_8000lh_person_count
        to: '1'
    action:
      - service: notify.mobile_app
        data:
          message: "Person detected in camera view"
```

#### Car Detection Alert
```yaml
automation:
  - alias: "Car Detection Alert"
    trigger:
      - platform: state
        entity_id: sensor.dcs_8000lh_car_count
        to: '1'
    action:
      - service: notify.mobile_app
        data:
          message: "Vehicle detected in camera view"
```

### Time-Based Automations

#### Night Mode Activation
```yaml
automation:
  - alias: "Night Mode Activation"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: light.turn_on
        entity_id: light.outdoor_lights
```

#### Day Mode Activation
```yaml
automation:
  - alias: "Day Mode Activation"
    trigger:
      - platform: sun
        event: sunrise
    action:
      - service: light.turn_off
        entity_id: light.outdoor_lights
```

### Security Automations

#### Security Mode Activation
```yaml
automation:
  - alias: "Security Mode Activation"
    trigger:
      - platform: state
        entity_id: input_boolean.security_mode
        to: 'on'
    action:
      - service: camera.enable_motion_detection
        entity_id: camera.dcs_8000lh_camera
```

#### Security Mode Deactivation
```yaml
automation:
  - alias: "Security Mode Deactivation"
    trigger:
      - platform: state
        entity_id: input_boolean.security_mode
        to: 'off'
    action:
      - service: camera.disable_motion_detection
        entity_id: camera.dcs_8000lh_camera
```

## Automation Modes

### Single Mode
```yaml
mode: single
```
- Runs once when triggered
- Ignores additional triggers while running

### Restart Mode
```yaml
mode: restart
```
- Restarts if triggered again while running
- Useful for motion-activated lights

### Queued Mode
```yaml
mode: queued
```
- Queues multiple triggers
- Runs each trigger in sequence

### Parallel Mode
```yaml
mode: parallel
```
- Runs multiple instances simultaneously
- Useful for independent actions

## Advanced Features

### Variables
```yaml
automation:
  - alias: "Dynamic Lighting"
    variables:
      brightness: "{{ states('input_number.brightness') | int }}"
      color_temp: "{{ states('input_number.color_temp') | int }}"
    action:
      - service: light.turn_on
        entity_id: light.living_room
        data:
          brightness: "{{ brightness }}"
          color_temp: "{{ color_temp }}"
```

### Choose Actions
```yaml
automation:
  - alias: "Conditional Action"
    action:
      - choose:
          - conditions:
              - condition: state
                entity_id: person.admin
                state: 'home'
            sequence:
              - service: light.turn_on
                entity_id: light.living_room
          - conditions:
              - condition: state
                entity_id: person.admin
                state: 'away'
            sequence:
              - service: light.turn_off
                entity_id: light.living_room
```

### Repeat Actions
```yaml
automation:
  - alias: "Repeating Action"
    action:
      - repeat:
          count: 3
          sequence:
            - service: light.turn_on
              entity_id: light.flash_light
            - delay: "00:00:01"
            - service: light.turn_off
              entity_id: light.flash_light
```

## Blueprints

### Using Blueprints
Blueprints are pre-made automation templates:

#### Motion-Activated Light Blueprint
```yaml
# Available in your system
blueprint:
  name: Motion-activated Light
  description: Turn on a light when motion is detected
  input:
    motion_entity:
      name: Motion Sensor
    light_target:
      name: Light
    no_motion_wait:
      name: Wait time
      default: 120
```

#### Zone Notification Blueprint
```yaml
# Available in your system
blueprint:
  name: Zone Notification
  description: Send notification when person leaves zone
  input:
    person_entity:
      name: Person
    zone_entity:
      name: Zone
    notify_device:
      name: Device to notify
```

## Best Practices

### 1. Naming Conventions
- Use descriptive names: "Living Room Motion Light"
- Include location and function
- Use consistent naming patterns

### 2. Organization
- Group related automations
- Use tags for categorization
- Document complex automations

### 3. Testing
- Test automations in safe conditions
- Use the automation editor for testing
- Check logs for errors

### 4. Performance
- Avoid too many automations
- Use conditions to limit execution
- Monitor system performance

## Troubleshooting

### Common Issues

#### Automation Not Triggering
- Check trigger conditions
- Verify entity states
- Check automation logs

#### Automation Running Too Often
- Add conditions to limit execution
- Check for multiple triggers
- Review automation mode

#### Performance Issues
- Reduce automation complexity
- Check for infinite loops
- Monitor system resources

### Debug Tools
- **Developer Tools** → **Services**: Test service calls
- **Developer Tools** → **States**: Check entity states
- **Developer Tools** → **Events**: Monitor events
- **Configuration** → **Logs**: Check for errors

## Examples for Your Setup

### Motion-Responsive Lighting
```yaml
automation:
  - alias: "DCS-8000LH Motion Light"
    trigger:
      - platform: state
        entity_id: binary_sensor.dcs_8000lh_motion
        to: 'on'
    condition:
      - condition: time
        after: "18:00:00"
        before: "06:00:00"
    action:
      - service: light.turn_on
        entity_id: light.outdoor_lights
      - wait_for_trigger:
          - platform: state
            entity_id: binary_sensor.dcs_8000lh_motion
            to: 'off'
      - delay: "00:05:00"
      - service: light.turn_off
        entity_id: light.outdoor_lights
```

### Person Detection Notification
```yaml
automation:
  - alias: "Person Detection Alert"
    trigger:
      - platform: state
        entity_id: sensor.dcs_8000lh_person_count
        to: '1'
    condition:
      - condition: state
        entity_id: person.admin
        state: 'away'
    action:
      - service: notify.mobile_app
        data:
          title: "Security Alert"
          message: "Person detected while away"
          data:
            actions:
              - action: "view_camera"
                title: "View Camera"
```

---

*This guide covers automation basics specific to your Home Assistant setup.*
