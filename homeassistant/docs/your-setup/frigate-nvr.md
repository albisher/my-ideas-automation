# Frigate NVR Integration Documentation

This document covers your Frigate NVR (Network Video Recorder) integration with Home Assistant, including video recording, object detection, and MQTT communication.

## Frigate Overview

Frigate is an open-source NVR that provides real-time object detection for IP cameras. It integrates with Home Assistant to provide advanced video analysis and recording capabilities.

## Current Configuration

### Frigate Settings
Your Frigate is configured with the following settings:

```yaml
# Frigate configuration
frigate:
  host: http://localhost:5000
  mqtt_host: localhost
  mqtt_port: 1883
  mqtt_username: frigate
  mqtt_password: frigate_password
```

### Network Configuration
- **Frigate Host:** localhost:5000
- **MQTT Broker:** localhost:1883
- **MQTT Username:** frigate
- **MQTT Password:** frigate_password

## Camera Integration

### DCS-8000LH Camera
Your DCS-8000LH camera is integrated with Frigate:

- **Camera Name:** dcs8000lh
- **RTSP Stream:** rtsp://admin:admin@192.168.68.100:554/stream1
- **Detection:** Motion and object detection enabled
- **Recording:** Continuous recording enabled

### Stream Configuration
- **Input Stream:** RTSP from DCS-8000LH
- **Output Stream:** Available via Home Assistant
- **Resolution:** As per camera settings
- **Frame Rate:** As per camera settings

## Object Detection

### Supported Objects
Frigate can detect various objects:
- **Person:** Human detection
- **Car:** Vehicle detection
- **Motion:** General motion detection
- **Custom Objects:** Additional trained models

### Detection Configuration
Your system is configured to detect:
- **Person Detection:** Enabled with counting
- **Car Detection:** Enabled with counting
- **Motion Detection:** Enabled for all areas

### MQTT Topics
Frigate publishes detection data to MQTT:

#### Motion Detection
- **Topic:** `frigate/dcs8000lh/motion`
- **Payload:** "ON" / "OFF"
- **Purpose:** Motion state changes

#### Person Detection
- **Topic:** `frigate/dcs8000lh/person`
- **Payload:** JSON with count data
- **Format:** `{"count": 2}`
- **Purpose:** Person counting

#### Car Detection
- **Topic:** `frigate/dcs8000lh/car`
- **Payload:** JSON with count data
- **Format:** `{"count": 1}`
- **Purpose:** Car counting

## Home Assistant Integration

### Entities Created
Frigate creates several entities in Home Assistant:

#### Motion Sensors
- `binary_sensor.dcs_8000lh_motion` - Main motion sensor
- `binary_sensor.dcs_8000lh_motion_1` - Motion zone 1
- `binary_sensor.dcs_8000lh_motion_2` - Motion zone 2

#### Object Counters
- `sensor.dcs_8000lh_person_count` - Person count
- `sensor.dcs_8000lh_car_count` - Car count
- `sensor.dcs_8000lh_person_count_1` - Person count zone 1
- `sensor.dcs_8000lh_person_count_2` - Person count zone 2
- `sensor.dcs_8000lh_car_count_1` - Car count zone 1
- `sensor.dcs_8000lh_car_count_2` - Car count zone 2

#### Raw Data
- `sensor.dcs_8000lh_motion_raw` - Raw motion data

### Camera Entity
- `camera.dcs_8000lh_camera` - Live camera feed
- **Stream Source:** From Frigate
- **Still Image:** Available
- **Recording:** Continuous

## Recording and Storage

### Recording Configuration
- **Mode:** Continuous recording
- **Retention:** Configurable (default: 7 days)
- **Format:** MP4
- **Quality:** As per camera settings

### Event Recording
- **Motion Events:** Recorded when motion detected
- **Object Events:** Recorded when objects detected
- **Pre-buffer:** Configurable pre-event recording
- **Post-buffer:** Configurable post-event recording

### Storage Management
- **Local Storage:** Recordings stored locally
- **Cleanup:** Automatic cleanup of old recordings
- **Backup:** Manual backup options available

