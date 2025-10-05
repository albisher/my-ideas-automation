# DCS-8000LH Camera Hotspot Setup Guide

## Understanding the Process:

### Your Existing Network:
- **SSID**: `SA`
- **Password**: `62Dad64Mom`
- This is your home WiFi network

### Camera's Hotspot Network:
The camera creates its **OWN** WiFi hotspot for initial setup. Look for these network names:

## 🔍 **Camera Hotspot SSIDs to Look For:**

### Most Common:
- `DCS-8000LH`
- `DCS-8000LH-XXXX` (where XXXX is a random number)
- `DCS-8000LH-Setup`

### Alternative Names:
- `D-Link`
- `D-Link-Camera`
- `Camera`
- `DCS8000LH`
- `DCS-8000LH-Config`

## 📱 **Step-by-Step Setup Process:**

### 1. **Reset the Camera**
   - Press and hold the reset button for **15-20 seconds**
   - Wait for the camera to reboot
   - The camera will create its own WiFi hotspot

### 2. **Find the Camera Hotspot**
   - Check your WiFi settings
   - Look for any of the network names listed above
   - The hotspot will be **open** (no password required)

### 3. **Connect to Camera Hotspot**
   - Connect your computer to the camera's hotspot
   - You'll be disconnected from your "SA" network temporarily
   - This is normal - you're now connected to the camera

### 4. **Access Camera Web Interface**
   - Open a web browser
   - Go to: `http://192.168.1.1` or `http://192.168.0.1`
   - You should see the camera's setup page

### 5. **Configure Camera to Connect to Your Network**
   - In the camera's web interface, find WiFi settings
   - **SSID**: Enter `SA` (your existing network)
   - **Password**: Enter `62Dad64Mom` (your existing password)
   - Save the settings

### 6. **Camera Connects to Your Network**
   - The camera will restart and connect to your "SA" network
   - You can now reconnect your computer to your "SA" network
   - The camera will be accessible from your network

## 🎯 **Expected Results:**

After setup, you should be able to:
- ✅ Access camera from your "SA" network
- ✅ View live video stream
- ✅ Take snapshots
- ✅ Configure streaming settings

## 🔧 **Troubleshooting:**

### If No Camera Hotspot Appears:
1. **Try multiple resets** (hold reset for 20+ seconds)
2. **Wait longer** (some cameras take 2-3 minutes)
3. **Check if camera is powered on** (LED indicators)

### If Camera Hotspot Appears but No Web Interface:
1. **Try different IP addresses:**
   - `http://192.168.1.1`
   - `http://192.168.0.1`
   - `http://192.168.1.254`
   - `http://192.168.0.254`

### If Camera Doesn't Connect to Your Network:
1. **Double-check WiFi credentials**
2. **Make sure your "SA" network is working**
3. **Try different WiFi settings in camera**

## 📋 **Summary:**

1. **Reset camera** → Creates its own hotspot
2. **Connect to camera hotspot** → Access camera web interface
3. **Configure camera** → Connect to your "SA" network
4. **Camera joins your network** → Accessible from your devices

The key is that the camera creates its own temporary hotspot for setup, then connects to your existing network.
