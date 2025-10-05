# DCS-8000LH Troubleshooting Guide

## Common Issues and Solutions

### 1. Camera Not Accessible

#### Symptoms
- Cannot access camera web interface
- Ping fails to camera IP
- Network scan doesn't find camera
- LEDs not indicating normal operation

#### Diagnosis
```bash
# Check network connectivity
ping 192.168.1.100

# Scan for camera
nmap -sn 192.168.1.0/24

# Check ARP table
arp -a | grep dlink

# Test specific ports
nmap -p 80,443,8080,554 192.168.1.100
```

#### Solutions
1. **Power Cycle Camera**
   ```bash
   # Turn off camera
   # Wait 10 seconds
   # Turn on camera
   # Wait 2-3 minutes for boot
   ```

2. **Reset Camera**
   ```bash
   # Press and hold reset button for 10 seconds
   # Release button
   # Wait for camera to reboot
   ```

3. **Check Network Settings**
   ```bash
   # Verify camera IP
   # Check subnet mask
   # Verify gateway
   # Test with different network
   ```

4. **Recovery Mode**
   ```bash
   # Press and hold reset button for 30 seconds
   # Power cycle camera
   # Access recovery interface
   ```

### 2. Firmware Flashing Issues

#### Symptoms
- Flashing process fails
- Camera becomes unresponsive
- Boot loop or no boot
- Error messages during flashing

#### Diagnosis
```bash
# Check firmware integrity
python verify_firmware.py firmware.bin

# Check camera connectivity
ping 192.168.1.100

# Test camera services
curl -I http://192.168.1.100

# Check flash logs
tail -f flash_log.txt
```

#### Solutions
1. **Verify Firmware**
   ```bash
   # Check firmware version compatibility
   python analyze_firmware.py firmware.bin
   
   # Verify firmware integrity
   python verify_firmware.py firmware.bin
   
   # Test with known good firmware
   ```

2. **Recovery Procedures**
   ```bash
   # Boot into recovery mode
   # Press and hold reset button for 30 seconds
   
   # Flash original firmware
   python flash_firmware.py --camera 192.168.1.100 --firmware original_firmware.bin
   
   # Verify recovery
   curl -I http://192.168.1.100
   ```

3. **Network Issues**
   ```bash
   # Check network connectivity
   ping 192.168.1.100
   
   # Test with Ethernet cable
   # Verify router settings
   # Check firewall rules
   ```

### 3. Streaming Problems

#### Symptoms
- No video stream
- Poor video quality
- High latency
- Stream drops frequently

#### Diagnosis
```bash
# Test HTTP streaming
curl -I http://192.168.1.100:8080/stream

# Test RTSP streaming
ffplay rtsp://192.168.1.100:554/stream

# Check streaming service
/etc/init.d/streaming status

# Monitor network traffic
tcpdump -i any host 192.168.1.100
```

#### Solutions
1. **Check Streaming Configuration**
   ```bash
   # Verify streaming settings
   cat /etc/camera.conf | grep streaming
   
   # Restart streaming service
   /etc/init.d/streaming restart
   
   # Check port configuration
   netstat -tlnp | grep 8080
   ```

2. **Network Optimization**
   ```bash
   # Check network bandwidth
   iperf3 -c 192.168.1.100
   
   # Optimize video settings
   echo "video_bitrate=1000" >> /etc/camera.conf
   echo "video_resolution=640x480" >> /etc/camera.conf
   
   # Restart camera service
   /etc/init.d/camera restart
   ```

3. **Codec Issues**
   ```bash
   # Check codec support
   ffmpeg -codecs | grep h264
   
   # Test different codecs
   echo "video_codec=mjpeg" >> /etc/camera.conf
   
   # Restart services
   /etc/init.d/camera restart
   ```

### 4. WiFi Connection Issues

#### Symptoms
- Camera cannot connect to WiFi
- Intermittent WiFi connection
- Poor WiFi signal strength
- WiFi authentication failures

#### Diagnosis
```bash
# Check WiFi configuration
uci show wireless

# Test WiFi connectivity
iwconfig

# Check signal strength
iwlist scan

# Test authentication
wpa_supplicant -i wlan0 -c /etc/wpa_supplicant.conf
```

#### Solutions
1. **WiFi Configuration**
   ```bash
   # Reset WiFi settings
   uci set wireless.@wifi-device[0].disabled=1
   uci commit wireless
   /etc/init.d/network restart
   
   # Reconfigure WiFi
   uci set wireless.@wifi-device[0].disabled=0
   uci set wireless.@wifi-iface[0].ssid="YourNetwork"
   uci set wireless.@wifi-iface[0].key="YourPassword"
   uci commit wireless
   /etc/init.d/network restart
   ```

