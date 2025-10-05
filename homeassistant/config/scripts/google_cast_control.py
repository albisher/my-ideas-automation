#!/usr/bin/env python3
"""
Google Cast Control Script for Xiaomi Device
This script provides direct control of Google Cast devices via HTTP API
"""

import requests
import json
import sys
import time

# Configuration
XIAOMI_IP = "192.168.68.62"
XIAOMI_PORT = 8008
BASE_URL = f"http://{XIAOMI_IP}:{XIAOMI_PORT}"

def send_cast_command(endpoint, data=None):
    """Send a command to the Google Cast device"""
    try:
        url = f"{BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if data:
            response = requests.post(url, json=data, headers=headers, timeout=5)
        else:
            response = requests.get(url, timeout=5)
            
        if response.status_code == 200:
            return {"success": True, "data": response.json() if response.content else {}}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}

def get_device_status():
    """Get the current status of the Google Cast device"""
    return send_cast_command("/v2/receiver/status")

def turn_on():
    """Turn on the Google Cast device"""
    return send_cast_command("/v2/receiver/launch", {"appId": "CC1AD845"})  # Default Media Receiver

def turn_off():
    """Turn off the Google Cast device"""
    return send_cast_command("/v2/receiver/stop")

def set_volume(volume_level):
    """Set volume level (0.0 to 1.0)"""
    return send_cast_command("/v2/receiver/setVolume", {"volume": {"level": volume_level}})

def mute():
    """Mute the device"""
    return send_cast_command("/v2/receiver/setVolume", {"volume": {"muted": True}})

def unmute():
    """Unmute the device"""
    return send_cast_command("/v2/receiver/setVolume", {"volume": {"muted": False}})

def play_media(media_url, media_type="video/mp4"):
    """Play media on the device"""
    return send_cast_command("/v2/receiver/launch", {
        "appId": "CC1AD845",
        "media": {
            "contentId": media_url,
            "contentType": media_type,
            "streamType": "BUFFERED"
        }
    })

def pause():
    """Pause current media"""
    return send_cast_command("/v2/receiver/media/pause")

def play():
    """Play current media"""
    return send_cast_command("/v2/receiver/media/play")

def stop():
    """Stop current media"""
    return send_cast_command("/v2/receiver/media/stop")

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("Usage: python3 google_cast_control.py <command> [args...]")
        print("Commands: status, on, off, volume <0.0-1.0>, mute, unmute, play <url>, pause, stop")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "status":
        result = get_device_status()
        print(json.dumps(result, indent=2))
        
    elif command == "on":
        result = turn_on()
        print(json.dumps(result, indent=2))
        
    elif command == "off":
        result = turn_off()
        print(json.dumps(result, indent=2))
        
    elif command == "volume":
        if len(sys.argv) < 3:
            print("Error: Volume level required (0.0 to 1.0)")
            sys.exit(1)
        try:
            volume = float(sys.argv[2])
            if 0.0 <= volume <= 1.0:
                result = set_volume(volume)
                print(json.dumps(result, indent=2))
            else:
                print("Error: Volume must be between 0.0 and 1.0")
                sys.exit(1)
        except ValueError:
            print("Error: Volume must be a number")
            sys.exit(1)
            
    elif command == "mute":
        result = mute()
        print(json.dumps(result, indent=2))
        
    elif command == "unmute":
        result = unmute()
        print(json.dumps(result, indent=2))
        
    elif command == "play":
        if len(sys.argv) < 3:
            print("Error: Media URL required")
            sys.exit(1)
        media_url = sys.argv[2]
        result = play_media(media_url)
        print(json.dumps(result, indent=2))
        
    elif command == "pause":
        result = pause()
        print(json.dumps(result, indent=2))
        
    elif command == "stop":
        result = stop()
        print(json.dumps(result, indent=2))
        
    else:
        print(f"Error: Unknown command '{command}'")
        sys.exit(1)

if __name__ == "__main__":
    main()
