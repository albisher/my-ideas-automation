# DCS-8000LH Hardware Specifications

## Camera Overview

The D-Link DCS-8000LH is a wireless network camera designed for home and small office surveillance. This document outlines the hardware specifications and capabilities for open-source firmware development.

## Physical Specifications

### Dimensions
- **Size**: 95mm x 95mm x 95mm (3.7" x 3.7" x 3.7")
- **Weight**: Approximately 200g
- **Mounting**: Wall/ceiling mountable with included bracket

### Camera Specifications
- **Sensor**: CMOS image sensor
- **Resolution**: 1280x720 (720p HD)
- **Lens**: Fixed focus lens
- **Field of View**: 110° diagonal
- **Night Vision**: IR LEDs for low-light operation
- **Audio**: Built-in microphone

## Network Specifications

### WiFi
- **Standard**: 802.11n (2.4GHz)
- **Security**: WPA/WPA2 encryption
- **Range**: Up to 100m (open area)

### Ethernet
- **Port**: 10/100 Mbps Ethernet
- **PoE**: Not supported
- **Power**: 5V DC adapter required

## Hardware Architecture

### System-on-Chip (SoC)
- **Processor**: ARM-based SoC (specific model varies by firmware version)
- **Architecture**: ARMv7 or ARMv8
- **Clock Speed**: ~400-800MHz (estimated)
- **Memory**: 64-128MB RAM (estimated)

### Storage
- **Flash Memory**: 16-32MB NOR/NAND flash
- **File System**: Custom firmware filesystem
- **Bootloader**: U-Boot or similar

### I/O Interfaces
- **USB**: Not exposed (internal only)
- **Serial**: UART debug port (4-pin header exposed on camera base)
- **GPIO**: Limited GPIO access
- **I2C/SPI**: Internal sensors and peripherals

### Serial Console Pinout (CONFIRMED)
- **Pin 1**: 3.3V (VCC)
- **Pin 2**: TX (Camera Transmit)
- **Pin 3**: RX (Camera Receive)
- **Pin 4**: GND (Ground)
- **Voltage**: 3.3V logic level
- **Baud Rate**: 115200 bps (typical)

## Power Requirements

### Power Supply
- **Input**: 100-240V AC, 50/60Hz
- **Output**: 5V DC, 1A
- **Consumption**: ~3-5W typical
- **Standby**: ~1-2W

### Power Management
- **Auto Power**: Automatic power-on
- **Power LED**: Status indication
- **Reset Button**: Hardware reset capability

## Connectivity

### Network Interfaces
- **WiFi**: 802.11n 2.4GHz
- **Ethernet**: 10/100 Mbps
- **Protocols**: HTTP, HTTPS, RTSP, ONVIF

### Audio/Video
- **Video Codec**: H.264
- **Audio Codec**: G.711/G.726
- **Streaming**: MPEG-TS over HTTP/HTTPS
- **Resolution**: 720p @ 30fps

## Hardware Modifications

### Required for Development
- **Serial Console**: UART access for debugging (4-pin header exposed)
- **JTAG**: Not typically accessible
- **Boot Mode**: Recovery mode via reset button

### Serial Console Access (CONFIRMED)
- **Location**: 4-pin header on camera base
- **Pinout**: 3.3V, TX, RX, GND (left to right)
- **Access Method**: USB-to-TTL serial adapter
- **Baud Rate**: 115200 bps
- **Login**: "alpha168" access code, then "admin" user

### Optional Modifications
- **External Antenna**: WiFi range extension
- **Power LED**: Status indication modification
- **Reset Button**: Custom functionality

## Firmware Storage

### Flash Layout
- **Bootloader**: First 1-2MB
- **Kernel**: 2-4MB
- **Root Filesystem**: 8-16MB
- **Configuration**: 1-2MB
- **Logs**: 1-2MB

### File System
- **Type**: SquashFS or similar compressed filesystem
- **Mount Points**: /tmp, /var, /etc
- **Writable**: Limited writable space

## Development Considerations

### Debugging
- **Serial Console**: Primary debugging interface
- **Network Logs**: HTTP-based logging
- **LED Indicators**: Status debugging

### Limitations
- **Limited RAM**: Memory constraints for applications
- **Flash Space**: Limited storage for custom applications
- **CPU Power**: Limited processing capability
- **I/O**: Restricted hardware access

## Compatibility Notes

### Firmware Versions
- **v2.01.03**: Tested for defogging
- **v2.02.02**: Tested for defogging
- **Other Versions**: May require different approaches

### Hardware Revisions
- **PCB Revisions**: Different hardware revisions may exist
- **Component Changes**: Some components may vary between batches
- **Firmware Compatibility**: Hardware-specific firmware requirements

## Safety Considerations

### Electrical Safety
- **High Voltage**: AC power input requires caution
- **Low Voltage**: 5V DC is generally safe
- **Grounding**: Proper grounding required

### Physical Safety
- **Sharp Edges**: Be careful with metal components
- **Heat**: Some components may get warm during operation
- **ESD**: Static electricity protection recommended

## Resources

### Documentation
- D-Link official documentation
- Community forums and wikis
- OpenWrt hardware database

### Tools
- Serial console cables
- Multimeter for voltage testing
- Oscilloscope for signal analysis
- Logic analyzer for protocol debugging
