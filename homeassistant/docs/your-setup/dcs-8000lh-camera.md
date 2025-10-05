# DCS-8000LH Camera System Documentation

This document covers your DCS-8000LH camera system integration with Home Assistant, including motion detection, object recognition, and automation setup.

## System Overview

The DCS-8000LH is a security camera system integrated with Home Assistant through MQTT and Frigate NVR for advanced video analysis and object detection.

## Camera Configuration

### Basic Camera Setup
- **Camera Name:** DCS-8000LH Camera
- **Stream Source:** `rtsp://admin:admin@192.168.68.100:554/stream1`
- **Still Image URL:** `http://192.168.68.100/image.jpg`
- **SSL Verification:** Disabled
- **Platform:** Generic camera

### Network Configuration
- **IP Address:** 192.168.68.100
- **Port:** 554 (RTSP)
- **Username:** admin
- **Password:** admin
- **Protocol:** RTSP

## Motion Detection System

### Motion Sensors
Your system has multiple motion detection sensors:

#### Primary Motion Sensor
- **Entity:** `binary_sensor.dcs_8000lh_motion`
- **Device Class:** motion
- **State Topic:** `frigate/dcs8000lh/motion`
- **Payload On:** "ON"
- **Payload Off:** "OFF"
- **Status:** Active

#### Additional Motion Sensors
- **Entity:** `binary_sensor.dcs_8000lh_motion_1`
- **Entity:** `binary_sensor.dcs_8000lh_motion_2`
- **Purpose:** Multiple motion zones
- **Status:** Active

### MQTT Motion Sensors
- **Entity:** `binary_sensor.dcs_8000lh_motion_mqtt`
- **Purpose:** MQTT-based motion detection
- **Status:** Active

## Object Detection System

### Person Detection
Your system can detect and count people in the camera's field of view:

#### Primary Person Counter
- **Entity:** `sensor.dcs_8000lh_person_count`
- **State Topic:** `frigate/dcs8000lh/person`
- **Value Template:** `{{ value_json.count }}`
- **Unit:** people
- **Status:** Active

#### Additional Person Counters
- **Entity:** `sensor.dcs_8000lh_person_count_1`
- **Entity:** `sensor.dcs_8000lh_person_count_2`
- **Purpose:** Multiple detection zones
- **Status:** Active

### Car Detection
Your system can detect and count vehicles:

#### Primary Car Counter
- **Entity:** `sensor.dcs_8000lh_car_count`
- **State Topic:** `frigate/dcs8000lh/car`
- **Value Template:** `{{ value_json.count }}`
- **Unit:** cars
- **Status:** Active

#### Additional Car Counters
- **Entity:** `sensor.dcs_8000lh_car_count_1`
- **Entity:** `sensor.dcs_8000lh_car_count_2`
- **Purpose:** Multiple detection zones
- **Status:** Active

### Raw Motion Data
- **Entity:** `sensor.dcs_8000lh_motion_raw`
- **Purpose:** Raw motion detection data
- **Status:** Active

## MQTT Integration

### MQTT Topics
Your system uses the following MQTT topics:

#### Motion Detection
- **Topic:** `frigate/dcs8000lh/motion`
- **Payload:** "ON" / "OFF"
- **Purpose:** Motion state changes

#### Object Detection
- **Person Topic:** `frigate/dcs8000lh/person`
- **Car Topic:** `frigate/dcs8000lh/car`
- **Format:** JSON with count data
- **Purpose:** Object counting

### MQTT Configuration
- **Broker:** localhost
- **Port:** 1883
- **Username:** frigate
- **Password:** frigate_password

## Frigate NVR Integration

### Frigate Configuration
- **Host:** http://localhost:5000
- **MQTT Host:** localhost
- **MQTT Port:** 1883
- **MQTT Username:** frigate
- **MQTT Password:** frigate_password

### Video Analysis
Frigate provides:
- Real-time object detection
- Motion detection
- Video recording
- Event storage
- MQTT integration

## Dashboard Integration

### Camera Card
Your dashboard includes a camera card showing:
- **Entity:** `camera.dcs_8000lh_camera`
- **Name:** "DCS-8000LH Live Feed"
- **Type:** Live video stream

### Motion Detection Card
Shows current motion status:
- Motion sensor states
- Person count
- Car count

### MQTT Status Card
Displays MQTT communication status:
- MQTT motion sensors
- MQTT person counters
- MQTT car counters

## Automations

### Motion Detection Automations
Your system has several motion-related automations:

#### DCS-8000LH Motion Detected
- **Entity:** `automation.dcs_8000lh_motion_detected`
- **Purpose:** Respond to motion detection
- **Status:** Active

#### DCS-8000LH Person Detected
- **Entity:** `automation.dcs_8000lh_person_detected`
- **Purpose:** Respond to person detection
- **Status:** Active

#### DCS-8000LH Car Detected
- **Entity:** `automation.dcs_8000lh_car_detected`
- **Purpose:** Respond to car detection
- **Status:** Active

### General Motion Automations
- **Motion Detection Alert:** `automation.motion_detection_alert`
- **Person Detection Alert:** `automation.person_detection_alert`
- **Car Detection Alert:** `automation.car_detection_alert`

## Scripts

### Camera Management Scripts
- **Take Camera Snapshot:** `script.take_camera_snapshot`
- **Restart Frigate:** `script.restart_frigate`
- **Motion Alert:** `script.motion_alert`
- **Test MQTT:** `script.test_mqtt`

## Voice Assistant Integration

### Exposed Entities
The following motion sensors are exposed to voice assistant:
- `binary_sensor.dcs_8000lh_motion`
- `binary_sensor.dcs_8000lh_motion_1`
- `binary_sensor.dcs_8000lh_motion_2`

### Voice Commands
You can use voice commands like:
- "Is there motion detected?"
- "How many people are detected?"
- "Show me the camera"

## Troubleshooting

### Common Issues

#### Camera Connection
- **Issue:** Camera not accessible
- **Check:** Network connectivity to 192.168.68.100
- **Verify:** RTSP stream is working
- **Test:** Access camera directly via browser

#### Motion Detection Not Working
- **Check:** MQTT broker connection
- **Verify:** Frigate is running
- **Test:** MQTT topics are publishing

#### Object Detection Issues
- **Check:** Frigate configuration
- **Verify:** Model is loaded correctly
- **Test:** Object detection in Frigate UI

### Logs and Debugging
- **Home Assistant Logs:** Check for camera-related errors
- **Frigate Logs:** Check for detection issues
- **MQTT Logs:** Verify message flow

### Performance Optimization
- **Stream Quality:** Adjust resolution if needed
- **Detection Sensitivity:** Tune Frigate settings
- **Storage:** Monitor disk usage for recordings

## Security Considerations

### Network Security
- **RTSP Stream:** Unencrypted (consider VPN)
- **MQTT:** Local network only
- **Camera Access:** Change default credentials

### Privacy
- **Recording:** Local storage only
- **Data Sharing:** No external sharing configured
- **Retention:** Configure appropriate retention periods

## Maintenance

### Regular Tasks
1. **Check Camera Status:** Verify camera is online
2. **Review Detections:** Check motion and object detection
3. **Clean Storage:** Manage recorded footage
4. **Update Firmware:** Keep camera firmware updated

### Monitoring
- **Motion Events:** Review motion detection logs
- **Object Detection:** Monitor detection accuracy
- **System Performance:** Check CPU and memory usage

---

*This documentation is specific to your DCS-8000LH camera system integration.*
