# YAML Configuration Best Practices

This guide covers advanced YAML configuration techniques and best practices for Home Assistant 2025.10.0, based on the [official documentation](https://www.home-assistant.io/docs/configuration/yaml/).

## YAML Syntax Standards

### Indentation and Formatting

Based on the [YAML configuration documentation](https://www.home-assistant.io/docs/configuration/yaml/), follow these formatting standards:

#### Proper Indentation
```yaml
# Use 2 spaces for indentation
automation:
  - alias: "Motion Light"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: 'on'
    action:
      - service: light.turn_on
        entity_id: light.living_room
```

#### Boolean Values
```yaml
# Use lowercase true/false
automation:
  - alias: "Test Automation"
    initial_state: true
    hide_entity: false
```

#### String Formatting
```yaml
# Use quotes for strings with special characters
sensor:
  - platform: template
    sensors:
      friendly_name: "Temperature Sensor"
      value_template: "{{ states('sensor.temperature') | float }}"
```

## Configuration Organization

### Splitting Configuration Files

Based on the [splitting configuration documentation](https://www.home-assistant.io/docs/configuration/splitting_configuration/):

#### Main Configuration File
```yaml
# configuration.yaml
default_config:

# Include separate files
automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml
group: !include groups.yaml
```

#### Include Directories
```yaml
# Include all files in a directory
automation: !include_dir_list automations/
script: !include_dir_list scripts/
```

#### Named Includes
```yaml
# Include files with names
automation: !include_dir_named automations/
script: !include_dir_named scripts/
```

### Package Configuration

Based on the [packages documentation](https://www.home-assistant.io/docs/configuration/packages/):

#### Package Structure
```
packages/
├── security.yaml
├── lighting.yaml
├── climate.yaml
└── energy.yaml
```

#### Package Configuration
```yaml
# configuration.yaml
homeassistant:
  packages: !include_dir_named packages/
```

#### Example Package
```yaml
# packages/security.yaml
automation:
  - alias: "Motion Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: 'on'
    action:
      - service: notify.mobile_app
        data:
          message: "Motion detected"

script:
  motion_alert:
    alias: "Motion Alert Script"
    sequence:
      - service: notify.mobile_app
        data:
          message: "Motion detected"
```

## Template Best Practices

### Safe Templates

Based on the [templating documentation](https://www.home-assistant.io/docs/configuration/templating/):

#### Safe Template Examples
```yaml
# Safe template with error handling
sensor:
  - platform: template
    sensors:
      safe_temperature:
        friendly_name: "Safe Temperature"
        value_template: >
          {% if states('sensor.temperature') != 'unknown' %}
            {{ states('sensor.temperature') | float }}
          {% else %}
            {{ states('sensor.temperature') }}
          {% endif %}
```

#### Template Performance
```yaml
# Efficient template expressions
sensor:
  - platform: template
    sensors:
      motion_status:
        friendly_name: "Motion Status"
        value_template: "{{ is_state('binary_sensor.motion', 'on') }}"
```

### Template Functions

#### Common Template Functions
```yaml
# Example template functions
sensor:
  - platform: template
    sensors:
      # String functions
      device_name:
        friendly_name: "Device Name"
        value_template: "{{ states('sensor.device') | title }}"
      
      # Numeric functions
      temperature_rounded:
        friendly_name: "Temperature Rounded"
        value_template: "{{ states('sensor.temperature') | float | round(1) }}"
      
      # Time functions
      last_updated:
        friendly_name: "Last Updated"
        value_template: "{{ states('sensor.temperature').last_updated }}"
```

## Entity Configuration

### Customizing Entities

Based on the [customizing entities documentation](https://www.home-assistant.io/docs/configuration/customizing/):

#### Entity Customization
```yaml
# customize.yaml
light.living_room:
  friendly_name: "Living Room Light"
  icon: mdi:sofa
  hidden: false

binary_sensor.motion:
  friendly_name: "Motion Sensor"
  device_class: motion
  hidden: false
```

#### Global Customization
```yaml
# Global customization
homeassistant:
  customize:
    light.living_room:
      friendly_name: "Living Room Light"
      icon: mdi:sofa
    binary_sensor.motion:
      friendly_name: "Motion Sensor"
      device_class: motion
```

### Entity Attributes

#### Custom Attributes
```yaml
# Example custom attributes
sensor:
  - platform: template
    sensors:
      custom_sensor:
        friendly_name: "Custom Sensor"
        value_template: "{{ states('sensor.temperature') | float }}"
        attribute_templates:
          unit_of_measurement: "°C"
          device_class: temperature
```

## Automation Configuration

### Advanced Automation Features

#### Variables in Automations
```yaml
# Example automation with variables
automation:
  - alias: "Dynamic Lighting"
    variables:
      brightness: "{{ states('input_number.brightness') | int }}"
      color_temp: "{{ states('input_number.color_temp') | int }}"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: 'on'
    action:
      - service: light.turn_on
        entity_id: light.living_room
        data:
          brightness: "{{ brightness }}"
          color_temp: "{{ color_temp }}"
```

#### Choose Actions
```yaml
# Example choose action
automation:
  - alias: "Conditional Action"
    trigger:
      - platform: state
        entity_id: person.admin
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

#### Repeat Actions
```yaml
# Example repeat action
automation:
  - alias: "Repeating Action"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: 'on'
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

## Script Configuration

### Advanced Script Features

#### Script Variables
```yaml
# Example script with variables
script:
  dynamic_lighting:
    alias: "Dynamic Lighting Script"
    variables:
      brightness: "{{ states('input_number.brightness') | int }}"
      color_temp: "{{ states('input_number.color_temp') | int }}"
    sequence:
      - service: light.turn_on
        entity_id: light.living_room
        data:
          brightness: "{{ brightness }}"
          color_temp: "{{ color_temp }}"
```

#### Script Modes
```yaml
# Example script modes
script:
  single_mode_script:
    alias: "Single Mode Script"
    mode: single
    sequence:
      - service: light.turn_on
        entity_id: light.living_room

  restart_mode_script:
    alias: "Restart Mode Script"
    mode: restart
    sequence:
      - service: light.turn_on
        entity_id: light.living_room
```

## Scene Configuration

### Advanced Scene Features

#### Scene with Conditions
```yaml
# Example scene with conditions
scene:
  - name: "Movie Mode"
    entities:
      light.living_room:
        state: on
        brightness: 50
        color_temp: 2000
      light.kitchen:
        state: off
    conditions:
      - condition: state
        entity_id: person.admin
        state: 'home'
```

#### Dynamic Scenes
```yaml
# Example dynamic scene
scene:
  - name: "Dynamic Scene"
    entities:
      light.living_room:
        state: on
        brightness: "{{ states('input_number.brightness') | int }}"
        color_temp: "{{ states('input_number.color_temp') | int }}"
```

## Integration Configuration

### Custom Integration Setup

#### Custom Component
```yaml
# Example custom component
custom_component:
  my_custom_component:
    api_key: "YOUR_API_KEY"
    host: "localhost"
    port: 8080
```

#### Platform Configuration
```yaml
# Example platform configuration
sensor:
  - platform: template
    sensors:
      custom_sensor:
        friendly_name: "Custom Sensor"
        value_template: "{{ states('sensor.temperature') | float }}"
        unit_of_measurement: "°C"
        device_class: temperature
```

## Security Configuration

### Secrets Management

Based on the [secrets documentation](https://www.home-assistant.io/docs/configuration/secrets/):

#### Secrets File
```yaml
# secrets.yaml
api_key: "YOUR_API_KEY"
password: "YOUR_PASSWORD"
username: "YOUR_USERNAME"
```

#### Using Secrets
```yaml
# configuration.yaml
sensor:
  - platform: template
    sensors:
      api_sensor:
        friendly_name: "API Sensor"
        value_template: "{{ states('sensor.api_data') | float }}"
        api_key: !secret api_key
```

### Authentication Configuration

#### Auth Providers
```yaml
# Example auth configuration
homeassistant:
  auth_providers:
    - type: homeassistant
      users:
        - username: admin
          password: !secret admin_password
          system_generated: false
    - type: trusted_networks
      trusted_networks:
        - 192.168.1.0/24
        - 127.0.0.1
```

## Performance Optimization

### Configuration Optimization

#### Efficient YAML
```yaml
# Efficient configuration
automation:
  - alias: "Efficient Automation"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: 'on'
    action:
      - service: light.turn_on
        entity_id: light.living_room
```

#### Template Optimization
```yaml
# Optimized templates
sensor:
  - platform: template
    sensors:
      optimized_sensor:
        friendly_name: "Optimized Sensor"
        value_template: "{{ is_state('binary_sensor.motion', 'on') }}"
```

## Troubleshooting

### Common YAML Issues

#### Syntax Errors
1. **Check Indentation**
   - Use 2 spaces consistently
   - Avoid mixing tabs and spaces

2. **Check Quotes**
   - Use quotes for strings with special characters
   - Escape quotes properly

3. **Check Brackets**
   - Match opening and closing brackets
   - Use proper YAML syntax

#### Configuration Validation

```bash
# Validate configuration
docker exec homeassistant python -m homeassistant --script check_config
```

#### Debug Tools
1. **Developer Tools** → **Services**
   - Test service calls
   - Verify service parameters

2. **Developer Tools** → **States**
   - Check entity states
   - Verify entity configuration

3. **Developer Tools** → **Events**
   - Monitor system events
   - Check for errors

---

*This guide is based on Home Assistant 2025.10.0 YAML configuration documentation and best practices.*
