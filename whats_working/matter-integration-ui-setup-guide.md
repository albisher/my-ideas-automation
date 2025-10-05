# Matter Integration UI Setup Guide

## Current Status
- ✅ Matter server container running (ports 5580/5581)
- ✅ Home Assistant container running without errors
- ✅ Network connectivity between containers established
- ⏳ Matter integration needs to be configured via UI

## Step-by-Step Setup Instructions

### Step 1: Access Home Assistant UI
1. Open browser and navigate to: `http://localhost:8123`
2. Log in to Home Assistant
3. Navigate to **Settings** > **Devices & Services**

### Step 2: Add Matter Integration
1. Click **"+ Add Integration"** button
2. Search for **"Matter"** in the integration list
3. Select **Matter** integration
4. Click **"Configure"**

### Step 3: Configure Matter Bridge
1. **Bridge Name**: Enter a name like "Home Assistant Bridge"
2. **Network Port**: Leave default (5540)
3. **Commissioning Port**: Leave default (5541)
4. Click **"Submit"**

### Step 4: Expose Entities to Matter
1. After Matter integration is added, click on it
2. Go to **"Expose"** tab
3. Select entities you want to control via Google Home:
   - Lights
   - Switches
   - Sensors
   - Cameras
   - Other devices

### Step 5: Get Matter Bridge Information
1. In the Matter integration settings
2. Look for **"Matter Bridge"** section
3. Note down:
   - **QR Code** for pairing
   - **Pairing Code** (8-digit number)
   - **Bridge IP Address**

## Google Home Setup

### Step 1: Open Google Home App
1. Open Google Home app on your phone
2. Tap **"+"** (Add device)
3. Select **"Set up device"**
4. Choose **"Works with Google"**

### Step 2: Add Matter Device
1. Look for **"Matter"** or **"Local devices"** option
2. Select **"Matter"**
3. Choose **"Scan QR code"** or **"Enter setup code"**

### Step 3: Pair with Home Assistant
1. **Option A - QR Code**:
   - Scan the QR code from Home Assistant Matter bridge
   
2. **Option B - Setup Code**:
   - Enter the 8-digit pairing code from Home Assistant

### Step 4: Verify Connection
1. Google Home should discover Home Assistant devices
2. Test basic controls (turn lights on/off)
3. Verify voice commands work

## Troubleshooting

### If Matter Integration Not Available
1. Check Home Assistant version (requires 2023.1+)
2. Update Home Assistant if needed
3. Restart Home Assistant container

### If Google Home Can't Find Matter Devices
1. Ensure both devices on same network
2. Check firewall settings
3. Verify Matter server is running: `docker ps | grep matter`
4. Test network connectivity

### If Pairing Fails
1. Check pairing code is correct
2. Ensure QR code is clear and readable
3. Try using setup code instead of QR code
4. Restart both Home Assistant and Google Home app

## Expected Results

### After Successful Setup
- ✅ Google Home can discover Home Assistant devices
- ✅ Voice commands work for device control
- ✅ Fast response times (< 1 second)
- ✅ Local control without cloud dependency
- ✅ Enhanced privacy and security

### Device Control Examples
- "Hey Google, turn on the living room light"
- "Hey Google, set the thermostat to 72 degrees"
- "Hey Google, show me the camera feed"

## Alternative: Google Assistant Integration

If Matter integration doesn't work or has limitations, consider Google Assistant integration:

### Option A: Nabu Casa Cloud (Easiest)
1. Subscribe to Home Assistant Cloud
2. Enable Google Assistant in cloud settings
3. Expose entities to Google Assistant
4. Link via Google Home app

### Option B: Manual Setup (Free but Complex)
1. Create Google Cloud Platform project
2. Configure OAuth2 credentials
3. Set up Google Actions for Smart Home
4. Configure Home Assistant Google Assistant integration

## Next Steps After Setup

1. **Test All Devices**: Verify each exposed entity works via Google Home
2. **Configure Scenes**: Set up room-based lighting scenes
3. **Create Automations**: Use Home Assistant automations with voice triggers
4. **Document Configuration**: Record working setup for future reference

## Success Criteria

- ✅ Google Home discovers Home Assistant devices
- ✅ Voice commands control devices successfully
- ✅ Response times under 2 seconds
- ✅ No cloud dependency for local control
- ✅ All desired entities accessible via Google Home

This setup provides the most robust and privacy-focused integration between Google Home and Home Assistant using the existing Matter server infrastructure.
