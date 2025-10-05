#!/usr/bin/env python3
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