2. **Signal Strength Issues**
   ```bash
   # Check signal strength
   iwlist scan | grep -A 5 "YourNetwork"
   
   # Move camera closer to router
   # Check for interference
   # Use 5GHz band if available
   ```

3. **Authentication Problems**
   ```bash
   # Verify network credentials
   # Check network security settings
   # Test with different network
   # Reset network configuration
   ```

### 5. Performance Issues

#### Symptoms
- Slow system response
- High CPU usage
- Memory issues
- Network timeouts

#### Diagnosis
```bash
# Check system resources
top
free -m
df -h

# Monitor network
iftop -i eth0

# Check system logs
logread | tail -50

# Monitor camera processes
ps aux | grep camera
```

#### Solutions
1. **Resource Optimization**
   ```bash
   # Check memory usage
   free -m
   
   # Optimize video settings
   echo "video_bitrate=1000" >> /etc/camera.conf
   echo "video_resolution=640x480" >> /etc/camera.conf
   
   # Restart services
   /etc/init.d/camera restart
   ```

2. **Network Optimization**
   ```bash
   # Check network bandwidth
   iperf3 -c 192.168.1.100
   
   # Optimize network settings
   echo "net.core.rmem_max=16777216" >> /etc/sysctl.conf
   echo "net.core.wmem_max=16777216" >> /etc/sysctl.conf
   
   # Apply settings
   sysctl -p
   ```

3. **System Maintenance**
   ```bash
   # Clear logs
   logread -c
   
   # Clean temporary files
   rm -rf /tmp/*
   
   # Restart system
   reboot
   ```

### 6. Security Issues

#### Symptoms
- Unauthorized access attempts
- Security warnings
- SSL/TLS errors
- Authentication failures

#### Diagnosis
```bash
# Check security logs
logread | grep -i security

# Test SSL/TLS
openssl s_client -connect 192.168.1.100:443

# Check authentication
curl -X POST http://192.168.1.100/login -d "username=admin&password=admin"

# Monitor network traffic
tcpdump -i any host 192.168.1.100
```

#### Solutions
1. **Authentication Issues**
   ```bash
   # Reset password
   passwd root
   
   # Check user accounts
   cat /etc/passwd
   
   # Verify authentication settings
   cat /etc/camera.conf | grep auth
   ```

2. **SSL/TLS Problems**
   ```bash
   # Check certificate
   openssl x509 -in /etc/ssl/cert.pem -text -noout
   
   # Regenerate certificate
   openssl req -x509 -newkey rsa:2048 -keyout /etc/ssl/private/key.pem -out /etc/ssl/cert.pem -days 365 -nodes
   
   # Restart web server
   /etc/init.d/uhttpd restart
   ```

3. **Firewall Configuration**
   ```bash
   # Check firewall rules
   iptables -L
   
   # Configure firewall
   uci set firewall.@defaults[0].input="ACCEPT"
   uci set firewall.@defaults[0].output="ACCEPT"
   uci set firewall.@defaults[0].forward="ACCEPT"
   uci commit firewall
   
   # Restart firewall
   /etc/init.d/firewall restart
   ```

## Advanced Troubleshooting

### 1. Serial Console Access

#### Hardware Requirements
- USB-to-TTL adapter (3.3V)
- Jumper wires
- Soldering iron (optional)

#### Connection
```
Camera UART    USB-TTL Adapter
VCC (3.3V)  -> VCC
GND         -> GND
TX          -> RX
RX          -> TX
```

#### Software Setup
```bash
# Install serial console tools
sudo apt-get install minicom

# Configure serial console
sudo minicom -s

# Set serial port (e.g., /dev/ttyUSB0)
# Set baud rate: 115200
# Set data bits: 8
# Set parity: None
# Set stop bits: 1
# Set flow control: None
```

### 2. Firmware Analysis

#### Extract Firmware
```bash
# Extract firmware filesystem
python firmware_extractor.py firmware.bin

# Analyze filesystem
ls -la extracted_firmware/

# Check key files
cat extracted_firmware/etc/camera.conf
cat extracted_firmware/etc/network.conf
```

#### Modify Firmware
```bash
# Make modifications
python config_modifier.py --input extracted_firmware/ --output modified_firmware/

# Create new firmware
python firmware_packer.py --input modified_firmware/ --output new_firmware.bin

# Verify firmware
python verify_firmware.py new_firmware.bin
```

### 3. Network Debugging

#### Network Analysis
```bash
# Monitor network traffic
tcpdump -i any host 192.168.1.100

# Check network configuration
ifconfig
route -n
cat /etc/resolv.conf

# Test network connectivity
ping 8.8.8.8
nslookup google.com
```

#### WiFi Debugging
```bash
# Check WiFi status
iwconfig
iwlist scan

# Monitor WiFi traffic
tcpdump -i wlan0

# Check WiFi configuration
cat /etc/config/wireless
```

