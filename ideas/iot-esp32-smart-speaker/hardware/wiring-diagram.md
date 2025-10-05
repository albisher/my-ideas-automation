# ESP32 Smart Speaker Wiring Diagram

## Complete Wiring Connections

### ESP32 Pinout Reference
```
ESP32-DevKitC Pinout:
┌─────────────────────────────────┐
│ 3V3  │ 5V   │ GND  │ GND  │ 5V   │
│ EN   │ VIN  │ G23  │ G22  │ G1   │
│ G3   │ G0   │ G5   │ G18  │ G19  │
│ G21  │ G22  │ G23  │ G25  │ G26  │
│ G27  │ G14  │ G12  │ G13  │ G15  │
│ G2   │ G4   │ G16  │ G17  │ G32  │
│ G33  │ G35  │ G34  │ G36  │ G39  │
└─────────────────────────────────┘
```

### 1. I2S Audio Amplifier (MAX98357A) Connections
```
MAX98357A    →    ESP32
─────────────────────────
VCC          →    3.3V
GND          →    GND
BCLK         →    GPIO 26
LRC          →    GPIO 25
DIN          →    GPIO 27
```

### 2. I2S Microphone (INMP441) Connections
```
INMP441      →    ESP32
─────────────────────────
VDD          →    3.3V
GND          →    GND
WS           →    GPIO 25 (shared with amplifier LRC)
SD           →    GPIO 33
SCK          →    GPIO 32
```

### 3. Speaker Connections
```
Speaker      →    MAX98357A
─────────────────────────
Positive     →    OUT+
Negative     →    OUT-
```

### 4. Power Supply Connections
```
Power Supply →    ESP32
─────────────────────────
5V           →    VIN
GND          →    GND

Voltage Regulator (AMS1117-3.3V):
5V Input     →    VIN
3.3V Output  →    3.3V rail
GND          →    GND
```

### 5. Additional Components
```
LED Indicator:
LED Anode    →    GPIO 2 (through 220Ω resistor)
LED Cathode  →    GND

Push Button:
Button Pin   →    GPIO 0
Other Pin    →    GND

Status LED:
LED Anode    →    GPIO 4 (through 220Ω resistor)
LED Cathode  →    GND
```

## Complete Circuit Diagram

```
                    ESP32-DevKitC
                    ┌─────────────┐
                    │             │
    5V ────────────►│ VIN         │
                    │             │
                    │ GND         │◄─── GND
                    │             │
                    │ GPIO 26 ────┼───► BCLK ──── MAX98357A
                    │ GPIO 25 ────┼───► LRC  ──── MAX98357A
                    │ GPIO 27 ────┼───► DIN  ──── MAX98357A
                    │             │
                    │ 3.3V ───────┼───► VCC ──── MAX98357A
                    │             │
                    │ GPIO 32 ────┼───► SCK  ──── INMP441
                    │ GPIO 33 ────┼───► SD   ──── INMP441
                    │ GPIO 25 ────┼───► WS   ──── INMP441
                    │             │
                    │ 3.3V ───────┼───► VDD ──── INMP441
                    │             │
                    │ GPIO 2  ────┼───► LED (220Ω)
                    │ GPIO 4  ────┼───► Status LED (220Ω)
                    │ GPIO 0  ────┼───► Button
                    └─────────────┘
                            │
                            ▼
                    ┌─────────────┐
                    │ MAX98357A   │
                    │             │
                    │ OUT+ ───────┼───► Speaker (+)
                    │ OUT- ───────┼───► Speaker (-)
                    └─────────────┘
```

## Breadboard Layout

### Step 1: Power Rails
- Connect 5V power supply to red rail
- Connect GND to blue rail
- Connect 3.3V regulator output to second red rail

### Step 2: ESP32 Placement
- Place ESP32 in center of breadboard
- Connect VIN to 5V rail
- Connect GND to GND rail
- Connect 3.3V to 3.3V rail

### Step 3: Audio Components
- Place MAX98357A near ESP32
- Connect power and I2S signals
- Place INMP441 on opposite side
- Connect microphone signals

### Step 4: Speaker Connection
- Connect speaker to MAX98357A outputs
- Use jumper wires for audio connections
- Keep audio wires short to reduce noise

## Wiring Tips

### 1. Power Considerations
- Use separate power rails for digital and analog
- Add decoupling capacitors (100nF) near power pins
- Keep power wires short and thick

### 2. Audio Quality
- Use shielded cables for audio connections
- Keep audio components away from digital circuits
- Add ferrite beads on power lines

### 3. Signal Integrity
- Keep I2S signals short and parallel
- Avoid crossing power and signal lines
- Use ground planes where possible

### 4. Mechanical Considerations
- Secure all connections with proper connectors
- Use strain relief for external connections
- Plan for enclosure mounting points
