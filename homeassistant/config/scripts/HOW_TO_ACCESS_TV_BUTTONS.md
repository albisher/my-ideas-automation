# 🎮 How to Access Your TV Control Buttons

## ❌ **Why You Can't See the TV Buttons**

You're currently viewing the **default "Overview" dashboard** in Home Assistant. The TV control buttons are on **custom dashboards** that need to be accessed via specific URLs.

## ✅ **How to Access Your TV Control Buttons**

### **Method 1: Direct URLs (Easiest)**

Copy and paste these URLs directly into your browser:

#### **🎨 Beautiful TV Control Dashboard:**
```
http://localhost:8123/beautiful-tv-control
```

#### **🎮 Ultimate TV Control Dashboard:**
```
http://localhost:8123/ultimate-tv-control
```

#### **📺 Basic TV Control Dashboard:**
```
http://localhost:8123/xiaomi-tv-dashboard
```

#### **🚀 Advanced TV Control Dashboard:**
```
http://localhost:8123/advanced-tv-dashboard
```

### **Method 2: Through Home Assistant Navigation**

1. **Go to Home Assistant**: `http://localhost:8123`
2. **Look for "Dashboards" in the sidebar** (if available)
3. **Or use the search function** to find "Xiaomi" or "TV"
4. **Click on the dashboard name** to access it

### **Method 3: Add to Sidebar (Recommended)**

1. **Go to**: `http://localhost:8123/config/dashboard`
2. **Click "Add Dashboard"**
3. **Choose "Import from YAML"**
4. **Select one of the dashboard files**:
   - `dashboards/beautiful-tv-control.yaml`
   - `dashboards/ultimate-tv-control.yaml`
   - `dashboards/xiaomi-tv-dashboard.yaml`
   - `dashboards/advanced-tv-dashboard.yaml`

## 🎯 **What You'll See on the TV Control Dashboards**

### **🔴 Power Control**
- Large red button for TV power on/off

### **🔊 Volume Control**
- Blue button for volume up
- Red button for volume down
- Gray button for mute

### **📺 Channel Control**
- Purple buttons for channel up/down

### **🎮 Navigation Control**
- Orange buttons for menu and back
- Green button for OK
- Teal buttons for directional control (up/down/left/right)

### **📺 Input & Utility**
- Orange button for input source
- Purple button for testing all commands
- Dark button for setup mode

## 🚀 **Quick Test Steps**

### **Step 1: Access Dashboard**
1. **Copy this URL**: `http://localhost:8123/ultimate-tv-control`
2. **Paste it in your browser**
3. **Press Enter**

### **Step 2: Test TV Control**
1. **Click the large red "🔴 TV Power" button**
2. **Check if your Hisense TV responds**
3. **Try other buttons** like volume and channels

### **Step 3: Verify Connection**
1. **Look for "Xiaomi IR Host: 192.168.68.68"** in the dashboard
2. **Check if device status shows "Connected"**
3. **Use "Test All Commands"** to verify everything works

## 🔧 **Troubleshooting**

### **If Dashboards Don't Load:**
1. **Wait for Home Assistant to fully start** (about 30 seconds)
2. **Check Home Assistant logs** for any errors
3. **Try refreshing the page**
4. **Clear browser cache**

### **If TV Doesn't Respond:**
1. **Ensure Xiaomi device is pointing at TV**
2. **Check TV is within IR range** (3-5 meters)
3. **Verify device IP is correct** (192.168.68.68)
4. **Test commands one by one**

### **If Buttons Don't Work:**
1. **Check Home Assistant logs** for script errors
2. **Verify all configuration files are loaded**
3. **Restart Home Assistant** if needed

## 📱 **Mobile Access**

The TV control dashboards work perfectly on mobile devices:

1. **Open your mobile browser**
2. **Go to**: `http://localhost:8123/ultimate-tv-control`
3. **Use the beautiful buttons** to control your TV
4. **All buttons are touch-optimized**

## 🎉 **Success Indicators**

### **When Everything Works:**
- ✅ Dashboard loads with beautiful buttons
- ✅ All buttons are clickable
- ✅ IR commands are sent to Xiaomi device
- ✅ Hisense TV responds to commands
- ✅ Device status shows "Connected"
- ✅ Command count increases with each button press

---

**🎯 IMPORTANT: The TV control buttons are NOT on the default Overview page!**

**🎮 They are on custom dashboards accessible via the URLs above!**

**🚀 Try this URL now: `http://localhost:8123/ultimate-tv-control`**