### 4. System Debugging

#### System Logs
```bash
# Check system logs
logread | tail -100

# Check kernel messages
dmesg | tail -50

# Check process status
ps aux | grep camera

# Check system resources
top
free -m
df -h
```

#### Performance Monitoring
```bash
# Monitor CPU usage
top -p $(pgrep camera)

# Monitor memory usage
cat /proc/meminfo

# Monitor network usage
iftop -i eth0

# Monitor disk usage
iostat -x 1
```

## Recovery Procedures

### 1. Firmware Recovery

#### Emergency Recovery
```bash
# Boot into recovery mode
# Press and hold reset button for 30 seconds

# Access recovery interface
# Navigate to http://192.168.1.100/recovery

# Upload original firmware
# Wait for flashing to complete
# Verify recovery
```

#### Serial Recovery
```bash
# Connect serial console
# Boot into U-Boot

# Set network parameters
setenv ipaddr 192.168.1.100
setenv serverip 192.168.1.1
setenv gatewayip 192.168.1.1

# Download firmware
tftp 0x80000000 firmware.bin

# Flash firmware
erase 0x9f000000 +0x800000
cp.b 0x80000000 0x9f000000 0x800000

# Boot system
bootm 0x9f000000
```

### 2. Network Recovery

#### Reset Network Settings
```bash
# Reset to factory defaults
uci set network.lan.proto=dhcp
uci set wireless.@wifi-device[0].disabled=1
uci commit network
uci commit wireless

# Restart network
/etc/init.d/network restart

# Check network status
ifconfig
```

#### Manual Network Configuration
```bash
# Configure static IP
ifconfig eth0 192.168.1.100 netmask 255.255.255.0
route add default gw 192.168.1.1

# Test connectivity
ping 192.168.1.1
ping 8.8.8.8
```

### 3. System Recovery

#### Factory Reset
```bash
# Reset to factory defaults
firstboot -y

# Reboot system
reboot

# Wait for system to boot
# Access web interface
# Reconfigure system
```

#### Manual System Reset
```bash
# Clear configuration
rm -rf /etc/config/*
rm -rf /etc/camera.conf

# Restart services
/etc/init.d/camera restart
/etc/init.d/streaming restart
/etc/init.d/network restart
```

## Prevention and Maintenance

### 1. Regular Maintenance

#### System Updates
```bash
# Check for updates
opkg update
opkg list-upgradable

# Install updates
opkg upgrade

# Restart system
reboot
```

#### Log Management
```bash
# Clear old logs
logread -c

# Rotate logs
logrotate /etc/logrotate.conf

# Monitor log size
du -sh /var/log/*
```

### 2. Monitoring

#### System Monitoring
```bash
# Monitor system resources
watch -n 1 'top -n 1'

# Monitor network
watch -n 1 'iftop -i eth0'

# Monitor disk usage
watch -n 1 'df -h'
```

#### Alert Configuration
```bash
# Configure email alerts
echo "email_alerts=1" >> /etc/camera.conf
echo "email_smtp=smtp.gmail.com" >> /etc/camera.conf
echo "email_port=587" >> /etc/camera.conf
echo "email_username=your_email@gmail.com" >> /etc/camera.conf
echo "email_password=your_password" >> /etc/camera.conf

# Restart camera service
/etc/init.d/camera restart
```

### 3. Backup Procedures

#### Configuration Backup
```bash
# Backup configuration
tar -czf config_backup_$(date +%Y%m%d).tar.gz /etc/

# Backup firmware
python backup_firmware.py --camera 192.168.1.100 --output firmware_backup_$(date +%Y%m%d).bin

# Verify backups
ls -la *backup*
```

#### Automated Backup
```bash
#!/bin/bash
# backup_script.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/tmp/backups/$DATE"

mkdir -p $BACKUP_DIR

# Backup configuration
tar -czf $BACKUP_DIR/config_backup.tar.gz /etc/

# Backup firmware
python backup_firmware.py --camera 192.168.1.100 --output $BACKUP_DIR/firmware_backup.bin

# Clean old backups
find /tmp/backups -type d -mtime +7 -exec rm -rf {} \;
```

## Support and Resources

### 1. Community Support
- **GitHub Issues**: Report bugs and request features
- **Forums**: Community discussion and support
- **Wiki**: Documentation and guides
- **IRC**: Real-time chat support

### 2. Documentation
- **User Manual**: Complete user guide
- **API Documentation**: Programming interface
- **Hardware Guide**: Hardware specifications
- **Troubleshooting**: Common issues and solutions

### 3. Professional Support
- **Consulting**: Professional installation and configuration
- **Training**: Technical training courses
- **Support Contracts**: Ongoing support and maintenance
- **Custom Development**: Custom features and modifications
