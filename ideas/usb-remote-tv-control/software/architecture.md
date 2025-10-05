# Software Architecture

## System Overview
The USB Remote TV Control Agent is designed as a modular system with clear separation of concerns between hardware interface, protocol handling, and intelligent control logic.

## Core Components

### 1. Agent System (`software/agent/`)
**Purpose**: Core intelligence and decision-making for TV control operations

**Key Modules**:
- `tv_controller.py`: Main agent class for TV control logic
- `command_processor.py`: Process and validate control commands
- `state_manager.py`: Track TV state and control history
- `learning_engine.py`: Machine learning for improved control accuracy

**Responsibilities**:
- Interpret user commands and intents
- Make intelligent decisions about TV control
- Learn from user behavior and preferences
- Handle complex control sequences

### 2. USB Driver (`software/usb-driver/`)
**Purpose**: Low-level communication with USB HID remote control device

**Key Modules**:
- `usb_hid_interface.py`: Direct USB HID communication
- `device_manager.py`: USB device discovery and management
- `hid_report_handler.py`: Process HID reports from device
- `usb_communication.py`: Raw USB data transfer

**Dependencies**:
- `pyusb`: Python USB library
- `libusb`: Low-level USB access
- `hidapi`: HID device interface

### 3. Protocol Handler (`software/protocol-handler/`)
**Purpose**: IR signal encoding/decoding and protocol management

**Key Modules**:
- `ir_protocols.py`: Support for various IR protocols (NEC, RC5, RC6)
- `signal_encoder.py`: Convert commands to IR signals
- `signal_decoder.py`: Decode received IR signals
- `protocol_manager.py`: Manage multiple protocol support

**Supported Protocols**:
- NEC Protocol (most common for TVs)
- RC5 Protocol (Philips standard)
- RC6 Protocol (Philips extended)
- Pronto Hex format
- Custom manufacturer protocols

### 4. API Layer (`software/api/`)
**Purpose**: External system integration and RESTful API

**Key Modules**:
- `rest_api.py`: RESTful API endpoints
- `websocket_handler.py`: Real-time WebSocket communication
- `command_interface.py`: Standardized command interface
- `authentication.py`: API security and authentication

**API Endpoints**:
- `POST /api/tv/power` - Power on/off TV
- `POST /api/tv/volume` - Adjust volume
- `POST /api/tv/channel` - Change channel
- `POST /api/tv/input` - Change input source
- `GET /api/tv/status` - Get current TV state

## Data Flow

```
User Command → Agent System → Command Processor → Protocol Handler → USB Driver → Hardware
     ↑                                                                              ↓
     ← State Manager ← Status Updates ← HID Reports ← USB Communication ← Device
```

## Configuration Management
- **Device Configuration**: USB device settings and capabilities
- **TV Configuration**: TV brand, model, and IR protocol settings
- **Agent Configuration**: Learning parameters and behavior settings
- **API Configuration**: Security settings and endpoint configuration

## Error Handling
- **USB Communication Errors**: Device disconnection, communication failures
- **Protocol Errors**: Invalid IR signals, unsupported protocols
- **Agent Errors**: Command interpretation failures, state inconsistencies
- **API Errors**: Authentication failures, invalid requests

## Performance Considerations
- **Latency**: Sub-100ms response time for control commands
- **Reliability**: 99.9% command success rate
- **Scalability**: Support for multiple TV devices
- **Resource Usage**: Minimal CPU and memory footprint

