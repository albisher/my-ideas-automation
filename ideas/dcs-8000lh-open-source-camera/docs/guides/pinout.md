# DCS-8000LH Pinout and Connector Information

## External Connectors

### Power Connector
- **Type**: DC barrel jack (center positive)
- **Voltage**: 5V DC
- **Current**: 1A maximum
- **Polarity**: Center positive, outer negative

### Ethernet Port
- **Type**: RJ45 8P8C
- **Standard**: 10/100 Mbps
- **Pinout**: Standard Ethernet T568B
  - Pin 1: White/Orange (TX+)
  - Pin 2: Orange (TX-)
  - Pin 3: White/Green (RX+)
  - Pin 4: Blue (not used)
  - Pin 5: White/Blue (not used)
  - Pin 6: Green (RX-)
  - Pin 7: White/Brown (not used)
  - Pin 8: Brown (not used)

### Reset Button
- **Type**: Tactile switch
- **Function**: Hardware reset
- **Location**: Bottom of camera
- **Operation**: Press and hold for 10+ seconds

## Internal Connectors

### Serial Console (UART)
**✅ Confirmed pinout from camera image**

- **Type**: 4-pin header (exposed on camera base)
- **Voltage**: 3.3V logic
- **Baud Rate**: 115200 bps (typical)
- **Pinout** (confirmed from camera image):
  - Pin 1: 3.3V (VCC)
  - Pin 2: TX (camera to PC)
  - Pin 3: RX (PC to camera)
  - Pin 4: GND (Ground)

## FTDI USB Connection with Color Coding

### Adafruit FTDI Friend Pinout
```
Adafruit FTDI Friend (6-pin header):
┌─────────────────┐
│ 1 2 3 4 5 6     │
│ │ │ │ │ │ │     │
│ │ │ │ │ │ │     │
│ │ │ │ │ │ │     │
└─────────────────┘

Pin 1: VCC (3.3V)     - RED wire
Pin 2: GND            - BLACK wire  
Pin 3: CTS            - Not used
Pin 4: TX             - YELLOW wire
Pin 5: RX             - GREEN wire
Pin 6: RTS            - Not used
```

### DCS-8000LH Camera UART Pads
```
Camera UART Pads (4-pin header - CONFIRMED from camera image):
┌─────────────────┐
│ 1 2 3 4         │
│ │ │ │ │         │
│ │ │ │ │         │
│ │ │ │ │         │
└─────────────────┘

Pin 1: 3.3V (VCC)     - RED wire
Pin 2: TX (Camera)    - YELLOW wire
Pin 3: RX (Camera)    - GREEN wire
Pin 4: GND (Ground)   - BLACK wire
```

### Color-Coded Wiring Diagram (CORRECTED)
```
Adafruit FTDI Friend    DCS-8000LH Camera
┌─────────────────┐     ┌─────────────────┐
│ Pin 1: VCC      │─────│ Pin 1: 3.3V     │  RED wire
│ (RED wire)      │     │ (VCC)           │
│                 │     │                 │
│ Pin 2: GND      │─────│ Pin 4: GND      │  BLACK wire
│ (BLACK wire)    │     │ (Ground)        │
│                 │     │                 │
│ Pin 4: TX       │─────│ Pin 3: RX       │  YELLOW wire
│ (YELLOW wire)   │     │ (Camera RX)     │
│                 │     │                 │
│ Pin 5: RX       │─────│ Pin 2: TX       │  GREEN wire
│ (GREEN wire)    │     │ (Camera TX)     │
└─────────────────┘     └─────────────────┘
```

### Wire Color Guide (CORRECTED)
- **RED**: VCC (3.3V power) - Always connect first
- **BLACK**: GND (Ground) - Always connect second  
- **YELLOW**: TX from FTDI to RX on camera (Pin 3)
- **GREEN**: RX from FTDI to TX on camera (Pin 2)

### Connection Steps with Colors (CORRECTED)
1. **Power Off**: Ensure camera is powered off
2. **Connect RED**: Connect RED wire (FTDI VCC to Camera Pin 1 - 3.3V)
3. **Connect BLACK**: Connect BLACK wire (FTDI GND to Camera Pin 4 - GND)
4. **Connect YELLOW**: Connect YELLOW wire (FTDI TX to Camera Pin 3 - RX)
5. **Connect GREEN**: Connect GREEN wire (FTDI RX to Camera Pin 2 - TX)
6. **Power On**: Power on camera and test connection

