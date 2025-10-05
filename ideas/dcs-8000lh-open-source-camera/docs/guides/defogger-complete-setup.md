# DCS-8000LH Defogger Complete Setup Guide

## Overview

This guide provides a complete step-by-step process to use the defogger method to enable local streaming on your DCS-8000LH camera. The defogger project by Bjørn Mork allows you to bypass D-Link's cloud services and enable direct local streaming.

## Prerequisites

### Hardware Requirements
- DCS-8000LH camera with firmware v2.01.03 or v2.02.02
- Linux PC with Bluetooth controller
- WiFi network with WPA2-PSK
- USB TTL adapter (3.3V) for serial console access (optional)

### Software Requirements
- Python 3.x
- bluepy library for Bluetooth LE communication
- squashfs-tools package
- TFTP server or web server for backups

## Step 1: Environment Setup

### Install Dependencies
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-pip squashfs-tools tftp

# Install Python dependencies
pip3 install bluepy
```

### Verify Bluetooth
```bash
# Check if Bluetooth is working
hciconfig
bluetoothctl show
```

## Step 2: Camera Information

### Get Camera Details
From your camera label, you need:
- **MAC Address**: Format as `B0:C5:54:AA:BB:CC` (not `B0C554AABBCC`)
- **PIN Code**: 6-digit code from camera label
- **WiFi Network**: Your network name and password

### Example Camera Label
```
MAC: B0:C5:54:AA:BB:CC
PIN: 123456
```

## Step 3: Bluetooth Configuration

### Basic Connection Test
```bash
cd /Users/amac/myIdeas/ideas/dcs-8000lh-open-source-camera/scripts
python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --survey
```

### Configure WiFi Network
```bash
# Connect camera to your WiFi
python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --essid YourWiFiName --wifipw YourWiFiPassword
```

### Verify Network Connection
```bash
# Check if camera connected to WiFi
python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --netconf
```

### Enable HTTP Server
```bash
# Enable web server on camera
python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --lighttpd
```

### Disable Firmware Signature Verification
```bash
# Allow unsigned firmware
python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --unsignedfw
```

### Enable Telnet Access
```bash
# Enable telnet server
python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --telnetd
```

### Enable RTSP Streaming
```bash
# Enable RTSP server
python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --rtsp
```

## Step 4: Build Custom Firmware

### Create Enhanced Firmware
```bash
cd /Users/amac/myIdeas/ideas/dcs-8000lh-open-source-camera/scripts

# Build custom firmware
make
```

This creates `fw.tar` with enhanced streaming capabilities.

## Step 5: Flash Custom Firmware

### Upload and Flash Firmware
```bash
# Get camera IP from network configuration
CAMERA_IP="192.168.1.100"  # Replace with actual IP

# Flash custom firmware
curl --http1.0 -u admin:123456 --form upload=@fw.tar http://$CAMERA_IP/config/firmwareupgrade.cgi
```

The camera will reboot automatically after successful upload.

## Step 6: Verify Streaming

### Test HTTP Streaming
```bash
# Test MPEG-TS stream
vlc http://$CAMERA_IP/video/mpegts.cgi

# Test FLV stream
vlc http://$CAMERA_IP/video/flv.cgi
```

### Test RTSP Streaming
```bash
# Get RTSP URL
curl -u admin:123456 --insecure "https://$CAMERA_IP/config/rtspurl.cgi?profileid=1"

# Connect to RTSP stream
vlc rtsp://$CAMERA_IP/live/profile.0
```

### Test NIPCA API
```bash
# Get camera info
curl -u admin:123456 http://$CAMERA_IP/common/info.cgi

# Control LED
curl -u admin:123456 http://$CAMERA_IP/config/led.cgi?led=off
```

## Step 7: Integration with Home Assistant

### Configure Home Assistant
Add to your `configuration.yaml`:

```yaml
camera:
  - platform: generic
    stream_source: rtsp://192.168.1.100/live/profile.0
    name: DCS-8000LH Camera
    authentication: basic
    username: admin
    password: 123456

  - platform: generic
    stream_source: http://192.168.1.100/video/mpegts.cgi
    name: DCS-8000LH HTTP Stream
    authentication: basic
    username: admin
    password: 123456
