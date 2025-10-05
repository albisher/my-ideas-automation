# BroadLink RM4 Pro - Home Assistant Setup Guide

## Quick Setup Steps

### 1. Hardware Setup
- Purchase BroadLink RM4 Pro (~$30-50)
- Connect to power and WiFi using BroadLink app
- Note the device IP address

### 2. Home Assistant Integration
```yaml
# configuration.yaml
broadlink:
  host: 192.168.1.100  # Your RM4 Pro IP
  mac: 'AA:BB:CC:DD:EE:FF'  # Device MAC
  type: rm4_pro
  timeout: 15
```

### 3. Learn IR Commands
1. Go to Home Assistant → Developer Tools → Services
2. Call `broadlink.learn` service
3. Point your remote at RM4 Pro and press button
4. Copy the learned code

### 4. Create IR Controls
```yaml
# Create scripts for IR commands
script:
  tv_power:
    alias: "TV Power"
    sequence:
      - service: broadlink.send
        data:
          host: 192.168.1.100
          packet: "your_learned_ir_code_here"
```

### 5. Add to Dashboard
- Create buttons for each IR command
- Use the script entities in your Lovelace UI

## Advantages
- ✅ Native Home Assistant support
- ✅ No coding required
- ✅ Works with any IR device
- ✅ 360-degree coverage
- ✅ Reliable and well-documented

## Cost: ~$30-50 + 1-2 hours setup time
