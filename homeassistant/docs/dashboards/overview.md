# Dashboard Overview

This guide covers your Home Assistant dashboard configuration, including views, cards, and customization options.

## Your Dashboard Configuration

### Main Dashboard (ui-lovelace.yaml)
Your primary dashboard is configured with the following structure:

```yaml
title: DCS-8000LH Camera System
views:
  - title: Overview
    path: default
    cards:
      - type: vertical-stack
        title: Camera System
        cards:
          - type: camera
            entity: camera.dcs_8000lh_camera
            name: "DCS-8000LH Live Feed"
            
          - type: entities
            title: Motion Detection
            entities:
              - binary_sensor.dcs_8000lh_motion
              - sensor.dcs_8000lh_person_count
              - sensor.dcs_8000lh_car_count
              
          - type: entities
            title: MQTT Status
            entities:
              - binary_sensor.dcs_8000lh_motion_mqtt
              - sensor.dcs_8000lh_person_count_mqtt
              - sensor.dcs_8000lh_car_count_mqtt
```

### Additional Dashboards
- **Map Dashboard** - Geographic view with map integration
- **Custom Dashboards** - Additional views can be created

## Dashboard Views

### Overview View
Your main dashboard view includes:

#### Camera System Section
- **Live Camera Feed** - Real-time video from DCS-8000LH
- **Motion Detection** - Current motion sensor status
- **Object Detection** - Person and car counts
- **MQTT Status** - Communication status

#### Card Organization
- **Vertical Stack** - Organizes multiple cards vertically
- **Entities Cards** - Groups related entities
- **Camera Card** - Live video stream

### Map View
- **Geographic Display** - Shows your home location
- **Device Locations** - Displays device positions
- **Zone Visualization** - Shows defined areas

## Card Types in Your Dashboard

### Camera Card
```yaml
type: camera
entity: camera.dcs_8000lh_camera
name: "DCS-8000LH Live Feed"
```
- **Purpose:** Live video streaming
- **Features:** Play/pause, fullscreen, snapshot
- **Integration:** Frigate NVR

### Entities Card
```yaml
type: entities
title: "Motion Detection"
entities:
  - binary_sensor.dcs_8000lh_motion
  - sensor.dcs_8000lh_person_count
  - sensor.dcs_8000lh_car_count
```
- **Purpose:** Display multiple related entities
- **Features:** Toggle controls, state display
- **Customization:** Icons, names, grouping

### Vertical Stack Card
```yaml
type: vertical-stack
title: Camera System
cards:
  - # Multiple cards stacked vertically
```
- **Purpose:** Organize multiple cards vertically
- **Features:** Automatic spacing, responsive layout
- **Use Case:** Grouping related functionality

## Dashboard Customization

### Adding New Cards

#### Light Control Card
```yaml
type: light
entity: light.living_room
name: "Living Room Light"
```

#### Switch Control Card
```yaml
type: entities
title: "Smart Plugs"
entities:
  - switch.tapo_living_room_plug
  - switch.tapo_kitchen_plug
```

#### Sensor Display Card
```yaml
type: sensor
entity: sensor.temperature
name: "Temperature"
```

#### Weather Card
```yaml
type: weather-forecast
entity: weather.forecast_home
```

### Creating New Views

#### Security View
```yaml
views:
  - title: Security
    path: security
    cards:
      - type: camera
        entity: camera.dcs_8000lh_camera
      - type: entities
        title: "Security Sensors"
        entities:
          - binary_sensor.dcs_8000lh_motion
          - binary_sensor.dcs_8000lh_motion_1
          - binary_sensor.dcs_8000lh_motion_2
```

#### Energy View
```yaml
views:
  - title: Energy
    path: energy
    cards:
      - type: entities
        title: "Power Consumption"
        entities:
          - sensor.tapo_plug_power
          - sensor.tapo_plug_energy_today
```

#### Automation View
```yaml
views:
  - title: Automations
    path: automations
    cards:
      - type: entities
        title: "Active Automations"
        entities:
          - automation.dcs_8000lh_motion_detected
          - automation.person_detection_alert
          - automation.car_detection_alert
```

## Advanced Card Types

