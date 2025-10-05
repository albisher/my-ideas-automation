# Xiaomi Smart Speaker with IR - Home Assistant Integration Research

## Issue: Integrating Xiaomi Smart Speaker with IR Control into Home Assistant

### Problem Analysis
The Xiaomi Smart Speaker with IR Control (L05G model) is designed to work with the Mi Home app and Google Assistant, but direct integration with Home Assistant is challenging due to limited support.

### What Doesn't Work: Direct Integration ❌

#### 1. **No Native Home Assistant Support**
- Xiaomi Miio integration doesn't support the L05G smart speaker
- No official Home Assistant integration for IR control features
- Limited API access for third-party control

#### 2. **Hardware Limitations**
- No exposed UART pins for direct communication
- Encrypted firmware prevents modification
- No GPIO access for external control
- Warranty void if hardware is modified

#### 3. **Software Barriers**
- Proprietary firmware with no open source
- No official API for PC/Home Assistant control
- Limited to voice commands through Google Assistant
- No direct network control capabilities

### What Works: Alternative Solutions ✅

#### Solution 1: BroadLink RM4 Pro Integration (Recommended)

**Why This Works:**
- **Native Home Assistant Support**: Full integration via BroadLink component
- **IR Learning Capability**: Can learn IR commands from any remote
- **Network Control**: WiFi-based control from Home Assistant
- **Reliable Hardware**: Commercial-grade IR blaster
- **Easy Setup**: Plug-and-play configuration

**Home Assistant Configuration:**
```yaml
# configuration.yaml
broadlink:
  host: 192.168.1.100
  mac: 'AA:BB:CC:DD:EE:FF'
  type: rm4_pro
  timeout: 15
  retry: 3
```

**Implementation Steps:**
1. **Purchase BroadLink RM4 Pro** (~$30-50)
2. **Connect to WiFi** using BroadLink app
3. **Add to Home Assistant** via integration
4. **Learn IR Commands** from existing remotes
5. **Create Automations** for IR control

**Advantages:**
- ✅ Native Home Assistant support
- ✅ No hardware modification required
- ✅ Can learn any IR command
- ✅ Reliable and well-documented
- ✅ 360-degree IR coverage
- ✅ Works with all IR devices

#### Solution 2: ESP32 + IR Transmitter (DIY)

**Why This Works:**
- **Full Customization**: Complete control over functionality
- **Home Assistant Integration**: Via ESPHome or MQTT
- **Cost Effective**: ~$15-25 total cost
- **Learning Capability**: Can capture and replay IR signals
- **Expandable**: Can add sensors and other features

**Hardware Requirements:**
- ESP32 development board
- IR LED transmitter
- Resistor (220Ω)
- Transistor (2N2222)
- Breadboard and jumper wires

**ESPHome Configuration:**
```yaml
# esp32_ir_controller.yaml
esphome:
  name: esp32-ir-controller
  platform: ESP32
  board: esp32dev

wifi:
  ssid: "YourWiFi"
  password: "YourPassword"

api:
  encryption:
    key: "your-encryption-key"

ota:

remote_transmitter:
  pin: GPIO2
  carrier_duty_percent: 50%

# Example IR commands
text_sensor:
  - platform: template
    name: "IR Commands"
    id: ir_commands

button:
  - platform: template
    name: "TV Power"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x20DF
          command: 0x10EF
```

**Advantages:**
- ✅ Full customization control
- ✅ Native ESPHome integration
- ✅ Very cost effective
- ✅ Can learn any IR protocol
- ✅ Educational and fun to build

#### Solution 3: Raspberry Pi + IR Transmitter

**Why This Works:**
- **Complete Control**: Full customization capabilities
- **Multiple Protocols**: Support for all IR protocols
- **Learning**: Can capture and replay IR signals
- **Home Assistant Integration**: Via MQTT or REST API
- **Expandable**: Can add cameras, sensors, etc.

**Hardware Setup:**
```python
# IR signal capture and transmission
import RPi.GPIO as GPIO
import time
import json

class IRController:
    def __init__(self, ir_pin=18):
        self.ir_pin = ir_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(ir_pin, GPIO.OUT)
    
    def send_ir_command(self, command_data):
        for pulse in command_data:
            GPIO.output(self.ir_pin, GPIO.HIGH)
            time.sleep(pulse[0])
            GPIO.output(self.ir_pin, GPIO.LOW)
            time.sleep(pulse[1])
```

**Home Assistant Integration:**
```yaml
# configuration.yaml
rest_command:
  ir_tv_power:
    url: "http://192.168.1.50:8080/ir/send"
    method: POST
    payload: '{"command": "tv_power"}'
    content_type: 'application/json'

automation:
  - alias: "Turn on TV"
    trigger:
      - platform: state
        entity_id: input_boolean.tv_control
        to: 'on'
    action:
      - service: rest_command.ir_tv_power
```

**Advantages:**
- ✅ Complete control and customization
- ✅ Can learn any IR protocol
- ✅ Multiple connectivity options
- ✅ Can add other features
- ✅ Great for learning

### Recommended Implementation Plan

#### Phase 1: Quick Solution (BroadLink RM4 Pro)
1. **Purchase BroadLink RM4 Pro**
2. **Set up in Home Assistant**
3. **Learn IR commands from existing remotes**
4. **Create automations and scripts**
5. **Test with your IR devices**

#### Phase 2: Advanced Solution (ESP32)
1. **Order ESP32 and IR components**
2. **Build IR transmitter circuit**
3. **Flash ESPHome firmware**
4. **Integrate with Home Assistant**
5. **Learn and store IR commands**

### Cost Comparison

| Solution | Hardware Cost | Development Time | Complexity | Reliability |
|----------|---------------|------------------|------------|-------------|
| BroadLink RM4 Pro | $30-50 | 1-2 days | Low | High |
| ESP32 + IR | $15-25 | 3-5 days | Medium | High |
| Raspberry Pi + IR | $75-100 | 1-2 weeks | High | High |

### Final Recommendation

**For immediate results**: Use **BroadLink RM4 Pro** - it's the fastest way to get IR control working in Home Assistant with minimal effort.

**For learning and customization**: Build an **ESP32 + IR transmitter** - it's cost-effective, educational, and gives you complete control.

**Avoid**: Trying to modify the Xiaomi L05G directly - it's not feasible and will void the warranty.

### Next Steps

1. **Choose your solution** based on your needs and technical comfort level
2. **Order the necessary hardware**
3. **Set up the integration** following the provided configurations
4. **Learn IR commands** from your existing remotes
5. **Create Home Assistant automations** for IR control
6. **Test and refine** your setup

This approach will give you full IR control through Home Assistant without the limitations of the Xiaomi smart speaker's closed ecosystem.
