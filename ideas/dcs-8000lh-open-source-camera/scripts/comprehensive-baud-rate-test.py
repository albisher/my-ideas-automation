#!/usr/bin/env python3

"""
Comprehensive Baud Rate Test for DCS-8000LH
Test all common baud rates to find the best communication
"""

import serial
import time
import sys
import os
from datetime import datetime

# Configuration
SERIAL_PORT = "/dev/cu.usbserial-31120"
TIMEOUT = 2

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_baud_rate_comprehensive(baud_rate, duration=15):
    """Comprehensive test of a specific baud rate"""
    log(f"🔄 Testing baud rate: {baud_rate}")
    log(f"⏳ Monitoring for {duration} seconds...")
    
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=baud_rate,
            timeout=TIMEOUT,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        
        start_time = time.time()
        data_received = False
        raw_data = b""
        character_count = 0
        readable_chars = 0
        
        while time.time() - start_time < duration:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                if data:
                    data_received = True
                    raw_data += data
                    character_count += len(data)
                    
                    # Count readable characters
                    try:
                        decoded = data.decode('utf-8', errors='replace')
                        readable_chars += sum(1 for c in decoded if c.isprintable())
                        print(f"📥 {data}", end='', flush=True)
                    except:
                        print(f"📥 {data}", end='', flush=True)
            time.sleep(0.1)
        
        ser.close()
        
        if data_received:
            log(f"\n✅ Data received at {baud_rate} bps")
            log(f"📊 Total bytes: {character_count}")
            log(f"📊 Readable chars: {readable_chars}")
            log(f"📊 Readability: {(readable_chars/character_count*100):.1f}%" if character_count > 0 else "📊 Readability: 0%")
            
            # Try to decode the data
            try:
                decoded = raw_data.decode('utf-8', errors='replace')
                log(f"📥 Decoded: {repr(decoded[:100])}{'...' if len(decoded) > 100 else ''}")
                
                # Check for bootloader indicators
                if any(keyword in decoded.lower() for keyword in ['uboot', 'rlxboot', '=>', 'help', 'version', 'boot', 'alpha168']):
                    log("🎯 BOOTLOADER DETECTED!")
                    return True, decoded, character_count, readable_chars
                else:
                    log("📥 Normal boot messages")
                    return True, decoded, character_count, readable_chars
                    
            except Exception as e:
                log(f"❌ Decode error: {e}")
                return True, raw_data, character_count, readable_chars
        else:
            log(f"📥 No data at {baud_rate} bps")
            return False, None, 0, 0
            
    except Exception as e:
        log(f"❌ Failed at {baud_rate} bps: {e}")
        return False, None, 0, 0

def main():
    """Main function"""
    print("🔧 DCS-8000LH Comprehensive Baud Rate Test")
    print("=" * 70)
    print("Testing all common baud rates to find the best communication")
    print()
    
    # Test baud rates in order of likelihood
    baud_rates = [
        115200,  # Primary recommendation
        57600,   # Alternative from defogger docs
        38400,   # Common embedded rate
        19200,   # Common embedded rate
        9600,    # Very common rate
        230400,  # High speed alternative
        460800,  # High speed alternative
        921600,  # High speed alternative
        4800,    # Low speed alternative
        2400,    # Low speed alternative
        1200,    # Low speed alternative
    ]
    
    results = {}
    
    log("🚀 Starting comprehensive baud rate test...")
    log("💡 Keep the camera powered on during the test")
    log("💡 Try power cycling the camera or pressing reset button")
    log("")
    
    for i, baud_rate in enumerate(baud_rates, 1):
        log(f"\n{'='*70}")
        log(f"Test {i}/{len(baud_rates)}: {baud_rate} bps")
        log("=" * 70)
        
        success, data, char_count, readable_chars = test_baud_rate_comprehensive(baud_rate)
        results[baud_rate] = {
            'success': success,
            'data': data,
            'char_count': char_count,
            'readable_chars': readable_chars,
            'readability': (readable_chars/char_count*100) if char_count > 0 else 0
        }
        
        if success:
            log(f"✅ {baud_rate} bps: Communication successful")
        else:
            log(f"❌ {baud_rate} bps: No communication")
    
    # Summary and analysis
    log(f"\n{'='*70}")
    log("📊 COMPREHENSIVE RESULTS")
    log("=" * 70)
    
    working_rates = []
    bootloader_rates = []
    
    for baud_rate, result in results.items():
        if result['success']:
            working_rates.append((baud_rate, result))
            log(f"✅ {baud_rate} bps: {result['char_count']} chars, {result['readability']:.1f}% readable")
            
            # Check for bootloader
            if result['data'] and any(keyword in str(result['data']).lower() for keyword in ['uboot', 'rlxboot', '=>', 'help', 'version', 'boot', 'alpha168']):
                bootloader_rates.append(baud_rate)
                log(f"🎯 {baud_rate} bps: BOOTLOADER DETECTED!")
        else:
            log(f"❌ {baud_rate} bps: No communication")
    
    # Recommendations
    log(f"\n{'='*70}")
    log("🎯 RECOMMENDATIONS")
    log("=" * 70)
    
    if bootloader_rates:
        log(f"🚀 BOOTLOADER ACCESS: Available at {', '.join(map(str, bootloader_rates))} bps")
        log("💡 Use any of these baud rates for firmware flashing")
        best_rate = bootloader_rates[0]
    elif working_rates:
        # Sort by readability
        working_rates.sort(key=lambda x: x[1]['readability'], reverse=True)
        best_rate = working_rates[0][0]
        log(f"✅ BEST COMMUNICATION: {best_rate} bps ({working_rates[0][1]['readability']:.1f}% readable)")
        log("💡 Use this baud rate for communication")
    else:
        log("❌ NO WORKING BAUD RATE FOUND")
        log("💡 Check wiring and camera power status")
        return
    
    # Final recommendation
    log(f"\n🎯 RECOMMENDED BAUD RATE: {best_rate} bps")
    
    if best_rate in bootloader_rates:
        log("🚀 BOOTLOADER ACCESS: Available")
        log("💡 You can now proceed with firmware flashing")
    else:
        log("⚠️ BOOTLOADER ACCESS: Not detected")
        log("💡 Camera may be in normal operation mode")
        log("💡 Try power cycling or pressing reset button")

if __name__ == "__main__":
    main()







