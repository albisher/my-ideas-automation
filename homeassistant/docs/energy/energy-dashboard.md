# Energy Dashboard Configuration

This guide covers setting up and optimizing the Home Assistant Energy Dashboard based on the latest [official documentation](https://www.home-assistant.io/docs/energy/).

## Energy Dashboard Overview

The Energy Dashboard provides comprehensive energy monitoring and management for your home, including electricity grid monitoring, solar panel integration, and individual device tracking.

## Your Current Energy Setup

### Available Energy Entities
Based on your current setup, you have the following energy-related entities:

#### Power Monitoring
- **D-Link Smart Plug**: `sensor.dlink_smart_plug_power` (with connection issues)
- **Tapo Smart Plugs**: Power consumption monitoring available

#### Weather Integration
- **Weather Forecast**: `weather.forecast_home` for solar calculations

## Basic Energy Configuration

### Enable Energy Dashboard

1. **Access Energy Settings**
   - Go to **Configuration** → **Energy**
   - Click **Start Setup**

2. **Configure Basic Settings**
   ```yaml
   # configuration.yaml
   energy:
     use_grid_cost: true
     use_solar_cost: true
   ```

### Grid Configuration

#### Electricity Grid Setup
```yaml
# configuration.yaml
energy:
  use_grid_cost: true
  grid_consumption_source: sensor.grid_consumption
  grid_return_source: sensor.grid_return
```

#### Cost Configuration
```yaml
# Example cost configuration
energy:
  grid_consumption_source: sensor.grid_consumption
  grid_return_source: sensor.grid_return
  cost_per_kwh: 0.15  # KWD per kWh
  cost_per_kwh_return: 0.10  # KWD per kWh for solar return
```

## Solar Panel Integration

### Solar Configuration

Based on the [solar panels documentation](https://www.home-assistant.io/docs/energy/solar_panels/):

```yaml
# configuration.yaml
energy:
  solar_production_source: sensor.solar_production
  solar_consumption_source: sensor.solar_consumption
```

### Solar Sensors

#### Production Sensors
```yaml
# Example solar production sensor
sensor:
  - platform: template
    sensors:
      solar_production:
        friendly_name: "Solar Production"
        unit_of_measurement: "W"
        value_template: "{{ states('sensor.solar_panel_power') | float }}"
```

#### Consumption Sensors
```yaml
# Example solar consumption sensor
sensor:
  - platform: template
    sensors:
      solar_consumption:
        friendly_name: "Solar Consumption"
        unit_of_measurement: "W"
        value_template: "{{ states('sensor.solar_consumption_power') | float }}"
```

## Individual Device Monitoring

### Power Monitoring Setup

Based on the [individual devices documentation](https://www.home-assistant.io/docs/energy/individual_devices/):

#### Tapo Smart Plug Monitoring
```yaml
# Example Tapo power monitoring
sensor:
  - platform: template
    sensors:
      tapo_plug_daily_cost:
        friendly_name: "Tapo Plug Daily Cost"
        unit_of_measurement: "KWD"
        value_template: >
          {{ states('sensor.tapo_plug_energy_today') | float * 0.15 }}
```

#### D-Link Smart Plug Monitoring
```yaml
# Example D-Link power monitoring (when working)
sensor:
  - platform: template
    sensors:
      dlink_plug_daily_cost:
        friendly_name: "D-Link Plug Daily Cost"
        unit_of_measurement: "KWD"
        value_template: >
          {{ states('sensor.dlink_smart_plug_energy_today') | float * 0.15 }}
```

### Energy Consumption Tracking

#### Daily Energy Consumption
```yaml
# Example daily consumption tracking
sensor:
  - platform: template
    sensors:
      daily_energy_consumption:
        friendly_name: "Daily Energy Consumption"
        unit_of_measurement: "kWh"
        value_template: >
          {{ states('sensor.tapo_plug_energy_today') | float + 
             states('sensor.dlink_smart_plug_energy_today') | float }}
```

#### Monthly Energy Consumption
```yaml
# Example monthly consumption tracking
sensor:
  - platform: template
    sensors:
      monthly_energy_consumption:
        friendly_name: "Monthly Energy Consumption"
        unit_of_measurement: "kWh"
        value_template: >
          {{ states('sensor.tapo_plug_energy_this_month') | float + 
             states('sensor.dlink_smart_plug_energy_this_month') | float }}
```

## Cost Calculation

### Electricity Cost Configuration

#### Basic Cost Setup
```yaml
# configuration.yaml
energy:
  cost_per_kwh: 0.15  # KWD per kWh
  cost_per_kwh_return: 0.10  # KWD per kWh for solar return
```

#### Time-of-Use Pricing
```yaml
# Example time-of-use pricing
energy:
  cost_per_kwh: 0.15  # Peak hours (6 PM - 10 PM)
  cost_per_kwh_off_peak: 0.10  # Off-peak hours
  cost_per_kwh_return: 0.08  # Solar return rate
```

### Cost Sensors

#### Daily Cost Calculation
```yaml
# Example daily cost sensor
sensor:
  - platform: template
    sensors:
      daily_electricity_cost:
        friendly_name: "Daily Electricity Cost"
        unit_of_measurement: "KWD"
        value_template: >
          {{ states('sensor.daily_energy_consumption') | float * 0.15 }}
```

#### Monthly Cost Calculation
```yaml
# Example monthly cost sensor
sensor:
  - platform: template
    sensors:
      monthly_electricity_cost:
        friendly_name: "Monthly Electricity Cost"
        unit_of_measurement: "KWD"
        value_template: >
          {{ states('sensor.monthly_energy_consumption') | float * 0.15 }}
```

## Dashboard Integration

### Energy Dashboard Cards

#### Power Consumption Card
```yaml
# ui-lovelace.yaml
type: entities
title: "Energy Consumption"
entities:
  - sensor.tapo_plug_power
  - sensor.dlink_smart_plug_power
  - sensor.daily_energy_consumption
  - sensor.daily_electricity_cost
```

#### Energy History Card
```yaml
# Energy history graph
type: history-graph
entities:
  - sensor.tapo_plug_power
  - sensor.dlink_smart_plug_power
hours_to_show: 24
```

#### Cost Tracking Card
```yaml
# Cost tracking
type: entities
title: "Energy Costs"
entities:
  - sensor.daily_electricity_cost
  - sensor.monthly_electricity_cost
  - sensor.tapo_plug_daily_cost
  - sensor.dlink_smart_plug_daily_cost
```

## Automation Integration

### Energy-Based Automations

#### High Power Usage Alert
```yaml
# Example high power usage automation
automation:
  - alias: "High Power Usage Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.tapo_plug_power
        above: 1000  # Watts
    action:
      - service: notify.mobile_app
        data:
          title: "High Power Usage"
          message: "Power consumption is above 1000W"
```

#### Energy Cost Alert
```yaml
# Example energy cost automation
automation:
  - alias: "Daily Energy Cost Alert"
    trigger:
      - platform: time
        at: "23:00:00"
    action:
      - service: notify.mobile_app
        data:
          title: "Daily Energy Cost"
          message: "Today's electricity cost: {{ states('sensor.daily_electricity_cost') }} KWD"
```

## Troubleshooting

### Common Issues

#### Energy Dashboard Not Showing Data
1. **Check Sensor Configuration**
   - Verify energy sensors are configured
   - Check sensor units and states

2. **Check Data Availability**
   - Ensure sensors have historical data
   - Wait for data to accumulate

3. **Check Configuration**
   - Verify energy configuration
   - Check for YAML syntax errors

#### Cost Calculations Not Working
1. **Check Cost Configuration**
   - Verify cost_per_kwh setting
   - Check currency configuration

2. **Check Sensor States**
   - Verify energy sensors are working
   - Check sensor values and units

3. **Check Calculations**
   - Verify template expressions
   - Test calculations manually

### Debug Tools

#### Developer Tools
1. **States Tab**
   - Check energy sensor states
   - Verify sensor values

2. **Services Tab**
   - Test energy services
   - Verify service calls

3. **Events Tab**
   - Monitor energy events
   - Check for errors

#### Log Analysis
```yaml
# Enable energy logging
logger:
  default: info
  logs:
    homeassistant.components.energy: debug
```

## Best Practices

### Data Collection

1. **Historical Data**
   - Ensure sensors have sufficient historical data
   - Use long-term statistics for accurate calculations

2. **Sensor Accuracy**
   - Calibrate energy sensors regularly
   - Verify sensor readings against utility bills

3. **Data Retention**
   - Configure appropriate data retention
   - Monitor database size

### Cost Optimization

1. **Time-of-Use Pricing**
   - Configure time-based pricing
   - Optimize energy usage during off-peak hours

2. **Solar Integration**
   - Maximize solar energy usage
   - Optimize battery storage

3. **Device Management**
   - Monitor high-consumption devices
   - Implement energy-saving automations

## Integration with Your Setup

### DCS-8000LH Camera System
```yaml
# Camera system energy monitoring
sensor:
  - platform: template
    sensors:
      camera_system_power:
        friendly_name: "Camera System Power"
        unit_of_measurement: "W"
        value_template: "{{ states('sensor.dcs_8000lh_power') | float }}"
```

### Tapo Device Integration
```yaml
# Tapo energy monitoring
sensor:
  - platform: template
    sensors:
      tapo_total_power:
        friendly_name: "Tapo Total Power"
        unit_of_measurement: "W"
        value_template: >
          {{ states('sensor.tapo_plug_power') | float + 
             states('sensor.tapo_kitchen_plug_power') | float }}
```

### Frigate NVR Integration
```yaml
# Frigate energy monitoring
sensor:
  - platform: template
    sensors:
      frigate_power:
        friendly_name: "Frigate NVR Power"
        unit_of_measurement: "W"
        value_template: "{{ states('sensor.frigate_power') | float }}"
```

---

*This guide is based on Home Assistant 2025.10.0 energy management documentation and best practices.*
