# Xiaomi Home Integration - Complete Setup Guide

## Overview
The [Xiaomi Home Integration](https://github.com/XiaoMi/ha_xiaomi_home) is the official Home Assistant integration for Xiaomi devices, including smart speakers with IR control. This integration supports MIoT (Mi IoT) devices and provides comprehensive control over Xiaomi ecosystem devices.

## Prerequisites
- Home Assistant Core ≥ 2024.4.4
- Home Assistant Operating System ≥ 13.0
- Xiaomi account with devices already set up in Mi Home app
- Your Xiaomi smart speaker with IR should be connected to your Xiaomi account

## Installation Methods

### Method 1: HACS Installation (Recommended)
1. **Install HACS** (if not already installed):
   - Go to Home Assistant → Settings → Add-ons → Add-on Store
   - Search for "HACS" and install it
   - Restart Home Assistant

2. **Install Xiaomi Home Integration**:
   - Go to HACS → Integrations
   - Search for "Xiaomi Home"
   - Click "Install" and follow the prompts
   - Restart Home Assistant

### Method 2: Manual Installation
1. **Download the integration**:
   ```bash
   cd /config
   git clone https://github.com/XiaoMi/ha_xiaomi_home.git
   cd ha_xiaomi_home
   ./install.sh /config
   ```

2. **Restart Home Assistant**

### Method 3: Direct File Copy
1. Download the `custom_components/xiaomi_home` folder from the repository
2. Copy it to your Home Assistant's `config/custom_components` directory
3. Restart Home Assistant

## Configuration Steps

### Step 1: Add Integration
1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **"Xiaomi Home"**
3. Click on it to start the configuration

### Step 2: Login Process
1. **Click the login link** provided in the integration setup
2. **Sign in with your Xiaomi account** credentials
3. **Authorize the integration** when prompted
4. **Return to Home Assistant** after successful login

### Step 3: Select Devices
1. A dialog titled **"Select Home and Devices"** will appear
2. **Choose your home** that contains your Xiaomi devices
3. **Select the devices** you want to integrate (including your smart speaker with IR)
4. **Click "Submit"** to complete the setup

### Step 4: Verify Integration
1. Go to **Settings** → **Devices & Services** → **Configured**
2. You should see **"Xiaomi Home"** in the list
3. Click on it to see your connected devices

## Advanced Configuration

### Multiple Account Support
To add devices from multiple Xiaomi accounts:
1. Go to **Settings** → **Devices & Services** → **Configured** → **Xiaomi Home**
2. Click **"Add Hub"**
3. Follow the login process for the additional account
4. Select devices from the new account

### Update Configurations
To modify settings:
1. Go to **Settings** → **Devices & Services** → **Configured** → **Xiaomi Home**
2. Click **"Configure"**
3. Update user nicknames, device lists, or other settings as needed

### Debug Mode
To manually send action commands:
1. Go to **Settings** → **Devices & Services** → **Configured** → **Xiaomi Home**
2. Click **"Configure"**
3. Enable **"Debug mode for action"**

## Expected Results

### Smart Speaker Integration
Your Xiaomi smart speaker with IR should appear as:
- **Media Player entity** for audio control
- **IR Remote entities** for each IR device you've set up
- **Switch entities** for power control of IR devices
- **Sensor entities** for device status

### IR Control Capabilities
- **Voice commands** through the speaker
- **Home Assistant automations** controlling IR devices
- **Dashboard buttons** for manual IR control
- **Scripts** for complex IR sequences

## Configuration Example

### Basic Configuration (Auto-generated)
The integration will automatically create entities. No manual YAML configuration is required for basic setup.

### Custom Automations
```yaml
# Example automation for IR control
automation:
  - alias: "Turn on TV when arriving home"
    trigger:
      - platform: state
        entity_id: person.your_name
        to: 'home'
    action:
      - service: remote.send_command
        target:
          entity_id: remote.xiaomi_smart_speaker_ir
        data:
          command: "power"
          device: "tv"

# Example script for IR control
script:
  tv_control:
    alias: "TV Control"
    sequence:
      - service: remote.send_command
        target:
          entity_id: remote.xiaomi_smart_speaker_ir
        data:
          command: "{{ command }}"
          device: "{{ device }}"
```

## Troubleshooting

### Common Issues
1. **Login fails**: Ensure you're using the correct Xiaomi account
2. **Devices not appearing**: Check if devices are properly set up in Mi Home app
3. **IR commands not working**: Verify IR devices are paired with the speaker in Mi Home app

### Debug Steps
1. **Check Home Assistant logs** for error messages
2. **Verify device connectivity** in Mi Home app
3. **Restart the integration** if needed
4. **Check network connectivity** between Home Assistant and Xiaomi devices

### Security Considerations
- Integration uses OAuth 2.0 for secure authentication
- Your Xiaomi password is not stored in Home Assistant
- Device tokens are stored locally in Home Assistant configuration
- You can revoke access via Mi Home app if needed

## Next Steps After Integration

1. **Test IR control** through Home Assistant interface
2. **Create automations** for your IR devices
3. **Add dashboard cards** for easy control
4. **Set up voice commands** through Google Assistant integration
5. **Create scripts** for complex IR sequences

## Benefits of This Integration

- ✅ **Native Home Assistant support** for Xiaomi devices
- ✅ **IR control** through Home Assistant interface
- ✅ **Automation capabilities** for IR devices
- ✅ **Voice control** integration
- ✅ **Multiple account support**
- ✅ **Regular updates** and maintenance
- ✅ **Official Xiaomi support**

This integration provides the most comprehensive way to integrate your Xiaomi smart speaker with IR control into Home Assistant, giving you full control over your IR devices through the Home Assistant interface.
