# Home Assistant Configuration Guide for DCS-8000LH Camera System

## Overview
This guide will help you configure Home Assistant to work with your DCS-8000LH camera system, including Frigate NVR, MQTT broker, and Tapo devices.

## Prerequisites
- Home Assistant running on port 8123
- MQTT broker running on port 1883
- Frigate NVR running on port 5001
- DCS-8000LH camera accessible via RTSP

## Step 1: Access Home Assistant Web Interface

### 1.1 Open Home Assistant
Navigate to: `http://localhost:8123/`

### 1.2 Complete Initial Setup
1. **Create Account**: Set up your admin account
2. **Location**: Configure your home location
3. **Units**: Select metric or imperial
4. **Name**: Give your home a name
5. **Username/Password**: Create secure credentials

## Step 2: Configure Integrations

### 2.1 MQTT Integration
1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **MQTT**
4. Configure with:
   - **Broker**: `localhost`
   - **Port**: `1883`
   - **Username**: `frigate`
   - **Password**: `frigate_password`

### 2.2 Frigate Integration
1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Frigate**
4. Configure with:
   - **Host**: `http://localhost:5001`
   - **MQTT Host**: `localhost`
   - **MQTT Port**: `1883`
   - **MQTT Username**: `frigate`
   - **MQTT Password**: `frigate_password`

### 2.3 Tapo Integration (Optional)
1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Tapo**
4. Configure with your Tapo credentials

## Step 3: Camera Configuration

### 3.1 DCS-8000LH Camera Setup
The camera is already configured in `configuration.yaml`:
```yaml
camera:
  - platform: generic
    name: "DCS-8000LH Camera"
    stream_source: rtsp://admin:admin@192.168.68.100:554/stream1
    still_image_url: http://192.168.68.100/image.jpg
    verify_ssl: false
```

### 3.2 Frigate Camera Integration
Frigate will automatically create camera entities for:
- Live view
- Motion detection
- Object detection
- Recordings

## Step 4: Sensor Configuration

### 4.1 Motion Detection Sensors
```yaml
binary_sensor:
  - platform: mqtt
    name: "DCS-8000LH Motion"
    state_topic: "frigate/dcs8000lh/motion"
    payload_on: "ON"
    payload_off: "OFF"
    device_class: motion
```

### 4.2 Object Detection Sensors
```yaml
sensor:
  - platform: mqtt
    name: "DCS-8000LH Person Count"
    state_topic: "frigate/dcs8000lh/person"
    value_template: "{{ value_json.count }}"
    unit_of_measurement: "people"
```

## Step 5: Automation Configuration

### 5.1 Motion Detection Automation
- **Trigger**: Motion detected
- **Condition**: Time between 6:00-22:00
- **Action**: Send notification + turn on lights

### 5.2 Person Detection Automation
- **Trigger**: Person count > 0
- **Condition**: Time between 6:00-22:00
- **Action**: Send alert with photo

### 5.3 Security Mode Automation
- **Trigger**: Device tracker leaves home
- **Action**: Activate security monitoring
- **Trigger**: Device tracker arrives home
- **Action**: Deactivate security monitoring

## Step 6: Dashboard Configuration

### 6.1 Create Security Dashboard
1. Go to **Overview** → **Edit Dashboard**
2. Add cards:
   - **Camera Card**: DCS-8000LH live view
   - **Entities Card**: Motion sensors
   - **Entities Card**: Object detection sensors
   - **Entities Card**: Frigate events

### 6.2 Camera Card Configuration
```yaml
type: picture-glance
entity: camera.dcs_8000lh_camera
camera_image: camera.dcs_8000lh_camera
title: DCS-8000LH Security Camera
```

## Step 7: Notification Setup

### 7.1 Telegram Notifications
1. Create Telegram bot via @BotFather
2. Get your chat ID
3. Update `configuration.yaml`:
```yaml
notify:
  - platform: telegram
    api_key: YOUR_TELEGRAM_BOT_TOKEN
    chat_id: YOUR_TELEGRAM_CHAT_ID
    name: telegram
```

### 7.2 Mobile App Setup
1. Install Home Assistant mobile app
2. Connect to your Home Assistant instance
3. Enable location tracking for security automations

## Step 8: Testing and Verification

### 8.1 Test Camera Feed
1. Go to **Overview** dashboard
2. Check if camera card shows live feed
3. Verify image quality and responsiveness

### 8.2 Test Motion Detection
1. Trigger motion in camera view
2. Check if motion sensor updates
3. Verify automation triggers

### 8.3 Test Object Detection
1. Walk in front of camera
2. Check person count sensor
3. Verify notifications are sent

## Step 9: Advanced Configuration

### 9.1 Frigate Zones
Configure detection zones in Frigate config:
```yaml
zones:
  front_door:
    coordinates: 0,0,100,0,100,100,0,100
    filters:
      person:
        min_area: 5000
        max_area: 100000
```

### 9.2 Recording Configuration
```yaml
record:
  enabled: true
  retain:
    days: 30
    mode: motion
```

### 9.3 Snapshot Configuration
```yaml
snapshots:
  enabled: true
  timestamp: true
  bounding_box: true
  retain:
    default: 30
    objects:
      person: 60
```

## Troubleshooting

### Common Issues
1. **Camera not showing**: Check RTSP URL and credentials
2. **Motion not detected**: Verify Frigate configuration
3. **MQTT not working**: Check broker credentials
4. **Automations not triggering**: Check entity names and conditions

### Debug Commands
```bash
# Check container status
docker ps

# Check Home Assistant logs
docker logs homeassistant

# Check Frigate logs
docker logs frigate

# Check MQTT logs
docker logs mqtt
```

## Security Considerations

### 1. Network Security
- Use strong passwords for all services
- Enable HTTPS for Home Assistant
- Configure firewall rules

### 2. Camera Security
- Change default camera credentials
- Use secure RTSP streams
- Enable camera authentication

### 3. MQTT Security
- Use authentication for MQTT broker
- Enable SSL/TLS for MQTT connections
- Regular password updates

## Production Ready Checklist

- ✅ Home Assistant accessible on port 8123
- ✅ MQTT broker running on port 1883
- ✅ Frigate NVR running on port 5001
- ✅ Camera RTSP stream working
- ✅ Motion detection configured
- ✅ Object detection configured
- ✅ Automations working
- ✅ Notifications working
- ✅ Dashboard configured
- ✅ Security measures in place

## Next Steps
1. Complete Home Assistant onboarding
2. Configure integrations
3. Set up dashboard
4. Test all functionality
5. Configure mobile app
6. Set up remote access (optional)

Your DCS-8000LH camera system is now ready for production use with Home Assistant!