## Automation Integration

### Motion-Based Automations
Your system has several motion-based automations:

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

#### Person Detection
```yaml
automation:
  - alias: "DCS-8000LH Person Detected"
    trigger:
      - platform: state
        entity_id: sensor.dcs_8000lh_person_count
        to: '1'
    action:
      - service: notify.mobile_app
        data:
          message: "Person detected in camera view"
```

#### Car Detection
```yaml
automation:
  - alias: "DCS-8000LH Car Detected"
    trigger:
      - platform: state
        entity_id: sensor.dcs_8000lh_car_count
        to: '1'
    action:
      - service: notify.mobile_app
        data:
          message: "Vehicle detected in camera view"
```

## Dashboard Integration

### Camera Card
Your dashboard includes a camera card:
```yaml
type: camera
entity: camera.dcs_8000lh_camera
name: "DCS-8000LH Live Feed"
```

### Motion Detection Card
```yaml
type: entities
title: "Motion Detection"
entities:
  - binary_sensor.dcs_8000lh_motion
  - sensor.dcs_8000lh_person_count
  - sensor.dcs_8000lh_car_count
```

### MQTT Status Card
```yaml
type: entities
title: "MQTT Status"
entities:
  - binary_sensor.dcs_8000lh_motion_mqtt
  - sensor.dcs_8000lh_person_count_mqtt
  - sensor.dcs_8000lh_car_count_mqtt
```

## Scripts and Services

### Available Scripts
- `script.take_camera_snapshot` - Take a snapshot
- `script.restart_frigate` - Restart Frigate service
- `script.motion_alert` - Motion alert script
- `script.test_mqtt` - Test MQTT connection

### Frigate Services
- `frigate.get_events` - Get recorded events
- `frigate.get_snapshots` - Get snapshots
- `frigate.get_clips` - Get video clips

## Performance Optimization

### System Requirements
- **CPU:** Multi-core recommended for object detection
- **RAM:** 4GB+ recommended
- **Storage:** SSD recommended for recording
- **GPU:** Optional for faster detection

### Configuration Tuning
- **Detection Sensitivity:** Adjust for your environment
- **Recording Quality:** Balance quality vs. storage
- **Retention Period:** Set appropriate retention
- **Motion Zones:** Configure detection areas

## Troubleshooting

### Common Issues

#### Frigate Not Starting
- **Check Ports:** Ensure port 5000 is available
- **Check Dependencies:** Verify all dependencies installed
- **Check Logs:** Review Frigate logs for errors

#### Detection Not Working
- **Check Camera Stream:** Verify RTSP stream is working
- **Check Model:** Ensure detection model is loaded
- **Check Configuration:** Verify Frigate configuration

#### MQTT Issues
- **Check Broker:** Verify MQTT broker is running
- **Check Credentials:** Verify MQTT username/password
- **Check Topics:** Verify topics are publishing

### Debug Steps
1. **Check Frigate Logs:** Review Frigate container logs
2. **Test Camera Stream:** Access camera directly
3. **Test MQTT:** Use MQTT client to test topics
4. **Check Home Assistant Logs:** Look for integration errors

## Security Considerations

### Network Security
- **RTSP Stream:** Consider VPN for remote access
- **MQTT:** Use secure MQTT if needed
- **Local Network:** Keep on secure network

### Privacy
- **Local Processing:** All processing is local
- **No Cloud:** No data sent to external services
- **Retention:** Configure appropriate retention

## Maintenance

### Regular Tasks
1. **Check Recording Status:** Verify recordings are working
2. **Review Detection Accuracy:** Check detection performance
3. **Clean Storage:** Manage disk space
4. **Update Frigate:** Keep Frigate updated

### Monitoring
- **CPU Usage:** Monitor detection performance
- **Storage Usage:** Monitor disk space
- **Detection Events:** Review detection logs
- **System Health:** Check overall system status

---

*This documentation covers Frigate NVR integration specific to your Home Assistant setup.*
