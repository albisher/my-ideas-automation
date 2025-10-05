# FTDI USB Communication Tools

## Overview

This directory contains tools and scripts for communicating with the DCS-8000LH camera using the Adafruit FTDI USB-to-Serial adapter. These tools enable direct serial communication for debugging, firmware flashing, and system management.

## Tools Included

### Core Communication Tools
- `serial_console.py` - Serial console interface
- `firmware_flasher.py` - Firmware flashing via serial
- `system_monitor.py` - System monitoring and diagnostics
- `network_config.py` - Network configuration via serial

### Utility Scripts
- `connection_test.py` - Test FTDI connection
- `boot_monitor.py` - Monitor boot process
- `command_executor.py` - Execute commands via serial
- `log_analyzer.py` - Analyze system logs

## Installation

### Prerequisites
```bash
# Install Python dependencies
pip install pyserial
pip install colorama
pip install click

# Install FTDI drivers
# Windows: Download from FTDI website
# Linux: sudo apt-get install libftdi1-dev
# macOS: brew install libftdi
```

### Setup
```bash
# Clone repository
git clone https://github.com/defogger/defogger.git
cd defogger/tools/ftdi-communication

# Make scripts executable
chmod +x *.py

# Test connection
python connection_test.py
```

## Usage

### Serial Console
```bash
# Open serial console
python serial_console.py --port COM3 --baud 115200

# With custom settings
python serial_console.py --port /dev/ttyUSB0 --baud 115200 --timeout 1
```

### Firmware Flashing
```bash
# Flash firmware via serial
python firmware_flasher.py --port COM3 --firmware firmware.bin

# With verification
python firmware_flasher.py --port COM3 --firmware firmware.bin --verify
```

### System Monitoring
```bash
# Monitor system status
python system_monitor.py --port COM3 --duration 60

# Monitor specific metrics
python system_monitor.py --port COM3 --metrics cpu,memory,network
```

### Network Configuration
```bash
# Configure network via serial
python network_config.py --port COM3 --wifi-ssid "YourNetwork" --wifi-password "YourPassword"

# Set static IP
python network_config.py --port COM3 --static-ip 192.168.1.100 --gateway 192.168.1.1
```

## Script Documentation

### serial_console.py
Interactive serial console for direct communication with the camera.

**Usage:**
```bash
python serial_console.py [OPTIONS]
```

**Options:**
- `--port`: Serial port (e.g., COM3, /dev/ttyUSB0)
- `--baud`: Baud rate (default: 115200)
- `--timeout`: Timeout in seconds (default: 1)
- `--log`: Enable logging to file
- `--verbose`: Enable verbose output

**Features:**
- Interactive command line
- Command history
- Logging capabilities
- Error handling
- Auto-reconnection

### firmware_flasher.py
Flash firmware to the camera via serial connection.

**Usage:**
```bash
python firmware_flasher.py [OPTIONS]
```

**Options:**
- `--port`: Serial port
- `--firmware`: Firmware file path
- `--verify`: Verify after flashing
- `--backup`: Create backup before flashing
- `--force`: Force flash even if risky

**Features:**
- U-Boot command execution
- TFTP firmware transfer
- Flash verification
- Backup creation
- Progress monitoring

### system_monitor.py
Monitor system status and performance via serial.

**Usage:**
```bash
python system_monitor.py [OPTIONS]
```

**Options:**
- `--port`: Serial port
- `--duration`: Monitoring duration in seconds
- `--metrics`: Specific metrics to monitor
- `--output`: Output file for logs
- `--interval`: Monitoring interval in seconds

**Features:**
- Real-time monitoring
- Performance metrics
- System health checks
- Alert notifications
- Data logging

### network_config.py
Configure network settings via serial connection.

**Usage:**
```bash
python network_config.py [OPTIONS]
```

**Options:**
- `--port`: Serial port
- `--wifi-ssid`: WiFi network name
- `--wifi-password`: WiFi password
- `--static-ip`: Static IP address
- `--gateway`: Gateway IP address
- `--dns`: DNS server IP

**Features:**
- WiFi configuration
- Static IP setup
- Network testing
- Configuration backup
- Validation

## Configuration

### config.ini
Main configuration file for FTDI communication tools.

```ini
[serial]
default_port = COM3
default_baud = 115200
timeout = 1
retries = 3

[logging]
log_level = INFO
log_file = ftdi_communication.log
max_log_size = 10MB
backup_count = 5

[monitoring]
default_interval = 5
alert_thresholds = cpu:80,memory:90,network:100
notification_email = admin@example.com

[network]
default_gateway = 192.168.1.1
default_dns = 8.8.8.8
wifi_timeout = 30
```

