# Xiaomi Home Integration - Quick Start Guide

## For Your Home Assistant Setup

### Current Status
- **Home Assistant**: Running with basic configuration
- **Current Integrations**: Tapo, Google Cast, Google Assistant
- **Goal**: Add Xiaomi smart speaker with IR control

### Quick Installation Steps

#### 1. Install via HACS (Easiest)
```
Home Assistant → Settings → Add-ons → Add-on Store → Search "HACS" → Install
Restart Home Assistant
HACS → Integrations → Search "Xiaomi Home" → Install
```

#### 2. Add Integration
```
Settings → Devices & Services → Add Integration → Search "Xiaomi Home"
Click login link → Sign in with Xiaomi account → Select devices → Submit
```

#### 3. Verify Setup
```
Settings → Devices & Services → Configured → Xiaomi Home
Check that your smart speaker appears in the device list
```

### Expected New Entities

After integration, you should see:
- **Media Player**: `media_player.xiaomi_smart_speaker`
- **IR Remote**: `remote.xiaomi_smart_speaker_ir` 
- **IR Switches**: For each IR device you've set up
- **Sensors**: Device status and information

### Quick Test
1. Go to **Developer Tools** → **Services**
2. Search for `remote.send_command`
3. Test with your IR devices

### Configuration Files
No manual YAML configuration needed - the integration handles everything automatically.

### Next Steps
1. Install the integration
2. Test IR control
3. Create automations
4. Add to dashboard

**Time Required**: 15-30 minutes
**Difficulty**: Easy
**Result**: Full Xiaomi smart speaker integration with IR control
