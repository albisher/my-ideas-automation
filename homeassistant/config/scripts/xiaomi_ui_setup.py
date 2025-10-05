#!/usr/bin/env python3
"""
Xiaomi Device UI Setup Script for Home Assistant
This script helps you configure the Xiaomi device through the Home Assistant UI
"""

import requests
import json
import time
import webbrowser
from urllib.parse import urlencode

def open_home_assistant_ui():
    """Open Home Assistant UI for Xiaomi device configuration"""
    print("Opening Home Assistant UI for Xiaomi device configuration...")
    
    # Home Assistant URL
    ha_url = "http://localhost:8123"
    
    # Direct link to add Xiaomi Miio integration
    integration_url = f"{ha_url}/config/integrations"
    
    print(f"Please follow these steps:")
    print(f"1. Open Home Assistant: {ha_url}")
    print(f"2. Go to Settings -> Devices & Services")
    print(f"3. Click 'Add Integration'")
    print(f"4. Search for 'Xiaomi Miio'")
    print(f"5. Enter the following details:")
    print(f"   - Host: 192.168.68.62")
    print(f"   - Token: [Your 32-character token]")
    print(f"6. Click 'Submit'")
    
    # Try to open the browser
    try:
        webbrowser.open(ha_url)
        print(f"Home Assistant opened in your browser: {ha_url}")
    except:
        print(f"Please manually open: {ha_url}")

def check_xiaomi_device_status():
    """Check if Xiaomi device is accessible"""
    print("Checking Xiaomi device status...")
    
    try:
        # Check if device is pingable
        import subprocess
        result = subprocess.run(['ping', '-c', '1', '192.168.68.62'], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ Xiaomi device is accessible at 192.168.68.62")
            return True
        else:
            print("❌ Xiaomi device is not accessible at 192.168.68.62")
            return False
    except Exception as e:
        print(f"❌ Error checking device: {e}")
        return False

def get_xiaomi_token_instructions():
    """Provide instructions for getting the Xiaomi token"""
    print("\n" + "="*60)
    print("HOW TO GET YOUR XIAOMI DEVICE TOKEN")
    print("="*60)
    print()
    print("Method 1: Using Xiaomi Home App")
    print("1. Open Xiaomi Home app on your phone")
    print("2. Find your device in the app")
    print("3. Tap on the device")
    print("4. Go to Settings (gear icon)")
    print("5. Look for 'Device Token' or 'Local Token'")
    print("6. Copy the 32-character token")
    print()
    print("Method 2: Using Mi Home App")
    print("1. Open Mi Home app")
    print("2. Go to Profile -> Settings -> Developer Options")
    print("3. Enable 'Developer Mode'")
    print("4. Go back to your device")
    print("5. Tap and hold on the device name")
    print("6. Look for 'Token' in the popup")
    print()
    print("Method 3: Using ADB (Advanced)")
    print("1. Enable ADB on your device")
    print("2. Connect via USB")
    print("3. Run: adb shell dumpsys activity | grep token")
    print()
    print("Method 4: Using Network Sniffing (Advanced)")
    print("1. Use Wireshark to capture network traffic")
    print("2. Look for MiIO protocol packets")
    print("3. Extract token from the packets")
    print()
    print("="*60)

def create_test_script():
    """Create a test script to verify the setup"""
    test_script = """#!/usr/bin/env python3
import requests
import json

def test_home_assistant_integration():
    # Test if Home Assistant is accessible
    try:
        response = requests.get('http://localhost:8123/api/')
        if response.status_code == 200:
            print("✅ Home Assistant is accessible")
        else:
            print("❌ Home Assistant is not accessible")
            return False
    except Exception as e:
        print(f"❌ Error accessing Home Assistant: {e}")
        return False
    
    # Test if Xiaomi device is configured
    try:
        response = requests.get('http://localhost:8123/api/states')
        if response.status_code == 200:
            states = response.json()
            xiaomi_entities = [state for state in states if 'xiaomi' in state['entity_id'].lower()]
            if xiaomi_entities:
                print("✅ Xiaomi entities found:")
                for entity in xiaomi_entities:
                    print(f"   - {entity['entity_id']}: {entity['state']}")
            else:
                print("❌ No Xiaomi entities found")
                print("   Please configure the Xiaomi Miio integration first")
                return False
        else:
            print("❌ Error getting Home Assistant states")
            return False
    except Exception as e:
        print(f"❌ Error testing integration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing Home Assistant Xiaomi integration...")
    success = test_home_assistant_integration()
    if success:
        print("✅ Integration test passed!")
    else:
        print("❌ Integration test failed!")
"""
    
    with open('/Users/amac/myIdeas/homeassistant/config/scripts/test_integration.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Test script created: /Users/amac/myIdeas/homeassistant/config/scripts/test_integration.py")

def main():
    print("Xiaomi Device UI Setup for Home Assistant")
    print("="*50)
    
    # Check device status
    if not check_xiaomi_device_status():
        print("Please ensure your Xiaomi device is connected to the network")
        return
    
    # Get token instructions
    get_xiaomi_token_instructions()
    
    # Open Home Assistant UI
    open_home_assistant_ui()
    
    # Create test script
    create_test_script()
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Get your Xiaomi device token (see instructions above)")
    print("2. Open Home Assistant UI (should open automatically)")
    print("3. Go to Settings -> Devices & Services")
    print("4. Add Xiaomi Miio integration")
    print("5. Enter host: 192.168.68.62")
    print("6. Enter your 32-character token")
    print("7. Test the integration")
    print("8. Run the test script: python3 test_integration.py")
    print("="*60)

if __name__ == "__main__":
    main()
