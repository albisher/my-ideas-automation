# Defogger Scripts

This directory contains the core defogger scripts and utilities for modifying the DCS-8000LH camera firmware.

## Scripts Overview

### Core Scripts
- `firmware_extractor.py` - Extract and analyze firmware images
- `config_modifier.py` - Modify camera configuration files
- `firmware_packer.py` - Create modified firmware images
- `flash_firmware.py` - Flash firmware to camera

### Utility Scripts
- `backup_firmware.py` - Backup original firmware
- `verify_firmware.py` - Verify firmware integrity
- `analyze_firmware.py` - Analyze firmware structure
- `network_scanner.py` - Scan for cameras on network

### Testing Scripts
- `streaming_tester.py` - Test streaming functionality
- `network_tester.py` - Test network performance
- `system_tester.py` - Test system performance
- `comprehensive_test.py` - Run all tests

## Installation

```bash
# Clone repository
git clone https://github.com/defogger/defogger.git
cd defogger

# Install dependencies
pip install -r requirements.txt

# Make scripts executable
chmod +x *.py
```

## Usage

### Basic Usage
```bash
# Extract firmware
python firmware_extractor.py firmware.bin

# Modify configuration
python config_modifier.py --input extracted_firmware/ --output modified_firmware/

# Create defogged firmware
python firmware_packer.py --input modified_firmware/ --output defogged_firmware.bin

# Flash firmware
python flash_firmware.py --camera 192.168.1.100 --firmware defogged_firmware.bin
```

### Advanced Usage
```bash
# Backup original firmware
python backup_firmware.py --camera 192.168.1.100 --output original.bin

# Verify firmware
python verify_firmware.py defogged_firmware.bin

# Test functionality
python comprehensive_test.py --camera 192.168.1.100
```

## Script Documentation

### firmware_extractor.py
Extracts and analyzes firmware images to understand their structure.

**Usage:**
```bash
python firmware_extractor.py <firmware_file.bin>
```

**Options:**
- `--output`: Output directory for extracted files
- `--verbose`: Enable verbose output
- `--debug`: Enable debug mode

**Output:**
- Extracted filesystem
- Analysis report
- Component list
- Configuration files

### config_modifier.py
Modifies camera configuration files to enable local functionality.

**Usage:**
```bash
python config_modifier.py --input <input_dir> --output <output_dir>
```

**Options:**
- `--disable-cloud`: Disable cloud services
- `--enable-streaming`: Enable local streaming
- `--modify-web`: Modify web interface
- `--verbose`: Enable verbose output

**Features:**
- Remove cloud authentication
- Enable HTTP streaming
- Configure local management
- Set up WiFi settings

### firmware_packer.py
Creates modified firmware images from extracted filesystems.

**Usage:**
```bash
python firmware_packer.py --input <extracted_fs> --output <firmware.bin>
```

**Options:**
- `--sign`: Sign firmware (if required)
- `--compress`: Enable compression
- `--verbose`: Enable verbose output

**Features:**
- Pack modified filesystem
- Create firmware image
- Sign firmware
- Generate checksums

### flash_firmware.py
Flashes firmware to the camera via network.

**Usage:**
```bash
python flash_firmware.py --camera <ip> --firmware <firmware.bin>
```

**Options:**
- `--backup`: Create backup before flashing
- `--verify`: Verify after flashing
- `--force`: Force flash even if risky
- `--verbose`: Enable verbose output

**Features:**
- Network-based flashing
- Backup creation
- Verification
- Error handling

## Testing Scripts

### streaming_tester.py
Tests streaming functionality and performance.

**Usage:**
```bash
python streaming_tester.py --camera <ip> [options]
```

**Options:**
- `--duration`: Test duration in seconds
- `--protocol`: Streaming protocol (http, rtsp, https)
- `--quality`: Video quality test
- `--performance`: Performance metrics

### network_tester.py
Tests network connectivity and performance.

**Usage:**
```bash
python network_tester.py --camera <ip> [options]
```

**Options:**
- `--bandwidth`: Test bandwidth
- `--latency`: Test latency
- `--stability`: Test connection stability
- `--wifi`: Test WiFi performance

### system_tester.py
Tests system performance and resources.

**Usage:**
```bash
python system_tester.py --camera <ip> [options]
```

**Options:**
- `--cpu`: Test CPU performance
- `--memory`: Test memory usage
- `--storage`: Test storage performance
- `--services`: Test service status

## Configuration

### config.ini
Main configuration file for defogger scripts.

```ini
[general]
debug = false
verbose = false
log_level = INFO

[network]
timeout = 30
retries = 3
scan_range = 192.168.1.0/24

[firmware]
backup_dir = ./backups
temp_dir = ./temp
output_dir = ./output

[streaming]
http_port = 8080
rtsp_port = 554
https_port = 8443
```

### requirements.txt
Python dependencies for defogger scripts.

```
requests>=2.25.0
paramiko>=2.7.0
cryptography>=3.4.0
scapy>=2.4.0
psutil>=5.8.0
```

## Error Handling

### Common Errors
1. **Network Connection Failed**
   - Check camera IP address
   - Verify network connectivity
   - Check firewall settings

2. **Firmware Extraction Failed**
   - Check firmware file integrity
   - Verify firmware version
   - Try different extraction method

3. **Configuration Modification Failed**
   - Check file permissions
   - Verify configuration syntax
   - Test with backup files

4. **Firmware Packing Failed**
   - Check filesystem integrity
   - Verify file sizes
   - Test with original firmware

### Debug Mode
```bash
# Enable debug mode
python script.py --debug --verbose

# Check logs
tail -f defogger.log

# Monitor network
tcpdump -i any host 192.168.1.100
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

## Contributing

### Development Setup
```bash
# Fork repository
git clone https://github.com/your-username/defogger.git
cd defogger

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/
```

### Code Style
- Follow PEP 8 style guide
- Use type hints
- Write comprehensive docstrings
- Include unit tests

### Testing
```bash
# Run unit tests
python -m pytest tests/unit/

# Run integration tests
python -m pytest tests/integration/

# Run all tests
python -m pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

### Documentation
- Read the documentation
- Check the wiki
- Review examples

### Community
- GitHub Issues
- Discussion Forums
- IRC Channel

### Professional Support
- Consulting Services
- Training Courses
- Custom Development
