# FSP Board Pin Analysis - Hardware Utilization

## 🔍 **Available Pins and Headers from Images**

### **1. P1 Header (8-pin)**
- **Location**: Left side of board
- **Type**: 8-pin header
- **Potential Uses**:
  - **Debugging/Programming**: Access to FSP2C01915A chip pins
  - **GPIO Pins**: General purpose input/output
  - **Power Pins**: 3.3V, 5V, GND
  - **Communication**: UART, SPI, I2C
  - **IR LED Control**: Direct pin control for IR LED

### **2. P2 Header (2-pin)**
- **Location**: Left side, below P1
- **Type**: 2-pin header
- **Potential Uses**:
  - **Power Output**: 3.3V or 5V for external components
  - **Ground**: Common ground connection
  - **IR LED Power**: Power supply for external IR LED
  - **Signal Output**: Digital signal for IR control

### **3. BT1 Header (2-pin)**
- **Location**: Bottom-left of board
- **Type**: 2-pin header (battery connection)
- **Potential Uses**:
  - **Battery Power**: Direct access to battery voltage
  - **Power Supply**: For external IR LED
  - **Voltage Levels**: 3.7V from LiPo battery

### **4. USB Port**
- **Location**: Bottom edge
- **Type**: USB connector
- **Potential Uses**:
  - **Power Supply**: 5V USB power
  - **Data Communication**: USB HID interface
  - **External Power**: For IR LED circuits

## 🔧 **Hardware Modification Options**

### **Option 1: Use P1 Header (8-pin)**
**Best Option - Most Pins Available**

**Required Components:**
- **IR LED**: 940nm infrared LED
- **Resistor**: Current limiting resistor (220Ω-1kΩ)
- **Transistor**: NPN transistor for current amplification
- **Jumper Wires**: To connect to P1 header

**Connection:**
```
P1 Pin 1 (3.3V) → Resistor → IR LED Anode
P1 Pin 2 (GPIO) → Transistor Base
IR LED Cathode → Transistor Collector
Transistor Emitter → P1 Pin 8 (GND)
```

### **Option 2: Use P2 Header (2-pin)**
**Simpler Option - Limited Pins**

**Required Components:**
- **IR LED**: 940nm infrared LED
- **Resistor**: Current limiting resistor
- **External Switch**: Manual IR control

**Connection:**
```
P2 Pin 1 (Power) → Resistor → IR LED Anode
IR LED Cathode → P2 Pin 2 (GND)
```

### **Option 3: Use BT1 Header (Battery)**
**Direct Battery Power**

**Required Components:**
- **IR LED**: 940nm infrared LED
- **Resistor**: Current limiting resistor
- **Voltage Regulator**: 3.3V regulator (if needed)

**Connection:**
```
BT1 Pin 1 (Battery+) → Resistor → IR LED Anode
IR LED Cathode → BT1 Pin 2 (Battery-)
```

## 🎯 **Recommended Approach**

### **Best Solution: P1 Header (8-pin)**

**Why P1 is Best:**
- **Most pins available** (8 pins)
- **Likely has GPIO pins** for software control
- **Power pins available** (3.3V, GND)
- **Debugging access** to FSP2C01915A chip

**Implementation Steps:**
1. **Identify P1 pin functions** using multimeter
2. **Find GPIO pin** that can be controlled by software
3. **Connect IR LED** to GPIO pin
4. **Add current limiting resistor** (220Ω-1kΩ)
5. **Test IR transmission** with software control

### **Hardware Requirements:**
- **IR LED**: 940nm, 5mm, 20-100mA
- **Resistor**: 220Ω-1kΩ (1/4W)
- **Transistor**: 2N2222 or similar NPN
- **Jumper Wires**: 22AWG
- **Multimeter**: To test pin functions

## 🔍 **Pin Function Testing**

### **Step 1: Identify Pin Functions**
```
P1 Pin 1: Test for 3.3V or 5V
P1 Pin 2: Test for GPIO (digital output)
P1 Pin 3: Test for GPIO (digital output)
P1 Pin 4: Test for GPIO (digital output)
P1 Pin 5: Test for GPIO (digital output)
P1 Pin 6: Test for GPIO (digital output)
P1 Pin 7: Test for GPIO (digital output)
P1 Pin 8: Test for GND
```

### **Step 2: Test GPIO Control**
- **Send software commands** to control GPIO pins
- **Measure voltage changes** on pins
- **Identify controllable pins** for IR LED

### **Step 3: Connect IR LED**
- **Connect IR LED** to controllable GPIO pin
- **Add current limiting resistor**
- **Test IR transmission** with software

## 🚀 **Implementation Plan**

### **Phase 1: Pin Analysis**
1. **Test P1 header pins** with multimeter
2. **Identify power pins** (3.3V, 5V, GND)
3. **Identify GPIO pins** (digital output)
4. **Map pin functions** to FSP2C01915A chip

### **Phase 2: Software Control**
1. **Send GPIO control commands** via USB
2. **Test pin voltage changes** with multimeter
3. **Identify controllable pins** for IR LED
4. **Develop IR LED control software**

### **Phase 3: Hardware Connection**
1. **Connect IR LED** to controllable GPIO pin
2. **Add current limiting resistor**
3. **Test IR LED activation** with software
4. **Verify IR signal transmission**

### **Phase 4: TV Control Testing**
1. **Test IR transmission** to Hisense TV
2. **Verify TV control** functionality
3. **Optimize IR signal strength**
4. **Complete TV control system**

## 🎯 **Expected Results**

**If successful:**
- ✅ **IR LED control** via software
- ✅ **IR signal transmission** to TV
- ✅ **Complete TV control** functionality
- ✅ **Hardware modification** working

**If not successful:**
- ❌ **Pins may not be controllable** via software
- ❌ **Different approach needed** (external IR blaster)
- ❌ **Hardware limitations** of FSP chip

## 🔧 **Next Steps**

1. **Test P1 header pins** with multimeter
2. **Identify controllable GPIO pins**
3. **Connect IR LED** to GPIO pin
4. **Test IR transmission** with software
5. **Verify TV control** functionality

**The P1 header is our best bet for adding IR LED control to the FSP board!**