### WiFi Antenna
- **Type**: Internal PCB antenna
- **Frequency**: 2.4GHz
- **Connector**: Soldered to PCB
- **Modification**: External antenna possible with soldering

### Camera Module
- **Type**: Integrated CMOS sensor
- **Interface**: MIPI CSI (likely)
- **Resolution**: 1280x720
- **Lens**: Fixed focus

## LED Indicators

### Power LED
- **Color**: Green/Blue
- **Function**: Power status indication
- **Behavior**:
  - Solid: Power on, normal operation
  - Blinking: Boot process
  - Off: Power off

### WiFi LED
- **Color**: Amber/Orange
- **Function**: WiFi connection status
- **Behavior**:
  - Solid: Connected to network
  - Blinking: Searching for network
  - Off: WiFi disabled

### Status LED
- **Color**: Red/Blue
- **Function**: System status
- **Behavior**:
  - Solid: Recording/streaming
  - Blinking: Motion detection
  - Off: Standby

## Internal Components

### Main PCB Layout
```
┌─────────────────────────────────┐
│  [Power Connector]              │
│                                 │
│  [Ethernet Port]                │
│                                 │
│  [SoC] [RAM] [Flash]            │
│                                 │
│  [WiFi Module] [Camera Module]  │
│                                 │
│  [Reset Button] [LEDs]          │
└─────────────────────────────────┘
```

### Component Locations
- **SoC**: Central processing unit
- **RAM**: System memory
- **Flash**: Firmware storage
- **WiFi Module**: 802.11n radio
- **Camera Module**: CMOS sensor and lens
- **Power Regulators**: Voltage conversion
- **Crystal Oscillators**: Clock generation

## Debugging Interfaces

### Serial Console Access
**⚠️ Hardware modification required**

1. **Locate UART Pads**: Look for 4-pin header or test points
2. **Identify Pins**: Use multimeter to find VCC, GND, TX, RX
3. **Connect Adapter**: Use USB-to-TTL adapter (3.3V)
4. **Configure Terminal**: 115200 bps, 8N1, no flow control

### JTAG Interface
- **Availability**: Not typically exposed
- **Access**: Requires PCB modification
- **Use**: Low-level debugging and recovery

## Power Distribution

### Voltage Rails
- **5V**: Input from power adapter
- **3.3V**: Main logic voltage
- **1.8V**: SoC core voltage
- **1.2V**: RAM voltage

### Power Consumption
- **Idle**: ~1-2W
- **Active**: ~3-5W
- **Peak**: ~6W (during boot)

## Mechanical Considerations

### Enclosure
- **Material**: Plastic housing
- **Sealing**: IP65 weather resistance
- **Mounting**: Wall/ceiling bracket included

### Thermal Management
- **Heat Sinks**: Passive cooling
- **Ventilation**: Natural convection
- **Temperature**: Operating range 0-40°C

## Modification Points

### Serial Console Installation
1. **Locate UART Pads**: Find 4-pin header or test points
2. **Solder Header**: Install 4-pin header
3. **Connect Adapter**: USB-to-TTL adapter
4. **Test Connection**: Verify console access

### External Antenna
1. **Locate Antenna Point**: Find WiFi antenna connection
2. **Remove Internal**: Desolder internal antenna
3. **Install Connector**: Add SMA connector
4. **Route Cable**: Connect external antenna

### Power LED Modification
1. **Identify LED**: Find power status LED
2. **Add Resistor**: Current limiting resistor
3. **Connect External**: Route to external indicator

## Safety Warnings

### Electrical Safety
- **High Voltage**: AC input requires caution
- **Low Voltage**: 3.3V/5V generally safe
- **ESD Protection**: Use anti-static precautions

### Physical Safety
- **Sharp Components**: Be careful with metal parts
- **Heat**: Some components may be hot
- **Fumes**: Soldering produces harmful fumes

## Tools Required

### Basic Tools
- Multimeter
- Soldering iron
- Solder wire
- Wire strippers
- Screwdrivers

### Advanced Tools
- Oscilloscope
- Logic analyzer
- JTAG programmer
- Hot air station

## Troubleshooting

### Common Issues
- **No Serial Output**: Check baud rate and connections
- **Power Issues**: Verify voltage levels
- **WiFi Problems**: Check antenna connections
- **Boot Failures**: Verify firmware integrity

### Debugging Steps
1. **Check Connections**: Verify all connections
2. **Measure Voltages**: Use multimeter
3. **Monitor Console**: Watch boot messages
4. **Test Components**: Individual component testing
