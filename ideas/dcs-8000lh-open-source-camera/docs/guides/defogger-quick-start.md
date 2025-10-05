# DCS-8000LH Defogger Quick Start Guide

## Quick Setup (5 Minutes)

### 1. Prerequisites Check
```bash
# Install dependencies
sudo apt-get update
sudo apt-get install python3-pip squashfs-tools
pip3 install bluepy

# Check Bluetooth
hciconfig
```

### 2. Get Camera Information
From your camera label:
- **MAC**: `B0:C5:54:AA:BB:CC` (format with colons)
- **PIN**: `123456` (6-digit code)
- **WiFi**: Your network name and password

### 3. Run Automated Setup
```bash
cd /Users/amac/myIdeas/ideas/dcs-8000lh-open-source-camera/scripts

# Edit the script with your details
nano defogger-setup.sh

# Run the automated setup
./defogger-setup.sh
```

### 4. Test Streaming
```bash
# Test HTTP stream
vlc http://CAMERA_IP/video/mpegts.cgi

# Test RTSP stream  
vlc rtsp://CAMERA_IP/live/profile.0
```

## Manual Setup (If Automated Fails)

### Step 1: Bluetooth Configuration
```bash
# Test connection
python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --survey

# Configure WiFi
python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --essid YourWiFi --wifipw YourPassword

# Enable services
python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --lighttpd
python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --unsignedfw
python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --telnetd
python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --rtsp
```

### Step 2: Build and Flash Firmware
```bash
# Build custom firmware
make

# Flash firmware
curl --http1.0 -u admin:123456 --form upload=@fw.tar http://CAMERA_IP/config/firmwareupgrade.cgi
```

## Expected Results

✅ **Local Streaming**: HTTP/HTTPS/RTSP without cloud dependency  
✅ **API Access**: Full camera control via NIPCA API  
✅ **Home Assistant**: Direct integration support  
✅ **Frigate NVR**: AI motion detection support  

## Troubleshooting

### Bluetooth Issues
```bash
sudo systemctl restart bluetooth
sudo hciconfig hci0 up
```

### Network Issues
```bash
# Check camera IP
python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --netconf

# Test connectivity
ping CAMERA_IP
```

### Streaming Issues
```bash
# Check RTSP status
curl -u admin:123456 http://CAMERA_IP/config/rtspurl.cgi?profileid=1

# Restart RTSP
python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --rtsp
```

## Integration Examples

### Home Assistant
```yaml
camera:
  - platform: generic
    stream_source: rtsp://CAMERA_IP/live/profile.0
    name: DCS-8000LH
    authentication: basic
    username: admin
    password: 123456
```

### Frigate NVR
```yaml
cameras:
  dcs_8000lh:
    ffmpeg:
      inputs:
        - path: rtsp://CAMERA_IP/live/profile.0
          roles: [detect, record]
    detect:
      width: 1280
      height: 720
      fps: 5
```

## Security Notes

⚠️ **Change default password**: `python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --command "tdb set HTTPAccount AdminPasswd_ss='newpassword'"`

⚠️ **Enable HTTPS**: `python3 dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --command "tdb set HTTPServer Enable_byte=1"`

## Support

- **Full Guide**: `docs/guides/defogger-complete-setup.md`
- **Troubleshooting**: `docs/guides/troubleshooting.md`
- **Home Assistant**: `docs/guides/homeassistant-configuration-guide.md`
