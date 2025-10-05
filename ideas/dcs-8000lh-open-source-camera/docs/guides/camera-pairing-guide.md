# DCS-8000LH Camera Pairing Guide

## Overview

The defogger method requires the camera to be in Bluetooth pairing mode. This guide will help you get your camera into the correct state for defogger configuration.

## Prerequisites

- DCS-8000LH camera powered on
- Camera not connected to WiFi network
- Camera in factory reset state (if possible)

## Step-by-Step Pairing Process

### 1. Reset Camera to Factory Settings

**Method A: Physical Reset Button**
1. Power on the camera
2. Locate the reset button (usually a small button on the back)
3. Hold the reset button for 10-15 seconds
4. Release the button
5. Wait for the camera to restart

**Method B: Power Cycle Reset**
1. Unplug the camera from power
2. Wait 30 seconds
3. Plug the camera back in
4. Wait for the camera to fully boot

### 2. Enable Bluetooth Pairing Mode

The camera needs to be in a specific state for Bluetooth pairing:

1. **Ensure camera is NOT connected to WiFi**
2. **Camera should be in setup mode** (not connected to any network)
3. **Camera should be discoverable via Bluetooth**

### 3. Check Camera Status

Before running defogger commands, verify:

- Camera is powered on
- Camera is not connected to WiFi
- Camera is in setup/configuration mode
- Camera LED should be blinking (indicating setup mode)

### 4. Run Defogger Commands

Once the camera is in the correct state:

```bash
cd /Users/amac/myIdeas/ideas/dcs-8000lh-open-source-camera/scripts
./run-defogger-commands.sh commands
```

## Troubleshooting

### Camera Not Discoverable

If the camera is not discoverable via Bluetooth:

1. **Reset the camera completely**
2. **Wait 2-3 minutes after reset**
3. **Ensure camera is not connected to any network**
4. **Try running defogger commands again**

### Bluetooth Connection Failed

If you get "Failed to connect to peripheral":

1. **Check camera MAC address**: `B0:C5:54:51:EB:76`
2. **Verify camera is in pairing mode**
3. **Try resetting camera again**
4. **Wait longer between reset and defogger commands**

### Camera Already Connected to WiFi

If the camera is already connected to WiFi:

1. **Reset camera to factory settings**
2. **Do NOT connect to WiFi during setup**
3. **Run defogger commands first**
4. **Then configure WiFi through defogger**

## Alternative Approach: Network Configuration

If Bluetooth pairing continues to fail, you can try the network approach:

### 1. Connect Camera to WiFi Manually

1. Use the D-Link app to connect camera to your WiFi
2. Note the camera's IP address
3. Use network-based defogger commands

### 2. Network-Based Defogger

```bash
# Detect camera IP
./run-defogger-commands.sh detect

# Configure via network (if camera is accessible)
curl -u admin:052446 http://CAMERA_IP/config/firmwareupgrade.cgi
```

## Expected Results

After successful pairing and configuration:

- **HTTP Streaming**: `http://CAMERA_IP/video/mpegts.cgi`
- **RTSP Streaming**: `rtsp://CAMERA_IP/live/profile.0`
- **API Access**: `http://CAMERA_IP/common/info.cgi`
- **Credentials**: `admin` / `052446`

## Next Steps

Once defogger configuration is successful:

1. **Test streaming with VLC**:
   - Open VLC Media Player
   - Go to Media > Open Network Stream
   - Enter: `rtsp://CAMERA_IP/live/profile.0`
   - Username: `admin`, Password: `052446`

2. **Configure Home Assistant** (if needed):
   - Add camera entity
   - Configure streaming URL
   - Set up motion detection

## Support

- **Full Defogger Guide**: `docs/guides/defogger-complete-setup.md`
- **Troubleshooting**: `docs/guides/troubleshooting.md`
- **Docker Setup**: `docs/guides/docker-defogger-setup.md`
