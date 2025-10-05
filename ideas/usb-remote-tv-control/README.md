# USB Remote TV Control Agent

## Overview
This project aims to create an intelligent agent system that can control a TV through a USB-connected remote control device. The system will enable automated TV control capabilities through a USB remote tagged with FSP2C01915A chip.

## Project Goals
- Develop an agent-based system for automated TV control
- Interface with USB HID remote control devices
- Support multiple TV brands and models through IR protocols
- Provide programmatic control over TV functions (power, volume, channels, etc.)
- Enable integration with smart home systems and voice assistants

## Key Features
- **USB HID Device Control**: Direct communication with USB remote control hardware
- **IR Protocol Support**: Support for NEC, RC5, RC6, and other IR protocols
- **Agent Intelligence**: AI-powered decision making for TV control
- **Multi-Brand Support**: Compatibility with major TV manufacturers
- **API Integration**: RESTful API for external system integration
- **Real-time Control**: Low-latency TV control operations

## Technical Architecture

### Hardware Components
- USB Remote Control with FSP2C01915A chip
- IR Transmitter/Receiver capabilities
- USB HID interface for computer communication

### Software Components
- **Agent System**: Core intelligence for TV control decisions
- **USB Driver**: Low-level USB HID communication
- **Protocol Handler**: IR signal encoding/decoding
- **API Layer**: External system integration
- **Configuration Manager**: Device and TV setup management

## Project Structure
```
usb-remote-tv-control/
├── hardware/           # Hardware specifications and components
├── software/           # Software components and modules
├── research/           # Technical research and documentation
├── docs/              # Project documentation
├── implementation/    # Setup and deployment guides
├── testing/           # Test cases and validation
└── whats_working/     # Working solutions and troubleshooting
```

## Getting Started
1. Review hardware specifications in `hardware/` directory
2. Study software architecture in `software/` directory
3. Follow implementation guide in `implementation/` directory
4. Run tests in `testing/` directory

## Status
🚧 **In Development** - Initial research and architecture phase

