# Google Home + Home Assistant Integration - Implementation Checklist

## Pre-Implementation Status ✅

### Infrastructure Ready
- ✅ Home Assistant running on port 8123
- ✅ Matter server running on ports 5580/5581
- ✅ Docker networks configured
- ✅ Home Assistant accessible at http://localhost:8123

### Configuration Complete
- ✅ Matter integration removed from YAML (UI setup required)
- ✅ Home Assistant restarted without errors
- ✅ All containers running properly

## Implementation Steps

### Step 1: Access Home Assistant UI
- [ ] Open browser to http://localhost:8123
- [ ] Log in to Home Assistant
- [ ] Navigate to Settings > Devices & Services

### Step 2: Add Matter Integration
- [ ] Click "+ Add Integration"
- [ ] Search for "Matter"
- [ ] Select Matter integration
- [ ] Configure bridge settings
- [ ] Set bridge name (e.g., "Home Assistant Bridge")
- [ ] Use default ports (5540/5541)

### Step 3: Expose Entities
- [ ] Go to Matter integration settings
- [ ] Click "Expose" tab
- [ ] Select entities to control via Google Home:
  - [ ] Lights
  - [ ] Switches
  - [ ] Sensors
  - [ ] Cameras
  - [ ] Other devices

### Step 4: Get Pairing Information
- [ ] Note QR code for pairing
- [ ] Note 8-digit pairing code
- [ ] Note bridge IP address

### Step 5: Configure Google Home
- [ ] Open Google Home app
- [ ] Tap "+" (Add device)
- [ ] Select "Set up device"
- [ ] Choose "Works with Google"
- [ ] Look for "Matter" or "Local devices"
- [ ] Scan QR code OR enter setup code

### Step 6: Test Functionality
- [ ] Verify Google Home discovers Home Assistant devices
- [ ] Test basic voice commands:
  - [ ] "Hey Google, turn on [device name]"
  - [ ] "Hey Google, turn off [device name]"
  - [ ] "Hey Google, set [device] to [value]"
- [ ] Check response times (< 2 seconds)
- [ ] Verify local control (no internet required)

## Troubleshooting Checklist

### If Matter Integration Not Available
- [ ] Check Home Assistant version (requires 2023.1+)
- [ ] Update Home Assistant if needed
- [ ] Restart Home Assistant container
- [ ] Check integration is not already added

### If Google Home Can't Find Devices
- [ ] Ensure both devices on same network
- [ ] Check firewall settings
- [ ] Verify Matter server running: `docker ps | grep matter`
- [ ] Test network connectivity
- [ ] Restart Google Home app

### If Pairing Fails
- [ ] Check pairing code is correct
- [ ] Ensure QR code is clear and readable
- [ ] Try setup code instead of QR code
- [ ] Restart both Home Assistant and Google Home app
- [ ] Check network connectivity

## Success Criteria

### Basic Functionality
- [ ] Google Home discovers Home Assistant devices
- [ ] Voice commands work for device control
- [ ] Response times under 2 seconds
- [ ] Local control without cloud dependency

### Advanced Features
- [ ] Scenes work via voice commands
- [ ] Multiple devices can be controlled together
- [ ] Complex commands work (e.g., "turn on all lights")
- [ ] Device status can be queried

## Alternative: Google Assistant Integration

### If Matter Integration Doesn't Work
- [ ] Consider Nabu Casa Cloud subscription ($6.50/month)
- [ ] Enable Google Assistant in HA Cloud settings
- [ ] Expose entities to Google Assistant
- [ ] Link via Google Home app

### If Manual Setup Preferred
- [ ] Create Google Cloud Platform project
- [ ] Configure OAuth2 credentials
- [ ] Set up Google Actions for Smart Home
- [ ] Configure Home Assistant Google Assistant integration

## Documentation

### Record Working Configuration
- [ ] Note which entities work via Google Home
- [ ] Document any limitations or issues
- [ ] Create backup of working configuration
- [ ] Record successful voice commands

### Update Project Documentation
- [ ] Add Google Home integration to project docs
- [ ] Document setup process for future reference
- [ ] Note any custom configurations made
- [ ] Create troubleshooting guide

## Next Steps After Implementation

### Testing Phase
- [ ] Test all exposed entities
- [ ] Verify voice command accuracy
- [ ] Check response times
- [ ] Test offline functionality (Matter)

### Optimization Phase
- [ ] Configure device groups in Google Home
- [ ] Set up scenes and routines
- [ ] Create Home Assistant automations
- [ ] Optimize voice command phrases

### Maintenance Phase
- [ ] Monitor integration stability
- [ ] Update configurations as needed
- [ ] Document any issues or solutions
- [ ] Plan for future enhancements

## Expected Timeline

- **Setup**: 15-30 minutes
- **Testing**: 15-30 minutes
- **Optimization**: 30-60 minutes
- **Total**: 1-2 hours

## Success Metrics

- ✅ Google Home controls Home Assistant devices
- ✅ Voice commands work reliably
- ✅ Response times under 2 seconds
- ✅ Local control without cloud dependency
- ✅ Enhanced privacy and security
- ✅ No ongoing costs (Matter integration)

This checklist ensures a systematic approach to implementing Google Home + Home Assistant integration with Home Assistant as the master controller.