```

### Configure Frigate NVR
Add to your `frigate/config/config.yml`:

```yaml
cameras:
  dcs_8000lh:
    ffmpeg:
      inputs:
        - path: rtsp://192.168.1.100/live/profile.0
          roles:
            - detect
            - record
    detect:
      width: 1280
      height: 720
      fps: 5
```

## Step 8: Troubleshooting

### Common Issues

#### Bluetooth Connection Failed
```bash
# Check Bluetooth status
sudo systemctl status bluetooth
sudo hciconfig hci0 up

# Reset Bluetooth
sudo systemctl restart bluetooth
```

#### Firmware Upload Failed
```bash
# Check camera web server
curl -I http://$CAMERA_IP/config/firmwareupgrade.cgi

# Verify authentication
curl -u admin:123456 http://$CAMERA_IP/common/info.cgi
```

#### Streaming Not Working
```bash
# Check RTSP settings
curl -u admin:123456 http://$CAMERA_IP/config/rtspurl.cgi?profileid=1

# Restart RTSP server
python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --rtsp
```

### Recovery Methods

#### Serial Console Access
If the camera becomes unresponsive:

1. **Locate Serial Header**: Remove bottom label to reveal 4-pin header
2. **Connect TTL Adapter**: 
   - Pin 1: 3.3V (don't connect)
   - Pin 2: TX
   - Pin 3: RX  
   - Pin 4: GND
3. **Serial Parameters**: 57600 8N1
4. **U-Boot Access**: Press ESC during boot, enter password `alpha168`
5. **Root Shell**: 
   ```bash
   setenv bootargs ${bootargs} init=/bin/sh
   bootm 0xbc1e0000
   ```

#### Factory Reset
Hold the reset button for 10 seconds to restore factory settings.

## Step 9: Advanced Configuration

### Custom Streaming Settings
```bash
# Access camera via telnet
telnet $CAMERA_IP

# Configure video settings
tdb set Video Width_byte=1280
tdb set Video Height_byte=720
tdb set Video FPS_byte=30
```

### Backup Camera Configuration
```bash
# Create backup
python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --sysinfo > camera_backup.txt
```

## Security Considerations

### Change Default Passwords
```bash
# Change admin password
python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --command "tdb set HTTPAccount AdminPasswd_ss='newpassword'"
```

### Enable HTTPS
```bash
# Enable HTTPS server
python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --command "tdb set HTTPServer Enable_byte=1"
```

## Expected Results

After successful defogger implementation:

✅ **Local HTTP/HTTPS Streaming**: Direct video access without cloud dependency  
✅ **RTSP Streaming**: Standard RTSP protocol support  
✅ **NIPCA API**: Full camera control via HTTP API  
✅ **Telnet Access**: Direct shell access for advanced configuration  
✅ **Home Assistant Integration**: Seamless integration with HA  
✅ **Frigate NVR Support**: AI-powered motion detection  

## Troubleshooting Commands

```bash
# Check camera status
python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --sysinfo

# Test network connectivity
ping $CAMERA_IP

# Check streaming endpoints
curl -I http://$CAMERA_IP/video/mpegts.cgi
curl -I http://$CAMERA_IP/video/flv.cgi

# Verify RTSP
ffprobe rtsp://$CAMERA_IP/live/profile.0
```

## Support and Resources

- **Defogger Repository**: https://github.com/bmork/defogger
- **D-Link Forums**: https://forums.dlink.com/
- **Home Assistant Community**: https://community.home-assistant.io/

## Warning

⚠️ **Modifying firmware carries risks including device bricking**  
⚠️ **Always backup your camera configuration before proceeding**  
⚠️ **This process voids the manufacturer warranty**  
⚠️ **Proceed at your own risk**
