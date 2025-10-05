# Hardware Research Findings

## Research Summary

Based on extensive research using web search tools, here are the findings for both universal remotes:

## FSP2C01915A Chip Research

### ❌ **Limited Documentation Found**
- **No specific datasheet** found for FSP2C01915A chip
- **No pinout schematics** available
- **No technical documentation** located
- **Appears to be proprietary/OEM** component

### 🔍 **What We Know:**
- **Board Numbers**: SG-G7v1.1, ZY1022v1.1, 20210531, fsp2c01915A
- **Integration**: Found in Apple Inc. - Albisher Keyboard devices
- **Functionality**: USB HID communication working
- **IR Processing**: Commands accepted but no physical IR transmission

### 📋 **Technical Characteristics:**
- **USB HID Controller**: Processes IR commands via USB
- **Missing Component**: No physical IR LED/transmitter
- **Communication**: Works with multiple report formats (0x01-0x05)
- **Protocol Support**: NEC, RC5, RC6 IR protocols

## eQ Brand Remote Research

### ✅ **Documentation Found**
- **eQ-3 HM-RC-12-B**: 12-button radio remote control
- **Auria EQ2688**: TV model with remote manual
- **Universal Remote WIR35001 EQ01**: Comprehensive user manual available

### 🔍 **eQ Remote Capabilities:**
- **Range**: Up to 200 meters (radio frequency)
- **Battery**: AAA batteries
- **Features**: 12-button design, multiple device support
- **Programming**: Auto code search and direct code entry

### 📋 **Available Manuals:**
1. **eQ-3 HM-RC-12-B Manual**: [manua.ls](https://www.manua.ls/eq-3/hm-rc-12-b/manual)
2. **Auria EQ2688 Manual**: [manua.ls](https://www.manua.ls/auria/eq2688/manual)
3. **Universal Remote WIR35001 EQ01**: [directutor.com](https://www.directutor.com/content/user-manual-universal-remote-wir35001-eq01)

## Universal Remote Control Circuit Research

### 🔧 **General Circuit Board Information:**
- **IR LED Connection**: Standard IR LEDs require specific pinout connections
- **USB HID Interface**: Standard USB HID protocol for communication
- **Power Requirements**: Typically 3.3V or 5V for IR LEDs
- **Signal Timing**: Precise timing requirements for IR transmission

### 📋 **Common IR LED Specifications:**
- **Wavelength**: 940nm (infrared)
- **Forward Voltage**: 1.2V typical
- **Forward Current**: 20-100mA
- **Viewing Angle**: 15-30 degrees
- **Carrier Frequency**: 38kHz for most TV remotes

## Hardware Analysis

### FSP2C01915A Chip Status:
- ✅ **USB HID Communication**: Working
- ✅ **IR Command Processing**: Working
- ❌ **Physical IR Transmission**: Missing IR LED
- ❌ **Technical Documentation**: Not available

### eQ Remote Status:
- ✅ **Documentation Available**: Multiple manuals found
- ✅ **Programming Instructions**: Available
- ❓ **USB Connection**: Not confirmed in current scan
- ❓ **IR Capabilities**: Need to verify with actual device

## Recommendations

### 1. **FSP2C01915A Chip Solution:**
- **Add IR LED**: Wire 940nm IR LED to chip output pins
- **Power Supply**: Ensure proper voltage (3.3V or 5V)
- **Signal Amplification**: May need transistor for current amplification
- **Testing**: Verify IR signal transmission with IR receiver

### 2. **eQ Remote Solution:**
- **Locate Device**: Find the eQ remote in your setup
- **Identify Model**: Check for exact model number
- **Programming**: Use available manuals for Hisense TV programming
- **Testing**: Test IR transmission to Hisense TV

### 3. **Hybrid Solution:**
- **Use FSP chip**: For command processing and USB communication
- **External IR blaster**: For actual IR signal transmission
- **Integration**: Connect IR blaster to FSP chip output

## Next Steps

1. **Locate eQ Remote**: Find the eQ brand remote in your setup
2. **Identify Model**: Check for model number and branding
3. **Test eQ Remote**: Verify IR transmission capabilities
4. **Hardware Modification**: Consider adding IR LED to FSP chip
5. **Integration Testing**: Test complete system with Hisense TV

## Status: Research Complete ✅

**Key Findings:**
- FSP2C01915A chip lacks physical IR transmitter
- eQ remote documentation available
- Hardware modification needed for FSP chip
- eQ remote may provide alternative solution

**Priority**: Test eQ remote and consider hardware modifications