### requirements.txt
Python dependencies for FTDI communication tools.

```
pyserial>=3.5
colorama>=0.4.4
click>=8.0.0
requests>=2.25.0
psutil>=5.8.0
```

## Examples

### Basic Serial Communication
```python
import serial
import time

# Open serial connection
ser = serial.Serial('COM3', 115200, timeout=1)

# Send command
ser.write(b'help\r\n')
time.sleep(0.1)

# Read response
response = ser.read(1024)
print(response.decode('utf-8'))

# Close connection
ser.close()
```

### U-Boot Command Execution
```python
import serial
import time

def execute_uboot_command(ser, command):
    """Execute U-Boot command via serial"""
    ser.write(f'{command}\r\n'.encode())
    time.sleep(0.5)
    response = ser.read(1024)
    return response.decode('utf-8')

# Open serial connection
ser = serial.Serial('COM3', 115200, timeout=1)

# Execute U-Boot commands
result = execute_uboot_command(ser, 'help')
print(result)

result = execute_uboot_command(ser, 'printenv')
print(result)

ser.close()
```

### System Monitoring
```python
import serial
import time
import json

def monitor_system(ser, duration=60):
    """Monitor system for specified duration"""
    start_time = time.time()
    metrics = []
    
    while time.time() - start_time < duration:
        # Get system info
        ser.write(b'cat /proc/version\r\n')
        time.sleep(0.1)
        version = ser.read(1024).decode('utf-8')
        
        ser.write(b'cat /proc/meminfo\r\n')
        time.sleep(0.1)
        memory = ser.read(1024).decode('utf-8')
        
        # Store metrics
        metrics.append({
            'timestamp': time.time(),
            'version': version,
            'memory': memory
        })
        
        time.sleep(5)  # Monitor every 5 seconds
    
    return metrics

# Monitor system
ser = serial.Serial('COM3', 115200, timeout=1)
metrics = monitor_system(ser, 60)
print(json.dumps(metrics, indent=2))
ser.close()
```

## Troubleshooting

### Common Issues
1. **Connection Failed**
   - Check FTDI drivers
   - Verify port number
   - Check cable connections
   - Try different USB port

2. **No Response**
   - Check baud rate
   - Verify voltage levels
   - Check for loose connections
   - Try different terminal software

3. **Garbled Output**
   - Check baud rate settings
   - Verify flow control
   - Check for interference
   - Try different cable

### Debug Mode
```bash
# Enable debug logging
python serial_console.py --port COM3 --verbose --log debug.log

# Test connection
python connection_test.py --port COM3 --debug

# Monitor with detailed output
python system_monitor.py --port COM3 --verbose
```

## Safety Considerations

### Electrical Safety
- **Voltage Levels**: 3.3V is generally safe
- **Power Off**: Always power off before connecting
- **ESD Protection**: Use anti-static precautions
- **Short Circuits**: Avoid shorting connections

### Data Safety
- **Backup**: Always backup before flashing
- **Verification**: Verify firmware integrity
- **Recovery**: Have recovery procedures ready
- **Testing**: Test on non-critical hardware first

## Advanced Usage

### Custom Commands
```python
# Custom command execution
def execute_command(ser, command, timeout=5):
    ser.write(f'{command}\r\n'.encode())
    time.sleep(timeout)
    response = ser.read(4096)
    return response.decode('utf-8')

# Execute custom commands
result = execute_command(ser, 'ls -la /etc')
print(result)
```

### Batch Operations
```python
# Execute multiple commands
commands = [
    'cat /proc/version',
    'cat /proc/meminfo',
    'ifconfig',
    'ps aux'
]

for cmd in commands:
    result = execute_command(ser, cmd)
    print(f'Command: {cmd}')
    print(f'Result: {result}')
    print('-' * 50)
```

### Error Handling
```python
import serial
import time

def safe_serial_operation(port, baud, operation):
    """Safely execute serial operation with error handling"""
    try:
        ser = serial.Serial(port, baud, timeout=1)
        result = operation(ser)
        ser.close()
        return result
    except serial.SerialException as e:
        print(f"Serial error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Safe command execution
def execute_command(ser):
    ser.write(b'help\r\n')
    time.sleep(0.5)
    return ser.read(1024).decode('utf-8')

result = safe_serial_operation('COM3', 115200, execute_command)
if result:
    print(result)
```

## Contributing

### Development Setup
```bash
# Fork repository
git clone https://github.com/your-username/defogger.git
cd defogger/tools/ftdi-communication

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
