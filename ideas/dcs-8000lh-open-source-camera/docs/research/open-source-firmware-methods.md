# DCS-8000LH Open Source Firmware Methods

## Executive Summary

The DCS-8000LH can be modified with custom firmware using several open source approaches. The defogger project provides the most comprehensive solution, but there are alternative methods for different skill levels.

## Method 1: Defogger Project (Recommended)

### Overview
The defogger project by Bjørn Mork provides a complete solution for enabling local streaming on DCS-8000LH cameras.

### Requirements
- Linux PC with Bluetooth controller
- Python3 with bluepy library
- WiFi network with WPA2-PSK
- mksquashfs from squashfs-tools package
- TFTP server or web server for backups

### Steps

#### 1. Hardware Access
- **Serial Console**: 4-pin header under bottom label
- **Pinout**: 3.3V, TX, RX, GND (2mm spacing)
- **Parameters**: 57600 8N1
- **U-Boot Password**: `alpha168`

#### 2. Bluetooth Configuration
```bash
# Install dependencies
pip install bluepy

# Configure camera via Bluetooth
./dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --survey
./dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --essid YourWiFi --wifipw YourPassword
./dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --lighttpd
./dcs8000lh-configure.py B0:C5:54:AA:BB:CC 123456 --unsignedfw
```

#### 3. Build Custom Firmware
```bash
# Build defogger firmware
make

# This creates fw.tar with enhanced streaming capabilities
```

#### 4. Flash Custom Firmware
```bash
# Upload and flash custom firmware
curl --http1.0 -u admin:123456 --form upload=@fw.tar http://192.168.2.37/config/firmwareupgrade.cgi
```

### Results
- Direct HTTP/HTTPS streaming
- RTSP streaming
- NIPCA API access
- Telnet server
- Local control without cloud dependency

## Method 2: Serial Console Approach

### Hardware Setup
1. Remove bottom label to reveal 4-pin header
2. Connect 3.3V TTL adapter (don't connect 3.3V pin)
3. Set terminal to 57600 8N1

### Boot Process
1. Power on camera
2. Press ESC when prompted
3. Enter U-Boot password: `alpha168`
4. Access U-Boot prompt: `rlxboot#`

### Root Shell Access
```bash
# Modify boot arguments for root shell
setenv bootargs ${bootargs} init=/bin/sh
bootm 0xbc1e0000

# Start services
/etc/rc.d/rcS
telnetd -l /bin/sh
```

### Enable HTTP Server
```bash
# Enable HTTP server
tdb set HTTPServer Enable_byte=1
tdb set HTTPAccount AdminPasswd_ss="your_password"
/etc/rc.d/init.d/extra_lighttpd.sh start
```

## Method 3: Firmware Downgrade Approach

### Prerequisites
- Original D-Link firmware v2.02.02
- Web server access enabled

### Steps
1. Enable web server (Method 2)
2. Download original firmware
3. Flash original firmware:
```bash
curl --http1.0 -u admin:password --form upload=@DCS-8000LH_Ax_v2.02.02_3014.bin http://CAMERA_IP/config/firmwareupgrade.cgi
```
4. Re-enable web server
5. Flash custom firmware

## Method 4: Custom OpenWrt Development

### Hardware Analysis
- **SoC**: Realtek RTL8196E (MIPS architecture)
- **RAM**: 64MB
- **Flash**: 16MB W25Q128FV
- **WiFi**: Realtek RTL8192CU
- **Camera**: H.264 encoder

### Development Approach
1. **Kernel**: Linux 3.10.27 (MIPS)
2. **Bootloader**: U-Boot 2014.01-rc2-V1.1
3. **File System**: SquashFS with XZ compression

### Custom Firmware Development
```bash
# Extract original firmware
tar xvf DCS-8000LH_Ax_v2.02.02_3014.bin

# Decrypt firmware
openssl rsautl -decrypt -in aes.key.rsa -inkey decrypt.key -out aes.key
openssl aes-128-cbc -md md5 -kfile aes.key -nosalt -d -in update.bin.aes -out update.bin

# Analyze partitions
binwalk update
```

## Method 5: Minimal Streaming Firmware

### Create Minimal Firmware
```bash
# Create minimal opt.local script
cat > opt.local << 'EOF'
#!/bin/sh
# Enable HTTP server
tdb set HTTPServer Enable_byte=1
/etc/rc.d/init.d/extra_lighttpd.sh start

# Enable RTSP
tdb set RTPServer RejectExtIP_byte=0
tdb set RTPServer Authenticate_byte=1
/etc/rc.d/init.d/rtspd.sh restart

# Enable telnet
telnetd -l /bin/sh
EOF

# Create version file
echo "1.0.0" > version

# Build squashfs
mksquashfs version opt.local opt.squashfs -all-root -comp xz
```

## Streaming Endpoints

### HTTP Streaming
- **MPEG-TS**: `http://CAMERA_IP/video/mpegts.cgi`
- **FLV**: `http://CAMERA_IP/video/flv.cgi`
- **Authentication**: admin:PIN_CODE

### RTSP Streaming
- **Profile 1**: `rtsp://CAMERA_IP/live/profile.0`
- **Authentication**: admin:PIN_CODE

### NIPCA API
- **Info**: `http://CAMERA_IP/common/info.cgi`
- **LED Control**: `http://CAMERA_IP/config/led.cgi?led=off`
- **Date/Time**: `http://CAMERA_IP/config/datetime.cgi`

## Troubleshooting

### Common Issues
1. **Bluetooth Connection Failed**: Check PIN code and MAC address format
2. **Firmware Upload Failed**: Use HTTP/1.0 and correct field name
3. **Streaming Not Working**: Verify RTSP settings and firewall
4. **Camera Bricked**: Use serial console for recovery

### Recovery Methods
1. **Serial Console**: Access U-Boot and modify boot arguments
2. **Factory Reset**: Hold reset button for 10 seconds
3. **Firmware Restore**: Flash original D-Link firmware

## Security Considerations

### Risks
- **Device Bricking**: High risk if firmware is corrupted
- **Security Vulnerabilities**: Custom firmware may have security holes
- **Warranty Void**: Modifications void manufacturer warranty

### Mitigations
- **Backup Everything**: Create complete partition backups
- **Test Environment**: Use test camera first
- **Recovery Plan**: Have recovery methods ready

## Conclusion

The defogger project (Method 1) provides the most comprehensive solution for enabling local streaming on the DCS-8000LH. For advanced users, custom OpenWrt development (Method 4) offers the most control but requires significant expertise.

**Recommended Approach**: Start with Method 1 (defogger) for immediate results, then explore Method 4 for advanced customization.
