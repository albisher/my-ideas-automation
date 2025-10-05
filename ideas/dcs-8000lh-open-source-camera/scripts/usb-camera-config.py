#!/usr/bin/env python3

"""
USB Camera Configuration Script for DCS-8000LH
Configures camera through USB serial connection
"""

import serial
import time
import sys
import os

# Configuration
SERIAL_PORT = "/dev/cu.usbserial-31120"
BAUD_RATE = 115200
TIMEOUT = 5

# Camera configuration
CAMERA_MAC = "B0:C5:54:51:EB:76"
CAMERA_PIN = "052446"
WIFI_SSID = "SA"
WIFI_PASSWORD = "62Dad64Mom"

def connect_to_camera():
    """Connect to camera via USB serial"""
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            timeout=TIMEOUT,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        print(f"✅ Connected to camera via {SERIAL_PORT}")
        return ser
    except Exception as e:
        print(f"❌ Failed to connect to camera: {e}")
        return None

def send_command(ser, command, wait_time=1):
    """Send command to camera and wait for response"""
    try:
        print(f"📤 Sending: {command}")
        ser.write(f"{command}\r\n".encode())
        time.sleep(wait_time)
        
        # Read response
        response = ""
        while ser.in_waiting > 0:
            response += ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            time.sleep(0.1)
        
        if response.strip():
            print(f"📥 Response: {response.strip()}")
        return response
    except Exception as e:
        print(f"❌ Error sending command: {e}")
        return ""

def configure_camera_services(ser):
    """Configure camera services for streaming"""
    print("\n🔧 Configuring Camera Services...")
    print("=" * 50)
    
    # Commands to enable streaming services
    commands = [
        # Enable HTTP server
        "lighttpd -f /etc/lighttpd/lighttpd.conf &",
        
        # Enable RTSP server
        "rtsp_server &",
        
        # Enable telnet
        "telnetd &",
        
        # Set video configuration
        "v4l2-ctl --set-fmt-video=width=1280,height=720,pixelformat=YUYV",
        
        # Enable streaming
        "echo 'streaming=1' > /tmp/streaming.conf",
        
        # Set network configuration
        f"ifconfig eth0 up",
        f"ifconfig wlan0 up",
        
        # Configure WiFi (if needed)
        f"wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf",
        
        # Start streaming services
        "mjpg_streamer -i 'input_uvc.so -d /dev/video0 -r 1280x720 -f 30' -o 'output_http.so -p 8080' &",
        "mjpg_streamer -i 'input_uvc.so -d /dev/video0 -r 640x480 -f 15' -o 'output_http.so -p 8081' &",
    ]
    
    for cmd in commands:
        send_command(ser, cmd, 2)
        time.sleep(1)
    
    print("✅ Camera services configured")

def configure_network(ser):
    """Configure camera network settings"""
    print("\n🌐 Configuring Network...")
    print("=" * 50)
    
    # Network configuration commands
    network_commands = [
        # Set static IP (if needed)
        "ifconfig eth0 192.168.1.100 netmask 255.255.255.0",
        
        # Configure WiFi
        f"iwconfig wlan0 essid '{WIFI_SSID}'",
        f"wpa_passphrase '{WIFI_SSID}' '{WIFI_PASSWORD}' > /etc/wpa_supplicant/wpa_supplicant.conf",
        
        # Start network services
        "udhcpc -i eth0 &",
        "udhcpc -i wlan0 &",
    ]
    
    for cmd in network_commands:
        send_command(ser, cmd, 2)
        time.sleep(1)
    
    print("✅ Network configured")

def enable_streaming(ser):
    """Enable camera streaming"""
    print("\n🎥 Enabling Streaming...")
    print("=" * 50)
    
    # Streaming configuration
    streaming_commands = [
        # Enable video streaming
        "echo '#!/bin/sh' > /usr/bin/start_streaming.sh",
        "echo 'mjpg_streamer -i \"input_uvc.so -d /dev/video0 -r 1280x720 -f 30\" -o \"output_http.so -p 8080\" &' >> /usr/bin/start_streaming.sh",
        "echo 'mjpg_streamer -i \"input_uvc.so -d /dev/video0 -r 640x480 -f 15\" -o \"output_http.so -p 8081\" &' >> /usr/bin/start_streaming.sh",
        "chmod +x /usr/bin/start_streaming.sh",
        "/usr/bin/start_streaming.sh",
        
        # Enable RTSP
        "echo '#!/bin/sh' > /usr/bin/start_rtsp.sh",
        "echo 'rtsp_server -p 554 -u admin:052446 &' >> /usr/bin/start_rtsp.sh",
        "chmod +x /usr/bin/start_rtsp.sh",
        "/usr/bin/start_rtsp.sh",
    ]
    
    for cmd in streaming_commands:
        send_command(ser, cmd, 2)
        time.sleep(1)
    
    print("✅ Streaming enabled")

def test_camera_connection(ser):
    """Test camera connection and get info"""
    print("\n🔍 Testing Camera Connection...")
    print("=" * 50)
    
    # Test commands
    test_commands = [
        "uname -a",
        "ifconfig",
        "ps aux",
        "netstat -tlnp",
        "ls -la /dev/video*",
        "ls -la /dev/v4l*",
    ]
    
    for cmd in test_commands:
        send_command(ser, cmd, 2)
        time.sleep(1)
    
    print("✅ Camera connection tested")

def main():
    """Main function"""
    print("🔌 DCS-8000LH USB Camera Configuration")
    print("=" * 60)
    print(f"Camera MAC: {CAMERA_MAC}")
    print(f"Camera PIN: {CAMERA_PIN}")
    print(f"WiFi SSID: {WIFI_SSID}")
    print(f"Serial Port: {SERIAL_PORT}")
    print("")
    
    # Connect to camera
    ser = connect_to_camera()
    if not ser:
        print("❌ Cannot connect to camera via USB")
        return
    
    try:
        # Test connection
        test_camera_connection(ser)
        
        # Configure services
        configure_camera_services(ser)
        
        # Configure network
        configure_network(ser)
        
        # Enable streaming
        enable_streaming(ser)
        
        print("\n✅ Camera configuration completed!")
        print("=" * 60)
        print("🎥 Streaming URLs:")
        print("  HTTP: http://CAMERA_IP:8080/?action=stream")
        print("  RTSP: rtsp://CAMERA_IP:554/live")
        print("  Snapshot: http://CAMERA_IP:8080/?action=snapshot")
        print("")
        print("🔑 Credentials: admin / 052446")
        
    except KeyboardInterrupt:
        print("\n⚠️ Configuration interrupted by user")
    except Exception as e:
        print(f"❌ Error during configuration: {e}")
    finally:
        if ser:
            ser.close()
            print("🔌 USB connection closed")

if __name__ == "__main__":
    main()
