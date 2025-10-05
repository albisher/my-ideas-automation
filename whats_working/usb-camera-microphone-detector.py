#!/usr/bin/env python3
"""
USB Camera Microphone Detection Script
Detects and tests USB-connected DCS-8000LH camera microphone
"""

import subprocess
import json
import time
import os
from datetime import datetime

def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def detect_usb_camera():
    """Detect USB-connected camera"""
    log("🔍 Scanning for USB-connected DCS-8000LH camera...")
    
    try:
        # Get USB device information
        result = subprocess.run(['system_profiler', 'SPUSBDataType'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            usb_info = result.stdout
            log("📊 USB devices found:")
            
            # Look for camera-related devices
            camera_keywords = ['d-link', 'dcs', 'camera', 'video', 'webcam', 'usb video']
            found_cameras = []
            
            lines = usb_info.split('\n')
            for i, line in enumerate(lines):
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in camera_keywords):
                    log(f"📱 Potential camera device found:")
                    # Show context around the match
                    start = max(0, i-3)
                    end = min(len(lines), i+4)
                    for j in range(start, end):
                        marker = ">>> " if j == i else "    "
                        log(f"{marker}{lines[j]}")
                    found_cameras.append(line.strip())
            
            if found_cameras:
                log(f"✅ Found {len(found_cameras)} potential camera device(s)")
                return found_cameras
            else:
                log("❌ No camera devices found in USB scan")
                return []
        else:
            log("❌ Error running system profiler")
            return []
            
    except Exception as e:
        log(f"❌ Error detecting USB camera: {e}")
        return []

def detect_serial_devices():
    """Detect serial devices that might be the camera"""
    log("🔍 Scanning for serial devices...")
    
    try:
        # Check for serial devices
        serial_devices = []
        
        # Check /dev/cu.* devices
        result = subprocess.run(['ls', '/dev/cu.*'], capture_output=True, text=True)
        if result.returncode == 0:
            devices = result.stdout.strip().split('\n')
            for device in devices:
                if device and 'Bluetooth' not in device and 'debug' not in device:
                    serial_devices.append(device)
                    log(f"📱 Serial device found: {device}")
        
        # Check /dev/tty.* devices
        result = subprocess.run(['ls', '/dev/tty.*'], capture_output=True, text=True)
        if result.returncode == 0:
            devices = result.stdout.strip().split('\n')
            for device in devices:
                if device and 'Bluetooth' not in device and 'debug' not in device:
                    serial_devices.append(device)
                    log(f"📱 TTY device found: {device}")
        
        if serial_devices:
            log(f"✅ Found {len(serial_devices)} serial device(s)")
            return serial_devices
        else:
            log("❌ No serial devices found")
            return []
            
    except Exception as e:
        log(f"❌ Error detecting serial devices: {e}")
        return []

def test_ffmpeg_devices():
    """Test FFmpeg for video and audio devices"""
    log("🎬 Testing FFmpeg for video and audio devices...")
    
    try:
        # Test video devices
        result = subprocess.run(['ffmpeg', '-f', 'avfoundation', '-list_devices', 'true', '-i', '""'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 or result.stderr:
            output = result.stderr if result.stderr else result.stdout
            
            # Look for video devices
            video_devices = []
            audio_devices = []
            
            lines = output.split('\n')
            in_video_section = False
            in_audio_section = False
            
            for line in lines:
                if 'AVFoundation video devices:' in line:
                    in_video_section = True
                    in_audio_section = False
                    continue
                elif 'AVFoundation audio devices:' in line:
                    in_video_section = False
                    in_audio_section = True
                    continue
                elif '[' in line and ']' in line and (in_video_section or in_audio_section):
                    # Extract device info
                    if in_video_section:
                        video_devices.append(line.strip())
                        log(f"📹 Video device: {line.strip()}")
                    elif in_audio_section:
                        audio_devices.append(line.strip())
                        log(f"🎤 Audio device: {line.strip()}")
            
            log(f"✅ Found {len(video_devices)} video device(s)")
            log(f"✅ Found {len(audio_devices)} audio device(s)")
            
            return video_devices, audio_devices
        else:
            log("❌ Error running FFmpeg device detection")
            return [], []
            
    except Exception as e:
        log(f"❌ Error testing FFmpeg devices: {e}")
        return [], []

def test_camera_microphone():
    """Test camera microphone functionality"""
    log("🎤 Testing camera microphone...")
    
    try:
        # Try to record audio from camera
        test_file = "/tmp/camera_mic_test.wav"
        
        # Test with different audio device indices
        for device_idx in range(5):  # Test first 5 audio devices
            log(f"🎤 Testing audio device {device_idx}...")
            
            cmd = [
                'ffmpeg', '-f', 'avfoundation', 
                '-i', f':{device_idx}', 
                '-t', '3', '-f', 'wav', test_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(test_file):
                file_size = os.path.getsize(test_file)
                if file_size > 1000:  # Check if file has reasonable size
                    log(f"✅ Audio device {device_idx} working - recorded {file_size} bytes")
                    
                    # Clean up test file
                    os.remove(test_file)
                    return device_idx
                else:
                    log(f"❌ Audio device {device_idx} - file too small ({file_size} bytes)")
                    if os.path.exists(test_file):
                        os.remove(test_file)
            else:
                log(f"❌ Audio device {device_idx} failed: {result.stderr}")
        
        log("❌ No working audio devices found")
        return None
        
    except Exception as e:
        log(f"❌ Error testing camera microphone: {e}")
        return None

def test_camera_video():
    """Test camera video functionality"""
    log("📹 Testing camera video...")
    
    try:
        # Try to capture video from camera
        test_file = "/tmp/camera_video_test.mp4"
        
        # Test with different video device indices
        for device_idx in range(5):  # Test first 5 video devices
            log(f"📹 Testing video device {device_idx}...")
            
            cmd = [
                'ffmpeg', '-f', 'avfoundation', 
                '-i', f'{device_idx}:', 
                '-t', '3', '-f', 'mp4', test_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(test_file):
                file_size = os.path.getsize(test_file)
                if file_size > 10000:  # Check if file has reasonable size
                    log(f"✅ Video device {device_idx} working - recorded {file_size} bytes")
                    
                    # Clean up test file
                    os.remove(test_file)
                    return device_idx
                else:
                    log(f"❌ Video device {device_idx} - file too small ({file_size} bytes)")
                    if os.path.exists(test_file):
                        os.remove(test_file)
            else:
                log(f"❌ Video device {device_idx} failed: {result.stderr}")
        
        log("❌ No working video devices found")
        return None
        
    except Exception as e:
        log(f"❌ Error testing camera video: {e}")
        return None

def main():
    """Main function"""
    print("🎤 USB Camera Microphone Detection")
    print("=" * 60)
    print("Detecting USB-connected DCS-8000LH camera and testing microphone")
    print()
    
    # Step 1: Detect USB camera
    usb_cameras = detect_usb_camera()
    
    # Step 2: Detect serial devices
    serial_devices = detect_serial_devices()
    
    # Step 3: Test FFmpeg devices
    video_devices, audio_devices = test_ffmpeg_devices()
    
    # Step 4: Test camera microphone
    working_audio_device = test_camera_microphone()
    
    # Step 5: Test camera video
    working_video_device = test_camera_video()
    
    # Final summary
    log(f"\n{'='*60}")
    log("📊 FINAL SUMMARY")
    log("=" * 60)
    
    if usb_cameras:
        log(f"✅ Found {len(usb_cameras)} USB camera device(s)")
        for camera in usb_cameras:
            log(f"  📱 {camera}")
    else:
        log("❌ No USB camera devices found")
    
    if serial_devices:
        log(f"✅ Found {len(serial_devices)} serial device(s)")
        for device in serial_devices:
            log(f"  📱 {device}")
    else:
        log("❌ No serial devices found")
    
    if video_devices:
        log(f"✅ Found {len(video_devices)} video device(s)")
    else:
        log("❌ No video devices found")
    
    if audio_devices:
        log(f"✅ Found {len(audio_devices)} audio device(s)")
    else:
        log("❌ No audio devices found")
    
    if working_audio_device is not None:
        log(f"✅ Camera microphone working on device {working_audio_device}")
        log("💡 You can use this device for voice input in Home Assistant")
    else:
        log("❌ Camera microphone not working")
        log("💡 Check if camera is powered on and properly connected")
    
    if working_video_device is not None:
        log(f"✅ Camera video working on device {working_video_device}")
    else:
        log("❌ Camera video not working")
    
    # Recommendations
    log(f"\n{'='*60}")
    log("💡 RECOMMENDATIONS")
    log("=" * 60)
    
    if working_audio_device is not None:
        log("✅ Camera microphone is working!")
        log("💡 You can use this for voice input in your Echo Dot optimization setup")
        log("💡 Configure Home Assistant to use this audio device for voice processing")
    else:
        log("❌ Camera microphone not detected")
        log("💡 Check if camera is powered on")
        log("💡 Check USB connection")
        log("💡 Try different USB port")
        log("💡 Check if camera needs drivers")

if __name__ == "__main__":
    main()
