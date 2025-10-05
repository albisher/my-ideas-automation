# Xiaomi Device Setup Guide for Hisense TV Control

## Overview
This guide will help you set up your Xiaomi device (192.168.68.62) to control your Hisense TV through Home Assistant.

## Prerequisites
- Xiaomi device connected to your network
- Home Assistant running
- Xiaomi device token (32 characters)

## Step 1: Get Your Xiaomi Device Token

### Method 1: From Xiaomi Home App
1. Open the Xiaomi Home app on your phone
2. Find your device in the app
3. Go to device settings
4. Look for "Device Token" or "Local Token"
5. Copy the 32-character token

### Method 2: Using the Setup Script
1. Run the setup script:
   ```bash
   cd /Users/amac/myIdeas/homeassistant/config/scripts
   python3 xiaomi_setup.py
   ```
2. Follow the prompts to discover your device
3. Enter the token when prompted

## Step 2: Update Configuration

### Update secrets.yaml
Edit `/Users/amac/myIdeas/homeassistant/config/secrets.yaml`:
```yaml
# Xiaomi IR Remote (L05G) - Your device IP
xiaomi_ir_host: "192.168.68.62"  # Your actual device IP
xiaomi_ir_token: "YOUR_32_CHARACTER_TOKEN_HERE"  # Replace with your actual token
```

### Verify configuration.yaml
The configuration should include:
```yaml
# Xiaomi Miio integration (official) - Configure via YAML
xiaomi_miio:
  - host: !secret xiaomi_ir_host
    token: !secret xiaomi_ir_token
    name: "Xiaomi Smart Speaker"

# Xiaomi IR Remote for TV control
remote:
  - platform: xiaomi_miio
    host: !secret xiaomi_ir_host
    token: !secret xiaomi_ir_token
    name: "Xiaomi IR Remote"
    commands:
      # Hisense TV IR Commands
      hisense_tv_power: "raw:2600500000012..."
      hisense_tv_volume_up: "raw:2600500000012..."
      hisense_tv_volume_down: "raw:2600500000012..."
      hisense_tv_channel_up: "raw:2600500000012..."
      hisense_tv_channel_down: "raw:2600500000012..."
      hisense_tv_input: "raw:2600500000012..."
      hisense_tv_menu: "raw:2600500000012..."
      hisense_tv_back: "raw:2600500000012..."
      hisense_tv_ok: "raw:2600500000012..."
      hisense_tv_up: "raw:2600500000012..."
      hisense_tv_down: "raw:2600500000012..."
      hisense_tv_left: "raw:2600500000012..."
      hisense_tv_right: "raw:2600500000012..."
```

## Step 3: Learn IR Commands

### Using the Setup Script
1. Run the setup script to learn IR commands:
   ```bash
   python3 xiaomi_setup.py
   ```
2. Follow the prompts to learn each IR command
3. Point your Hisense TV remote at the Xiaomi device
4. Press the corresponding buttons when prompted

### Manual Learning
1. Go to Home Assistant → Settings → Devices & Services
2. Find your Xiaomi IR Remote device
3. Use the "Learn Command" feature
4. Point your Hisense TV remote at the Xiaomi device
5. Press the button you want to learn
6. Repeat for all TV controls

## Step 4: Test the Setup

### Test Basic Connection
1. Go to Home Assistant → Settings → Devices & Services
2. Check if the Xiaomi device is listed
3. Verify the device status is "Online"

### Test IR Commands
1. Go to the Hisense TV dashboard
2. Try the power button first
3. Test volume controls
4. Test channel controls
5. Test navigation controls

## Troubleshooting

### Device Not Found
- Check if the device is on the network: `ping 192.168.68.62`
- Verify the IP address in secrets.yaml
- Check if the device is responding on port 54321

### Token Issues
- Verify the token is exactly 32 characters
- Check if the token is correct in the Xiaomi Home app
- Try regenerating the token in the app

### IR Commands Not Working
- Ensure the Xiaomi device is pointing at the TV
- Check if the IR commands were learned correctly
- Try relearning the commands
- Verify the TV is in range of the IR signal

### Home Assistant Integration Issues
- Check the Home Assistant logs for errors
- Restart Home Assistant after configuration changes
- Verify the YAML syntax is correct

## Step 5: Automation Setup

### Basic Automations
The following automations are already configured:
- Turn on TV when arriving home
- Turn off TV when leaving home
- Morning routine (7:00 AM)
- Evening routine (7:00 PM)

### Custom Automations
You can create custom automations using:
- Time-based triggers
- Presence detection
- Voice commands
- Button presses

## Step 6: Dashboard Access

### Access the Dashboard
1. Go to Home Assistant → Overview
2. Look for "Hisense TV Control" dashboard
3. Or navigate to: `http://localhost:8123/hisense-tv-dashboard`

### Dashboard Features
- Power control
- Volume control
- Channel control
- Navigation controls
- Device status
- IR command testing

## Troubleshooting Commands

### Check Device Status
```bash
# Check if device is online
ping 192.168.68.62

# Check if port 54321 is open
nc -zv 192.168.68.62 54321
```

### Check Home Assistant Logs
```bash
# View Home Assistant logs
docker-compose logs homeassistant

# Follow logs in real-time
docker-compose logs -f homeassistant
```

### Test IR Commands
```bash
# Test IR command via Home Assistant API
curl -X POST "http://localhost:8123/api/services/remote/send_command" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "remote.xiaomi_ir_remote", "command": "hisense_tv_power"}'
```

## Support

If you encounter issues:
1. Check the Home Assistant logs
2. Verify the device configuration
3. Test the IR commands manually
4. Check the network connectivity
5. Verify the token is correct

## Next Steps

Once everything is working:
1. Set up voice control with Google Assistant
2. Create custom automations
3. Add more IR devices
4. Set up scenes for different TV modes
5. Integrate with other smart home devices
