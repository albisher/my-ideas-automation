# DCS-8000LH AI Features Setup Guide

## Overview

This guide provides detailed instructions for adding AI features to your DCS-8000LH camera using Frigate NVR and other open source solutions.

## 🤖 **AI Features Available**

### **Core AI Capabilities**
- **Person Detection**: Identify people in video streams
- **Motion Detection**: Detect movement and activity
- **Object Recognition**: Identify cars, bicycles, animals
- **Face Recognition**: Recognize known faces
- **License Plate Detection**: Read license plates
- **Line Crossing Detection**: Monitor boundary crossings

### **Advanced Features**
- **Custom Object Detection**: Train for specific objects
- **Behavioral Analysis**: Analyze movement patterns
- **Event Correlation**: Link related events
- **Smart Alerts**: Intelligent notification system

## 🛠️ **Installation Methods**

### **Method 1: Docker Installation (Recommended)**

#### **1.1 Install Docker**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

#### **1.2 Create Frigate Configuration**
```bash
# Create directories
mkdir -p /opt/frigate/config
mkdir -p /opt/frigate/recordings
mkdir -p /opt/frigate/cache

# Create docker-compose.yml
cat > /opt/frigate/docker-compose.yml << EOF
version: "3.9"
services:
  frigate:
    container_name: frigate
    image: ghcr.io/blakeblackshear/frigate:stable
    restart: unless-stopped
    ports:
      - "5000:5000"
      - "8554:8554"
      - "8555:8555"
    volumes:
      - /opt/frigate/config:/config
      - /opt/frigate/recordings:/media/frigate/recordings
      - /opt/frigate/cache:/tmp/cache
    environment:
      - FRIGATE_RTSP_PASSWORD=your-password
    devices:
      - /dev/bus/usb:/dev/bus/usb
    shm_size: 64m
EOF
```

#### **1.3 Configure Frigate**
```yaml
# /opt/frigate/config/config.yml
mqtt:
  host: your-mqtt-broker
  port: 1883
  user: your-username
  password: your-password

detectors:
  cpu1:
    type: cpu
    num_threads: 3

cameras:
  dcs8000lh:
    ffmpeg:
      inputs:
        - path: rtsp://your-camera-ip:554/stream
          roles:
            - detect
            - record
    detect:
      width: 1280
      height: 720
      fps: 5
    objects:
      track:
        - person
        - car
        - bicycle
        - dog
        - cat
    motion:
      mask: 0,0,0,0,0,0,0,0
    record:
      enabled: true
      retain:
        days: 7
        mode: motion
```

### **Method 2: Home Assistant Add-on**

#### **2.1 Install Home Assistant**
```bash
# Install Home Assistant OS
# Follow official installation guide
```

#### **2.2 Add Frigate Add-on**
1. Go to Home Assistant → Supervisor → Add-on Store
2. Search for "Frigate"
3. Install and configure

#### **2.3 Configure Integration**
```yaml
# configuration.yaml
frigate:
  host: your-frigate-ip
  port: 5000
```

## 🔧 **Configuration Examples**

### **Basic Person Detection**
```yaml
# frigate.yml
cameras:
  dcs8000lh:
    ffmpeg:
      inputs:
        - path: rtsp://your-camera-ip:554/stream
          roles:
            - detect
    detect:
      width: 1280
      height: 720
      fps: 5
    objects:
      track:
        - person
      filters:
        person:
          min_area: 5000
          max_area: 100000
          min_score: 0.5
```

### **Advanced Motion Detection**
```yaml
# frigate.yml
cameras:
  dcs8000lh:
    motion:
      threshold: 25
      contour_area: 100
      delta_alpha: 0.2
      frame_alpha: 0.2
      frame_height: 180
    zones:
      front_door:
        coordinates: 0,0,0,0,0,0,0,0
        filters:
          person:
            min_area: 5000
            max_area: 100000
```

### **Face Recognition Setup**
```yaml
# frigate.yml
face_recognition:
  enabled: true
  model_path: /config/model
  face_recognition:
    enabled: true
    expire_after: 30
    save_unknown_faces: true
```

## 📊 **Monitoring and Alerts**

### **Frigate Web Interface**
- **URL**: `http://your-frigate-ip:5000`
- **Features**: Live view, event browser, configuration
- **Access**: Web-based interface for monitoring

