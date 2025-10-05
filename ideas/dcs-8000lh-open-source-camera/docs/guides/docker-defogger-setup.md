# Docker-based Defogger Setup for DCS-8000LH

## Overview

This guide uses Docker to run the defogger setup on Linux, avoiding bluepy compilation issues on macOS. The container includes all necessary dependencies and tools.

## Prerequisites

- Docker Desktop for Mac installed and running
- Your camera details (already configured)

## Quick Start

### 1. Build the Container
```bash
cd /Users/amac/myIdeas/ideas/dcs-8000lh-open-source-camera/scripts
./docker-defogger-setup.sh build
```

### 2. Run Automated Setup
```bash
./docker-defogger-setup.sh setup
```

### 3. Interactive Commands
```bash
./docker-defogger-setup.sh interactive
```

### 4. Interactive Shell
```bash
./docker-defogger-setup.sh shell
```

## Your Camera Configuration

The container is pre-configured with your camera details:
- **MAC**: `B0:C5:54:51:EB:76`
- **PIN**: `052446`
- **WiFi**: `SA`
- **Password**: `62Dad64Mom`

## Available Commands

### Build Container
```bash
./docker-defogger-setup.sh build
```
Builds the defogger container with all dependencies.

### Automated Setup
```bash
./docker-defogger-setup.sh setup
```
Runs the complete automated defogger setup.

### Interactive Commands
```bash
./docker-defogger-setup.sh interactive
```
Starts an interactive menu for step-by-step control.

### Interactive Shell
```bash
./docker-defogger-setup.sh shell
```
Starts a bash shell in the container for manual control.

### Cleanup
```bash
./docker-defogger-setup.sh cleanup
```
Cleans up containers and images.

## Manual Commands in Container

Once inside the container, you can run:

### Test Bluetooth Connection
```bash
python3 dcs8000lh-configure.py B0:C5:54:51:EB:76 052446 --survey
```

### Configure WiFi
```bash
python3 dcs8000lh-configure.py B0:C5:54:51:EB:76 052446 --essid SA --wifipw 62Dad64Mom
```

### Enable Services
```bash
python3 dcs8000lh-configure.py B0:C5:54:51:EB:76 052446 --lighttpd
python3 dcs8000lh-configure.py B0:C5:54:51:EB:76 052446 --unsignedfw
python3 dcs8000lh-configure.py B0:C5:54:51:EB:76 052446 --telnetd
python3 dcs8000lh-configure.py B0:C5:54:51:EB:76 052446 --rtsp
```

### Build and Flash Firmware
```bash
make
curl --http1.0 -u admin:052446 --form upload=@fw.tar http://CAMERA_IP/config/firmwareupgrade.cgi
```

## Container Features

- **Ubuntu 22.04** base with all dependencies
- **bluepy** library pre-installed
- **Bluetooth** support with privileged access
- **Network** access for camera communication
- **All defogger tools** ready to use

## Troubleshooting

### Docker Issues
```bash
# Check Docker status
docker info

# Restart Docker Desktop if needed
```

### Bluetooth Issues
```bash
# Check Bluetooth in container
hciconfig

# Restart Bluetooth service
sudo systemctl restart bluetooth
```

### Network Issues
```bash
# Check network connectivity
ping CAMERA_IP

# Test camera access
curl -I http://CAMERA_IP/common/info.cgi
```

## Expected Results

After successful setup:
- **HTTP Streaming**: `http://CAMERA_IP/video/mpegts.cgi`
- **RTSP Streaming**: `rtsp://CAMERA_IP/live/profile.0`
- **API Access**: `http://CAMERA_IP/common/info.cgi`
- **Credentials**: `admin` / `052446`

## Integration Examples

### Home Assistant
```yaml
camera:
  - platform: generic
    stream_source: rtsp://CAMERA_IP/live/profile.0
    name: DCS-8000LH Camera
    authentication: basic
    username: admin
    password: 052446
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

- Change default password after setup
- Enable HTTPS for secure access
- Use strong passwords for production

## Support

- **Full Guide**: `docs/guides/defogger-complete-setup.md`
- **Troubleshooting**: `docs/guides/troubleshooting.md`
- **Docker Issues**: Check Docker Desktop logs
