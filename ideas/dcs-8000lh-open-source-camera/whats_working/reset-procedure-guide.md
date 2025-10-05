# DCS-8000LH Reset Procedure Guide

## Reset Button Not Showing Indicators - This is Normal

### Why No Visual Indicators?

Many cameras, including the DCS-8000LH, don't have visual indicators for the reset button. This is normal and doesn't mean the reset isn't working.

### Proper Reset Procedure

#### Method 1: Standard Reset (Recommended)
1. **Unplug camera power** - Remove power adapter
2. **Wait 10 seconds** - Let capacitors discharge
3. **Press and hold reset button** - Even if no indicator, hold it down
4. **Plug power back in** - While still holding reset button
5. **Hold reset for 5-10 seconds** - Continue holding after power is restored
6. **Release reset button** - Let camera boot normally

#### Method 2: Extended Reset
1. **Unplug camera power**
2. **Wait 30 seconds** - Longer discharge time
3. **Press and hold reset button**
4. **Plug power back in** - While holding reset
5. **Hold reset for 15-20 seconds** - Extended hold time
6. **Release reset button**

#### Method 3: Multiple Reset Attempts
1. **Unplug camera power**
2. **Wait 10 seconds**
3. **Press and hold reset button**
4. **Plug power back in** - While holding reset
5. **Hold reset for 5 seconds**
6. **Release reset button**
7. **Wait 2 seconds**
8. **Press and hold reset button again**
9. **Hold for 5 seconds**
10. **Release reset button**

### What to Expect

#### Normal Behavior (No Indicators)
- Reset button may feel "clicky" but no LED indicators
- Camera may not show any visual feedback
- This is completely normal for this camera model

#### Success Indicators
- Camera may take longer to boot after reset
- Network settings may be reset to defaults
- Camera may create a new WiFi hotspot
- Serial communication may show boot messages

### Troubleshooting Reset Issues

#### If Reset Doesn't Seem to Work
1. **Try different timing**:
   - Hold reset button longer (15-20 seconds)
   - Try holding reset before plugging in power
   - Try releasing reset at different times

2. **Check reset button**:
   - Make sure you're pressing the actual reset button
   - Reset button is usually small and recessed
   - May require a paperclip or small tool to press

3. **Power cycle timing**:
   - Wait longer between unplugging and plugging back in
   - Try multiple power cycles
   - Ensure power adapter is fully connected

#### Alternative Reset Methods
1. **Factory reset via web interface** (if accessible)
2. **Bluetooth reset** (if camera is in pairing mode)
3. **Recovery mode** (if available)

### Monitoring Reset Success

#### Serial Communication Monitoring
The best way to know if reset worked is to monitor serial communication:

```bash
cd /Users/amac/myIdeas/ideas/dcs-8000lh-open-source-camera/scripts
source firmware-env/bin/activate
python3 monitor-boot-process.py
```

#### What to Look For
- Boot messages during startup
- U-Boot prompt (`=>` or `rlxboot#`)
- Bootloader access
- Network configuration changes

### Reset Button Location

The reset button is typically located:
- On the bottom of the camera
- Small, recessed button
- May require a paperclip or small tool
- Usually labeled "RESET" or "RST"

### Common Issues

#### Reset Button Hard to Press
- Use a paperclip or small tool
- Apply firm pressure
- Make sure you're pressing the actual reset button
- Not the power button or other buttons

#### No Response to Reset
- Try different timing
- Hold reset button longer
- Try multiple reset attempts
- Check if camera is actually powering on

#### Camera Not Booting After Reset
- Wait longer for boot process
- Check power connection
- Try power cycling without reset
- Check for boot messages via serial

### Success Criteria

Reset is successful if:
1. Camera boots normally
2. Serial communication shows boot messages
3. Camera creates new WiFi hotspot
4. Network settings are reset to defaults
5. Bootloader is accessible via serial

### Next Steps After Reset

Once reset is successful:
1. **Monitor boot process** with serial communication
2. **Look for bootloader access** (U-Boot prompt)
3. **Flash official firmware** if bootloader is accessible
4. **Configure camera** with new settings

### Important Notes

- **No visual indicators are normal** for this camera
- **Reset button may be hard to press** - use a tool if needed
- **Timing is important** - follow the procedure exactly
- **Serial monitoring is the best way** to verify reset success
- **Multiple attempts may be needed** - don't give up after one try

The lack of visual indicators is not a problem - it's just how this camera model works. The important thing is to follow the procedure correctly and monitor the serial communication to see if the reset worked.