### **Home Assistant Integration**
```yaml
# configuration.yaml
camera:
  - platform: generic
    name: DCS-8000LH Live
    stream_source: rtsp://your-camera-ip:554/stream

binary_sensor:
  - platform: mqtt
    name: "DCS-8000LH Person Detection"
    state_topic: "frigate/dcs8000lh/person"
    payload_on: "ON"
    payload_off: "OFF"

sensor:
  - platform: mqtt
    name: "DCS-8000LH Person Count"
    state_topic: "frigate/dcs8000lh/person"
    unit_of_measurement: "count"
```

### **Automation Examples**
```yaml
# automation.yaml
- alias: "Person Detected Alert"
  trigger:
    platform: state
    entity_id: binary_sensor.dcs8000lh_person_detection
    to: "on"
  action:
    - service: notify.mobile_app_your_phone
      data:
        title: "Person Detected"
        message: "A person was detected at the front door"

- alias: "Motion Recording"
  trigger:
    platform: state
    entity_id: binary_sensor.dcs8000lh_motion
    to: "on"
  action:
    - service: camera.record
      entity_id: camera.dcs8000lh_live
```

## 🔍 **Advanced AI Features**

### **Custom Object Detection**
```yaml
# frigate.yml
detectors:
  cpu1:
    type: cpu
    num_threads: 3
  custom:
    type: cpu
    model:
      path: /config/custom_model.pb
      width: 320
      height: 320
      input_tensor: input
      output_tensors: output

cameras:
  dcs8000lh:
    detect:
      enabled: true
      max_disappeared: 10
      stationary_interval: 10
    objects:
      track:
        - person
        - car
        - bicycle
        - dog
        - cat
        - custom_object
```

### **Behavioral Analysis**
```yaml
# frigate.yml
cameras:
  dcs8000lh:
    motion:
      threshold: 25
      contour_area: 100
      delta_alpha: 0.2
      frame_alpha: 0.2
      frame_height: 180
    zones:
      front_door:
        coordinates: 0,0,0,0,0,0,0,0
        filters:
          person:
            min_area: 5000
            max_area: 100000
      backyard:
        coordinates: 0,0,0,0,0,0,0,0
        filters:
          person:
            min_area: 5000
            max_area: 100000
```

## 📈 **Performance Optimization**

### **Hardware Requirements**
- **CPU**: Multi-core processor recommended
- **RAM**: 8GB+ recommended
- **Storage**: SSD for better performance
- **GPU**: Optional but recommended for better performance

### **Configuration Optimization**
```yaml
# frigate.yml
detectors:
  cpu1:
    type: cpu
    num_threads: 3
  gpu1:
    type: edgetpu
    device: usb

cameras:
  dcs8000lh:
    detect:
      width: 1280
      height: 720
      fps: 5
    motion:
      threshold: 25
      contour_area: 100
    record:
      enabled: true
      retain:
        days: 7
        mode: motion
```

### **Network Optimization**
- Use wired connections when possible
- Optimize video quality settings
- Configure proper network segmentation
- Monitor bandwidth usage

## 🛠️ **Troubleshooting**

### **Common Issues**
1. **AI Detection Not Working**: Check Frigate configuration
2. **High CPU Usage**: Optimize detection settings
3. **Network Issues**: Test RTSP stream manually
4. **Storage Issues**: Check disk space and permissions

### **Debug Commands**
```bash
# Check Frigate logs
docker logs frigate

# Test RTSP stream
ffplay rtsp://your-camera-ip:554/stream

# Check system resources
htop
df -h
```

### **Performance Monitoring**
```bash
# Monitor CPU usage
top -p $(pgrep frigate)

# Monitor memory usage
free -h

# Monitor disk usage
df -h /opt/frigate/recordings
```

## 📚 **Additional Resources**

### **Documentation**
- [Frigate Documentation](https://docs.frigate.video/)
- [Home Assistant Documentation](https://www.home-assistant.io/docs/)
- [Docker Documentation](https://docs.docker.com/)

### **Community Support**
- [Frigate Discord](https://discord.gg/frigate)
- [Home Assistant Community](https://community.home-assistant.io/)
- [GitHub Issues](https://github.com/blakeblackshear/frigate/issues)

## 🎉 **Expected Results**

After successful implementation, you will have:

- ✅ **Person Detection**: Automatic person identification
- ✅ **Motion Alerts**: Smart motion detection
- ✅ **Object Recognition**: Identify various objects
- ✅ **Face Recognition**: Recognize known faces
- ✅ **Smart Recording**: Event-based recording
- ✅ **Advanced Analytics**: Behavioral analysis
- ✅ **Custom Alerts**: Intelligent notifications
- ✅ **Performance Monitoring**: System optimization

This setup provides comprehensive AI features for your DCS-8000LH camera, transforming it into a smart surveillance system with advanced capabilities.
