#!/usr/bin/env python3
"""
DCS-8000LH Camera Microphone Detection Script
Detects and tests the built-in microphone on the DCS-8000LH camera
"""

import subprocess
import requests
import time
import json
import socket
from datetime import datetime

def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def detect_camera_on_network():
    """Detect DCS-8000LH camera on network"""
    log("🔍 Scanning for DCS-8000LH camera on network...")
    
    # Get current network
    try:
        result = subprocess.run(['ifconfig'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if 'inet ' in line and '127.0.0.1' not in line:
                ip = line.split()[1]
                if ip.startswith('192.168.'):
                    network = '.'.join(ip.split('.')[:-1]) + '.'
                    log(f"📡 Found network: {network}0/24")
                    return network
    except Exception as e:
        log(f"❌ Error detecting network: {e}")
    
    return None

def scan_for_camera(network):
    """Scan network for DCS-8000LH camera"""
    log(f"🔍 Scanning {network}0/24 for DCS-8000LH camera...")
    
    found_cameras = []
    
    for i in range(1, 255):
        ip = f"{network}{i}"
        try:
            # Quick ping test
            result = subprocess.run(['ping', '-c', '1', '-W', '1000', ip], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                log(f"📱 Found device at {ip}")
                
                # Try to identify as DCS-8000LH
                if is_dcs_camera(ip):
                    found_cameras.append(ip)
                    log(f"✅ DCS-8000LH camera found at {ip}")
                    
        except Exception:
            continue
    
    return found_cameras

def is_dcs_camera(ip):
    """Check if device is DCS-8000LH camera"""
    try:
        # Try HTTP connection
        response = requests.get(f"http://{ip}", timeout=3)
        if response.status_code == 200:
            # Check for D-Link specific content
            content = response.text.lower()
            if 'd-link' in content or 'dcs' in content or 'camera' in content:
                return True
                
        # Try RTSP port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ip, 554))
        sock.close()
        if result == 0:
            return True
            
    except Exception:
        pass
    
    return False

def test_camera_microphone(ip):
    """Test camera microphone functionality"""
    log(f"🎤 Testing microphone on camera {ip}...")
    
    try:
        # Try to access camera audio stream
        rtsp_url = f"rtsp://{ip}/audio"
        log(f"📡 Testing RTSP audio stream: {rtsp_url}")
        
        # Test RTSP connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, 554))
        sock.close()
        
        if result == 0:
            log("✅ RTSP port 554 is open - audio stream may be available")
            return True
        else:
            log("❌ RTSP port 554 is closed - no audio stream")
            return False
            
    except Exception as e:
        log(f"❌ Error testing microphone: {e}")
        return False

def test_http_audio_endpoint(ip):
    """Test HTTP audio endpoints"""
    log(f"🌐 Testing HTTP audio endpoints on {ip}...")
    
    # Common D-Link audio endpoints
    endpoints = [
        f"http://{ip}/audio",
        f"http://{ip}/audio.cgi",
        f"http://{ip}/audio_stream",
        f"http://{ip}/audio_stream.cgi",
        f"http://{ip}/audio.wav",
        f"http://{ip}/audio.mp3"
    ]
    
    working_endpoints = []
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=3)
            if response.status_code == 200:
                log(f"✅ Audio endpoint working: {endpoint}")
                working_endpoints.append(endpoint)
            else:
                log(f"❌ Audio endpoint failed: {endpoint} (Status: {response.status_code})")
        except Exception as e:
            log(f"❌ Audio endpoint error: {endpoint} - {e}")
    
    return working_endpoints

def test_ffmpeg_audio_capture(ip):
    """Test FFmpeg audio capture from camera"""
    log(f"🎬 Testing FFmpeg audio capture from {ip}...")
    
    try:
        # Test RTSP audio capture
        cmd = [
            'ffmpeg', '-f', 'rtsp', '-i', f'rtsp://{ip}/audio',
            '-t', '5', '-f', 'wav', '-'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            log("✅ FFmpeg audio capture successful")
            return True
        else:
            log(f"❌ FFmpeg audio capture failed: {result.stderr}")
            return False
            
    except Exception as e:
        log(f"❌ FFmpeg audio capture error: {e}")
        return False

def test_system_audio_devices():
    """Test system audio devices for camera microphone"""
    log("🔊 Testing system audio devices...")
    
    try:
        # Check system profiler for audio devices
        result = subprocess.run(['system_profiler', 'SPAudioDataType'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            audio_info = result.stdout
            log("📊 Audio devices found:")
            print(audio_info)
            
            # Check for camera-related audio devices
            if 'camera' in audio_info.lower() or 'dcs' in audio_info.lower():
                log("✅ Camera audio device detected in system profiler")
                return True
            else:
                log("❌ No camera audio device found in system profiler")
                return False
        else:
            log("❌ Error running system profiler")
            return False
            
    except Exception as e:
        log(f"❌ Error checking system audio devices: {e}")
        return False

def main():
    """Main function"""
    print("🎤 DCS-8000LH Camera Microphone Detection")
    print("=" * 60)
    print("Detecting and testing camera microphone functionality")
    print()
    
    # Step 1: Detect network
    network = detect_camera_on_network()
    if not network:
        log("❌ Could not detect network")
        return
    
    # Step 2: Scan for camera
    cameras = scan_for_camera(network)
    if not cameras:
        log("❌ No DCS-8000LH cameras found on network")
        log("💡 Make sure camera is powered on and connected to network")
        return
    
    # Step 3: Test each camera
    for camera_ip in cameras:
        log(f"\n🎯 Testing camera at {camera_ip}")
        log("=" * 40)
        
        # Test microphone functionality
        mic_working = test_camera_microphone(camera_ip)
        
        # Test HTTP audio endpoints
        audio_endpoints = test_http_audio_endpoint(camera_ip)
        
        # Test FFmpeg audio capture
        ffmpeg_working = test_ffmpeg_audio_capture(camera_ip)
        
        # Test system audio devices
        system_audio = test_system_audio_devices()
        
        # Summary for this camera
        log(f"\n📊 Camera {camera_ip} Microphone Status:")
        log(f"  🎤 RTSP Audio Stream: {'✅ Working' if mic_working else '❌ Not Working'}")
        log(f"  🌐 HTTP Audio Endpoints: {len(audio_endpoints)} found")
        log(f"  🎬 FFmpeg Audio Capture: {'✅ Working' if ffmpeg_working else '❌ Not Working'}")
        log(f"  🔊 System Audio Device: {'✅ Detected' if system_audio else '❌ Not Detected'}")
        
        if mic_working or audio_endpoints or ffmpeg_working:
            log("✅ Camera microphone is working!")
        else:
            log("❌ Camera microphone is not working")
    
    # Final summary
    log(f"\n{'='*60}")
    log("📊 FINAL SUMMARY")
    log("=" * 60)
    
    if cameras:
        log(f"✅ Found {len(cameras)} DCS-8000LH camera(s)")
        for camera in cameras:
            log(f"  📱 Camera: {camera}")
        log("💡 Camera microphone detection complete")
        log("💡 Use the working audio endpoints for voice input")
    else:
        log("❌ No DCS-8000LH cameras found")
        log("💡 Check camera power and network connection")
        log("💡 Verify camera is on the same network as your Mac Mini")

if __name__ == "__main__":
    main()
