# Your DCS-8000LH Camera Setup

## Your Camera Details
- **MAC Address**: `B0:C5:54:51:EB:76`
- **PIN Code**: `052446`
- **WiFi Network**: `SA`
- **WiFi Password**: `62Dad64Mom`

## Quick Start (Ready to Use)

### Option 1: Automated Setup
```bash
cd /Users/amac/myIdeas/ideas/dcs-8000lh-open-source-camera/scripts
./defogger-setup.sh
```

### Option 2: Interactive Commands
```bash
cd /Users/amac/myIdeas/ideas/dcs-8000lh-open-source-camera/scripts
./defogger-quick-commands.sh
```

### Option 3: Manual Commands
```bash
cd /Users/amac/myIdeas/ideas/dcs-8000lh-open-source-camera/scripts

# Test connection
python3 dcs8000lh-configure.py B0:C5:54:51:EB:76 052446 --survey

# Configure WiFi
python3 dcs8000lh-configure.py B0:C5:54:51:EB:76 052446 --essid SA --wifipw 62Dad64Mom

# Enable services
python3 dcs8000lh-configure.py B0:C5:54:51:EB:76 052446 --lighttpd
python3 dcs8000lh-configure.py B0:C5:54:51:EB:76 052446 --unsignedfw
python3 dcs8000lh-configure.py B0:C5:54:51:EB:76 052446 --telnetd
python3 dcs8000lh-configure.py B0:C5:54:51:EB:76 052446 --rtsp
```

## Expected Results

After successful setup, your camera will provide:

### Streaming Endpoints
- **HTTP MPEG-TS**: `http://CAMERA_IP/video/mpegts.cgi`
- **HTTP FLV**: `http://CAMERA_IP/video/flv.cgi`
- **RTSP**: `rtsp://CAMERA_IP/live/profile.0`

### API Endpoints
- **Camera Info**: `http://CAMERA_IP/common/info.cgi`
- **LED Control**: `http://CAMERA_IP/config/led.cgi?led=off`
- **Date/Time**: `http://CAMERA_IP/config/datetime.cgi`

### Access Credentials
- **Username**: `admin`
- **Password**: `052446` (your PIN code)

## Testing Commands

### Test HTTP Streaming
```bash
# Test MPEG-TS stream
vlc http://CAMERA_IP/video/mpegts.cgi

# Test FLV stream
vlc http://CAMERA_IP/video/flv.cgi
```

### Test RTSP Streaming
```bash
# Get RTSP URL
curl -u admin:052446 http://CAMERA_IP/config/rtspurl.cgi?profileid=1

# Connect to RTSP stream
vlc rtsp://CAMERA_IP/live/profile.0
```

### Test API Access
```bash
# Get camera information
curl -u admin:052446 http://CAMERA_IP/common/info.cgi

# Control LED
curl -u admin:052446 http://CAMERA_IP/config/led.cgi?led=off
```

## Home Assistant Integration

Add to your `configuration.yaml`:

```yaml
camera:
  - platform: generic
    stream_source: rtsp://CAMERA_IP/live/profile.0
    name: DCS-8000LH Camera
    authentication: basic
    username: admin
    password: 052446

  - platform: generic
    stream_source: http://CAMERA_IP/video/mpegts.cgi
    name: DCS-8000LH HTTP Stream
    authentication: basic
    username: admin
    password: 052446
```

## Frigate NVR Integration

Add to your `frigate/config/config.yml`:

```yaml
cameras:
  dcs_8000lh:
    ffmpeg:
      inputs:
        - path: rtsp://CAMERA_IP/live/profile.0
          roles:
            - detect
            - record
    detect:
      width: 1280
      height: 720
      fps: 5
```

## Troubleshooting

### If Bluetooth Connection Fails
```bash
# Check Bluetooth status
sudo systemctl status bluetooth
sudo hciconfig hci0 up

# Reset Bluetooth
sudo systemctl restart bluetooth
```

### If Network Configuration Fails
```bash
# Check network configuration
python3 dcs8000lh-configure.py B0:C5:54:51:EB:76 052446 --netconf

# Test connectivity
ping CAMERA_IP
```

### If Streaming Doesn't Work
```bash
# Check RTSP status
curl -u admin:052446 http://CAMERA_IP/config/rtspurl.cgi?profileid=1

# Restart RTSP
python3 dcs8000lh-configure.py B0:C5:54:51:EB:76 052446 --rtsp
```

## Security Recommendations

### Change Default Password
```bash
python3 dcs8000lh-configure.py B0:C5:54:51:EB:76 052446 --command "tdb set HTTPAccount AdminPasswd_ss='your_new_password'"
```

### Enable HTTPS
```bash
python3 dcs8000lh-configure.py B0:C5:54:51:EB:76 052446 --command "tdb set HTTPServer Enable_byte=1"
```

## Next Steps

1. **Run the automated setup**: `./defogger-setup.sh`
2. **Test streaming endpoints** with VLC or similar player
3. **Configure Home Assistant integration** if desired
4. **Set up Frigate NVR** for AI motion detection
5. **Change default passwords** for security

Your camera is now ready for defogger setup with all the correct details pre-configured!
