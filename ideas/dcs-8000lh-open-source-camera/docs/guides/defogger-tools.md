# Defogger Tools and Scripts

## Overview

The defogger tools are a collection of scripts and utilities designed to modify the DCS-8000LH firmware to enable local streaming and remove cloud dependencies. This document outlines the available tools and their usage.

## Defogger Repository

### GitHub Repository
- **Repository**: [defogger](https://github.com/defogger/defogger)
- **License**: MIT License
- **Language**: Python, Shell Scripts
- **Platform**: Linux, macOS, Windows

### Installation
```bash
git clone https://github.com/defogger/defogger.git
cd defogger
pip install -r requirements.txt
```

## Core Tools

### 1. Firmware Extractor
**Purpose**: Extract and analyze firmware images

```bash
python firmware_extractor.py <firmware_file.bin>
```

**Features**:
- Extract filesystem from firmware
- Analyze firmware structure
- Identify key components
- Generate firmware report

**Output**:
- Extracted filesystem
- Analysis report
- Component list
- Configuration files

### 2. Configuration Modifier
**Purpose**: Modify camera configuration files

```bash
python config_modifier.py --input <config_file> --output <modified_config>
```

**Features**:
- Disable cloud services
- Enable local streaming
- Modify network settings
- Update web interface

**Configuration Changes**:
- Remove cloud authentication
- Enable HTTP streaming
- Configure local management
- Set up WiFi settings

### 3. Firmware Packer
**Purpose**: Create modified firmware image

```bash
python firmware_packer.py --input <extracted_fs> --output <modified_firmware.bin>
```

**Features**:
- Pack modified filesystem
- Create firmware image
- Sign firmware (if required)
- Generate checksums

## Defogging Process

### Step 1: Firmware Analysis
```bash
# Extract firmware
python firmware_extractor.py dcs8000lh_v2.02.02.bin

# Analyze components
python analyze_firmware.py extracted_firmware/
```

### Step 2: Configuration Modification
```bash
# Modify web interface
python modify_web_interface.py --input extracted_firmware/www/ --output modified_www/

# Update streaming config
python modify_streaming.py --input extracted_firmware/etc/ --output modified_etc/

# Disable cloud services
python disable_cloud.py --input extracted_firmware/etc/ --output modified_etc/
```

### Step 3: Firmware Creation
```bash
# Create modified firmware
python firmware_packer.py --input modified_firmware/ --output dcs8000lh_defogged.bin

# Verify firmware
python verify_firmware.py dcs8000lh_defogged.bin
```

## Advanced Tools

### 1. Network Scanner
**Purpose**: Discover and analyze camera network

```bash
python network_scanner.py --range 192.168.1.0/24
```

**Features**:
- Scan for cameras
- Identify firmware versions
- Test connectivity
- Analyze services

### 2. Streaming Tester
**Purpose**: Test streaming functionality

```bash
python streaming_tester.py --camera 192.168.1.100
```

**Features**:
- Test HTTP streaming
- Verify RTSP support
- Check audio/video quality
- Monitor performance

### 3. Recovery Tool
**Purpose**: Recover from failed flashing

```bash
python recovery_tool.py --camera 192.168.1.100 --firmware original.bin
```

**Features**:
- Emergency recovery
- Firmware restoration
- System reset
- Network recovery

## Configuration Files

### Web Interface Modifications
```javascript
// Remove cloud authentication
window.cloudAuth = false;
window.localMode = true;

// Enable local streaming
window.streamingConfig = {
    http: true,
    https: true,
    rtsp: true,
    local: true
};
```

### Streaming Configuration
```bash
# Enable HTTP streaming
echo "streaming_http=1" >> /etc/camera.conf
echo "streaming_https=1" >> /etc/camera.conf
echo "streaming_rtsp=1" >> /etc/camera.conf

# Disable cloud services
echo "cloud_enabled=0" >> /etc/camera.conf
echo "cloud_auth=0" >> /etc/camera.conf
```

### Network Configuration
```bash
# Configure WiFi
echo "wifi_mode=station" >> /etc/network.conf
echo "wifi_ssid=YourNetwork" >> /etc/network.conf
echo "wifi_password=YourPassword" >> /etc/network.conf

# Set static IP
echo "ip_mode=static" >> /etc/network.conf
echo "ip_address=192.168.1.100" >> /etc/network.conf
echo "ip_gateway=192.168.1.1" >> /etc/network.conf
```

## Scripts and Automation

### 1. Automated Defogging
```bash
#!/bin/bash
# auto_defog.sh - Automated defogging script

CAMERA_IP="192.168.1.100"
FIRMWARE_FILE="dcs8000lh_v2.02.02.bin"

echo "Starting automated defogging process..."

# Step 1: Backup original firmware
python backup_firmware.py --camera $CAMERA_IP --output original_backup.bin

# Step 2: Extract and modify firmware
python firmware_extractor.py $FIRMWARE_FILE
python config_modifier.py --input extracted_firmware/ --output modified_firmware/

# Step 3: Create defogged firmware
python firmware_packer.py --input modified_firmware/ --output defogged_firmware.bin

# Step 4: Flash modified firmware
python flash_firmware.py --camera $CAMERA_IP --firmware defogged_firmware.bin

echo "Defogging process completed!"
```

### 2. Network Setup
```bash
#!/bin/bash
# network_setup.sh - Configure camera network

CAMERA_IP="192.168.1.100"
WIFI_SSID="YourNetwork"
WIFI_PASSWORD="YourPassword"

echo "Configuring camera network..."

# Connect to camera
ssh root@$CAMERA_IP << EOF
# Configure WiFi
uci set wireless.@wifi-device[0].disabled=0
uci set wireless.@wifi-iface[0].ssid="$WIFI_SSID"
uci set wireless.@wifi-iface[0].key="$WIFI_PASSWORD"
uci commit wireless

# Configure network
uci set network.lan.ipaddr="$CAMERA_IP"
uci commit network

# Restart services
/etc/init.d/network restart
EOF

echo "Network configuration completed!"
```

### 3. Streaming Setup
```bash
#!/bin/bash
# streaming_setup.sh - Configure streaming services

CAMERA_IP="192.168.1.100"

echo "Configuring streaming services..."

# Connect to camera
ssh root@$CAMERA_IP << EOF
# Enable HTTP streaming
echo "streaming_http=1" >> /etc/camera.conf
echo "streaming_port=8080" >> /etc/camera.conf

# Enable RTSP streaming
echo "streaming_rtsp=1" >> /etc/camera.conf
echo "rtsp_port=554" >> /etc/camera.conf

# Configure video settings
echo "video_codec=h264" >> /etc/camera.conf
echo "video_resolution=1280x720" >> /etc/camera.conf
echo "video_bitrate=2000" >> /etc/camera.conf

# Restart camera service
/etc/init.d/camera restart
EOF

echo "Streaming configuration completed!"
```

## Testing and Validation

### 1. Functionality Tests
```bash
# Test web interface
curl -I http://192.168.1.100:80

# Test HTTP streaming
curl -I http://192.168.1.100:8080/stream

# Test RTSP streaming
ffplay rtsp://192.168.1.100:554/stream

# Test HTTPS streaming
curl -k -I https://192.168.1.100:8443/stream
```

### 2. Performance Tests
```bash
# Test streaming performance
python streaming_tester.py --camera 192.168.1.100 --duration 60

# Test network performance
python network_tester.py --camera 192.168.1.100 --test bandwidth

# Test system performance
python system_tester.py --camera 192.168.1.100 --test cpu
```

### 3. Security Tests
```bash
# Test authentication
python security_tester.py --camera 192.168.1.100 --test auth

# Test encryption
python security_tester.py --camera 192.168.1.100 --test ssl

# Test network security
python security_tester.py --camera 192.168.1.100 --test firewall
```

## Troubleshooting

### Common Issues
1. **Firmware Extraction Fails**
   - Check firmware file integrity
   - Verify firmware version compatibility
   - Try different extraction methods

2. **Configuration Modification Fails**
   - Check file permissions
   - Verify configuration syntax
   - Test with backup files

3. **Firmware Packing Fails**
   - Check filesystem integrity
   - Verify file sizes
   - Test with original firmware

4. **Flashing Fails**
   - Check network connectivity
   - Verify camera accessibility
   - Try recovery mode

### Debug Mode
```bash
# Enable debug logging
python defogger.py --debug --verbose

# Enable network debugging
python network_scanner.py --debug --verbose

# Enable streaming debugging
python streaming_tester.py --debug --verbose
```

## Safety Features

### Backup and Recovery
- **Automatic Backup**: Original firmware backup
- **Recovery Mode**: Emergency recovery procedures
- **Rollback**: Firmware rollback capability
- **Verification**: Firmware integrity verification

### Error Handling
- **Graceful Failures**: Safe error handling
- **Logging**: Comprehensive error logging
- **Notifications**: Error notifications
- **Recovery**: Automatic recovery attempts
