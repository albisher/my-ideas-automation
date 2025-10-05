# USB Pin Connection Guide - Making Pins Accessible via USB

## 🎯 **Why USB Connection is a GREAT Idea:**

### **✅ Advantages:**
- **Software Control**: Control pins directly from your computer
- **Real-time Control**: Send commands instantly via USB
- **No Hardware Modification**: Use existing USB interface
- **Easy Testing**: Test pin functions with software
- **Scalable**: Control multiple pins simultaneously
- **Debugging**: Monitor pin states in real-time

### **✅ How It Works:**
- **USB HID Interface**: Already working (we tested this)
- **FSP2C01915A Chip**: Has GPIO pins accessible via USB
- **Software Commands**: Send pin control commands via USB
- **Hardware Response**: Pins change state based on commands

## 🔧 **Connection Methods:**

### **Method 1: Direct Pin Access (Recommended)**
**Use P1 Header pins directly**

**Connection:**
```
USB → FSP2C01915A Chip → P1 Header Pins → IR LED
```

**Steps:**
1. **Identify P1 pin functions** with multimeter
2. **Find GPIO pins** that respond to USB commands
3. **Connect IR LED** to controllable GPIO pin
4. **Control via software** through USB

### **Method 2: External USB-to-GPIO Adapter**
**Add external GPIO control board**

**Connection:**
```
USB → USB-to-GPIO Adapter → IR LED Circuit
```

**Components:**
- **USB-to-GPIO Adapter**: CH340G, CP2102, or similar
- **GPIO Expansion Board**: For multiple pin control
- **IR LED Circuit**: External IR LED with driver

### **Method 3: USB HID Pin Control**
**Use existing USB HID interface**

**Connection:**
```
USB HID Commands → FSP2C01915A Chip → GPIO Pins → IR LED
```

**Implementation:**
- **Send HID reports** to control pins
- **FSP chip processes** commands
- **GPIO pins change** state
- **IR LED activates** based on pin state

## 🎯 **Recommended Approach: USB HID Pin Control**

### **Why This is Best:**
- **No additional hardware** needed
- **Uses existing USB connection**
- **Software-controlled** pin states
- **Real-time control** via USB commands
- **Easy to implement** and test

### **Implementation Steps:**

#### **Step 1: Pin Function Testing**
```python
# Test P1 header pins via USB
import hid

# Send GPIO control commands
device.write([0x01, 0x01, 0x00, 0x00] + [0x00] * 60)  # Pin 1 HIGH
device.write([0x01, 0x00, 0x00, 0x00] + [0x00] * 60)  # Pin 1 LOW
```

#### **Step 2: Hardware Connection**
```
P1 Pin 1 (3.3V) → Resistor (220Ω) → IR LED Anode
P1 Pin 2 (GPIO) → IR LED Cathode
P1 Pin 8 (GND) → IR LED Ground
```

#### **Step 3: Software Control**
```python
# Control IR LED via USB
def control_ir_led(state):
    if state == "ON":
        device.write([0x01, 0x02, 0x00, 0x00] + [0x00] * 60)
    else:
        device.write([0x01, 0x00, 0x00, 0x00] + [0x00] * 60)
```

## 🔧 **Hardware Requirements:**

### **For Direct Pin Access:**
- **IR LED**: 940nm, 5mm, 20-100mA
- **Resistor**: 220Ω-1kΩ (current limiting)
- **Transistor**: 2N2222 (current amplification)
- **Jumper Wires**: 22AWG
- **Multimeter**: To test pin functions

### **For USB-to-GPIO Adapter:**
- **USB-to-GPIO Adapter**: CH340G or CP2102
- **GPIO Expansion Board**: For multiple pins
- **IR LED Circuit**: External circuit
- **USB Cable**: For connection

## 🚀 **Implementation Plan:**

### **Phase 1: Pin Testing**
1. **Test P1 header pins** with multimeter
2. **Send USB commands** to control pins
3. **Measure voltage changes** on pins
4. **Identify controllable pins**

### **Phase 2: Hardware Connection**
1. **Connect IR LED** to controllable pin
2. **Add current limiting resistor**
3. **Test IR LED activation** with USB commands
4. **Verify pin control** functionality

### **Phase 3: Software Integration**
1. **Develop pin control software**
2. **Test IR LED control** via USB
3. **Integrate with TV control** system
4. **Complete USB-controlled IR system**

## 🎯 **Expected Results:**

### **If Successful:**
- ✅ **Pin control** via USB commands
- ✅ **IR LED activation** via software
- ✅ **TV control** through USB
- ✅ **Complete system** integration

### **If Not Successful:**
- ❌ **Pins may not be controllable** via USB
- ❌ **Different approach needed** (external GPIO)
- ❌ **Hardware limitations** of FSP chip

## 🔧 **Testing Procedure:**

### **Step 1: Pin Function Test**
```python
# Test each P1 pin
for pin in range(1, 9):
    # Send HIGH command
    device.write([0x01, 1 << (pin-1), 0x00, 0x00] + [0x00] * 60)
    # Measure voltage with multimeter
    # Send LOW command
    device.write([0x01, 0x00, 0x00, 0x00] + [0x00] * 60)
```

### **Step 2: IR LED Connection**
```
P1 Pin 1 (3.3V) → Resistor → IR LED Anode
P1 Pin 2 (GPIO) → IR LED Cathode
P1 Pin 8 (GND) → IR LED Ground
```

### **Step 3: Software Control**
```python
# Control IR LED
def ir_led_on():
    device.write([0x01, 0x02, 0x00, 0x00] + [0x00] * 60)

def ir_led_off():
    device.write([0x01, 0x00, 0x00, 0x00] + [0x00] * 60)
```

## 🎯 **Conclusion:**

**USB pin control is an EXCELLENT idea because:**
- ✅ **Uses existing USB connection**
- ✅ **Software-controlled** pin states
- ✅ **Real-time control** via USB commands
- ✅ **Easy to implement** and test
- ✅ **No additional hardware** needed

**Next Step**: Test P1 header pins with multimeter while sending USB commands to identify controllable pins!