### Conditional Card
```yaml
type: conditional
conditions:
  - entity: binary_sensor.dcs_8000lh_motion
    state: 'on'
card:
  type: entities
  title: "Motion Detected"
  entities:
    - sensor.dcs_8000lh_person_count
    - sensor.dcs_8000lh_car_count
```

### Glance Card
```yaml
type: glance
title: "Quick Controls"
entities:
  - entity: light.living_room
    name: "Living Room"
  - entity: switch.tapo_plug
    name: "Smart Plug"
```

### Picture Card
```yaml
type: picture
image: /local/images/home.jpg
tap_action:
  action: navigate
  navigation_path: /lovelace/security
```

### Markdown Card
```yaml
type: markdown
content: |
  # Welcome Home
  
  Current status:
  - Motion: {{ states('binary_sensor.dcs_8000lh_motion') }}
  - People: {{ states('sensor.dcs_8000lh_person_count') }}
  - Cars: {{ states('sensor.dcs_8000lh_car_count') }}
```

## Dashboard Themes

### Available Themes
- **Default** - Standard Home Assistant theme
- **Dark** - Dark mode theme
- **Light** - Light mode theme
- **Custom** - User-defined themes

### Theme Configuration
```yaml
# In configuration.yaml
frontend:
  themes: !include_dir_merge_named themes/
```

## Mobile Optimization

### Responsive Design
- **Mobile Layout** - Cards adapt to screen size
- **Touch Controls** - Optimized for touch interaction
- **Swipe Navigation** - Easy navigation between views

### Mobile App Features
- **Push Notifications** - Real-time alerts
- **Location Services** - GPS-based automations
- **Voice Control** - Voice assistant integration

## Dashboard Performance

### Optimization Tips
1. **Limit Card Count** - Don't overload views
2. **Use Conditional Cards** - Show only relevant content
3. **Optimize Images** - Compress images for faster loading
4. **Cache Resources** - Use local resources when possible

### Monitoring Performance
- **Load Times** - Monitor dashboard load times
- **Memory Usage** - Check browser memory usage
- **Network Requests** - Monitor API calls

## Troubleshooting

### Common Issues

#### Cards Not Displaying
- Check entity IDs
- Verify entity states
- Check card configuration syntax

#### Performance Issues
- Reduce card complexity
- Check for infinite loops
- Monitor system resources

#### Mobile Issues
- Check responsive design
- Test touch interactions
- Verify mobile app compatibility

### Debug Tools
- **Developer Tools** → **States**: Check entity states
- **Developer Tools** → **Services**: Test service calls
- **Browser DevTools**: Check for JavaScript errors
- **Network Tab**: Monitor API requests

## Best Practices

### Organization
1. **Logical Grouping** - Group related cards
2. **Clear Titles** - Use descriptive titles
3. **Consistent Layout** - Maintain consistent design
4. **User-Friendly** - Design for ease of use

### Performance
1. **Minimize Cards** - Use only necessary cards
2. **Optimize Images** - Compress images
3. **Cache Resources** - Use local resources
4. **Monitor Performance** - Regular performance checks

### Accessibility
1. **Clear Labels** - Use descriptive labels
2. **Color Contrast** - Ensure good contrast
3. **Touch Targets** - Adequate touch target sizes
4. **Screen Reader** - Support for assistive technologies

## Examples for Your Setup

### Enhanced Security Dashboard
```yaml
views:
  - title: Security
    path: security
    cards:
      - type: vertical-stack
        title: "Camera System"
        cards:
          - type: camera
            entity: camera.dcs_8000lh_camera
            name: "Live Feed"
          - type: entities
            title: "Motion Detection"
            entities:
              - binary_sensor.dcs_8000lh_motion
              - binary_sensor.dcs_8000lh_motion_1
              - binary_sensor.dcs_8000lh_motion_2
          - type: entities
            title: "Object Detection"
            entities:
              - sensor.dcs_8000lh_person_count
              - sensor.dcs_8000lh_car_count
```

### Energy Monitoring Dashboard
```yaml
views:
  - title: Energy
    path: energy
    cards:
      - type: entities
        title: "Power Consumption"
        entities:
          - sensor.tapo_plug_power
          - sensor.tapo_plug_energy_today
      - type: history-graph
        entities:
          - sensor.tapo_plug_power
        hours_to_show: 24
```

---

*This guide covers dashboard configuration specific to your Home Assistant setup.*
