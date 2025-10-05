# Implementation Setup Guide

## Prerequisites

### Hardware Requirements
- USB Remote Control with FSP2C01915A chip
- Compatible TV with IR receiver
- Computer with USB port (Windows/Linux/macOS)
- Optional: IR blaster for extended range

### Software Requirements
- Python 3.8 or higher
- USB HID libraries (pyusb, hidapi)
- IR protocol libraries
- Optional: Virtual environment for isolation

## Installation Steps

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv usb-remote-env
source usb-remote-env/bin/activate  # Linux/macOS
# or
usb-remote-env\Scripts\activate    # Windows

# Install required packages
pip install pyusb hidapi python-hid
pip install requests flask websockets
pip install numpy scikit-learn  # For machine learning features
```

### 2. USB Driver Installation

#### Linux
```bash
# Install libusb development headers
sudo apt-get install libusb-1.0-0-dev  # Ubuntu/Debian
sudo yum install libusb1-devel         # CentOS/RHEL

# Add udev rules for USB device access
sudo nano /etc/udev/rules.d/99-usb-remote.rules
```

#### Windows
- Install WinUSB driver for the USB device
- Use Zadig tool to install proper drivers
- Ensure device is recognized as HID device

#### macOS
- No additional drivers required for HID devices
- May need to disable Gatekeeper for unsigned drivers

### 3. Device Configuration

#### USB Device Discovery
```python
import usb.core
import usb.util

# Find USB device by vendor/product ID
device = usb.core.find(idVendor=0x1234, idProduct=0x5678)
if device is None:
    raise ValueError('USB Remote Control not found')
```

#### HID Report Configuration
```python
# Configure HID report descriptor
REPORT_DESCRIPTOR = [
    0x05, 0x01,  # Usage Page (Generic Desktop)
    0x09, 0x06,  # Usage (Keyboard)
    0xa1, 0x01,  # Collection (Application)
    # ... additional descriptor bytes
]
```

### 4. TV Configuration

#### IR Protocol Detection
```python
# Test different IR protocols
protocols = ['nec', 'rc5', 'rc6', 'pronto']
for protocol in protocols:
    success = test_ir_protocol(protocol, tv_brand, tv_model)
    if success:
        print(f"TV supports {protocol} protocol")
        break
```

#### TV Brand/Model Setup
```python
# Configure TV-specific settings
tv_config = {
    'brand': 'Samsung',
    'model': 'UN55MU8000',
    'protocol': 'nec',
    'power_code': '0xE0E040BF',
    'volume_up': '0xE0E0E01F',
    'volume_down': '0xE0E0D02F',
    'channel_up': '0xE0E048B7',
    'channel_down': '0xE0E008F7'
}
```

### 5. Agent System Setup

#### Core Agent Configuration
```python
# Initialize TV control agent
from software.agent.tv_controller import TVController

agent = TVController(
    usb_device_id='FSP2C01915A',
    tv_config=tv_config,
    learning_enabled=True,
    voice_control=True
)
```

#### API Server Setup
```python
# Start REST API server
from software.api.rest_api import create_app

app = create_app(agent)
app.run(host='0.0.0.0', port=8080, debug=False)
```

### 6. Testing and Validation

#### USB Communication Test
```python
# Test USB HID communication
def test_usb_communication():
    device = find_usb_remote()
    report = device.read_hid_report()
    assert report is not None
    print("USB communication successful")
```

#### IR Signal Test
```python
# Test IR signal transmission
def test_ir_transmission():
    agent = TVController()
    result = agent.send_command('power')
    assert result.success
    print("IR transmission successful")
```

#### End-to-End Test
```python
# Complete system test
def test_complete_system():
    agent = TVController()
    
    # Test basic commands
    commands = ['power', 'volume_up', 'channel_up', 'input_hdmi1']
    for cmd in commands:
        result = agent.send_command(cmd)
        assert result.success
        time.sleep(1)  # Wait between commands
    
    print("Complete system test successful")
```

## Configuration Files

### Device Configuration (`config/device.json`)
```json
{
    "usb_device": {
        "vendor_id": "0x1234",
        "product_id": "0x5678",
        "interface": 0,
        "endpoint": 1
    },
    "ir_settings": {
        "carrier_frequency": 38000,
        "protocol": "nec",
        "repeat_count": 3
    }
}
```

### TV Configuration (`config/tv.json`)
```json
{
    "tv_settings": {
        "brand": "Samsung",
        "model": "UN55MU8000",
        "protocol": "nec",
        "codes": {
            "power": "0xE0E040BF",
            "volume_up": "0xE0E0E01F",
            "volume_down": "0xE0E0D02F",
            "channel_up": "0xE0E048B7",
            "channel_down": "0xE0E008F7"
        }
    }
}
```

### Agent Configuration (`config/agent.json`)
```json
{
    "agent_settings": {
        "learning_enabled": true,
        "voice_control": true,
        "auto_discovery": true,
        "response_timeout": 5.0,
        "retry_count": 3
    }
}
```

## Troubleshooting

### Common Issues
1. **USB Device Not Found**: Check device connection and drivers
2. **Permission Denied**: Add user to appropriate groups (Linux)
3. **IR Signal Not Working**: Verify TV IR receiver and protocol
4. **Agent Not Responding**: Check API server status and logs

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with verbose output
agent = TVController(debug=True)
```

### Log Files
- `logs/usb_communication.log`: USB HID communication logs
- `logs/ir_protocol.log`: IR signal transmission logs
- `logs/agent_control.log`: Agent decision and control logs
- `logs/api_requests.log`: REST API request logs

