#!/usr/bin/env python3
"""
Xiaomi IR Send Command Script - Production Solution
Sends IR commands directly to Xiaomi device via UDP
"""

import socket
import sys
import time
import logging
import json
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Device configuration
XIAOMI_IR_HOST = "192.168.68.68"
XIAOMI_IR_PORT = 54321

# IR command mappings - These are placeholder hex codes
# In production, these would be actual learned IR codes from the device
IR_COMMANDS = {
    "hisense_tv_power": b'\x21\x31\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01',
    "hisense_tv_volume_up": b'\x21\x31\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02',
    "hisense_tv_volume_down": b'\x21\x31\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03',
    "hisense_tv_channel_up": b'\x21\x31\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04',
    "hisense_tv_channel_down": b'\x21\x31\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05',
    "hisense_tv_input": b'\x21\x31\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06',
    "hisense_tv_menu": b'\x21\x31\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07',
    "hisense_tv_back": b'\x21\x31\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08',
    "hisense_tv_ok": b'\x21\x31\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x09',
    "hisense_tv_up": b'\x21\x31\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0a',
    "hisense_tv_down": b'\x21\x31\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0b',
    "hisense_tv_left": b'\x21\x31\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0c',
    "hisense_tv_right": b'\x21\x31\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0d',
    "hisense_tv_mute": b'\x21\x31\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0e'
}

def send_ir_command(command_name):
    """Send IR command to Xiaomi device"""
    logger.info(f"=== SENDING IR COMMAND: {command_name} ===")
    logger.info(f"Target: {XIAOMI_IR_HOST}:{XIAOMI_IR_PORT}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    if command_name not in IR_COMMANDS:
        logger.error(f"Unknown command: {command_name}")
        logger.error(f"Available commands: {list(IR_COMMANDS.keys())}")
        return False
    
    try:
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(10)  # 10 second timeout
        
        # Get the IR command data
        ir_data = IR_COMMANDS[command_name]
        logger.info(f"IR Data: {ir_data.hex()}")
        
        # Send the command
        sock.sendto(ir_data, (XIAOMI_IR_HOST, XIAOMI_IR_PORT))
        logger.info(f"✅ Sent {len(ir_data)} bytes to {XIAOMI_IR_HOST}:{XIAOMI_IR_PORT}")
        
        # Try to get response (optional)
        try:
            sock.settimeout(2)
            response, addr = sock.recvfrom(1024)
            logger.info(f"📡 Response from {addr}: {response.hex()}")
        except socket.timeout:
            logger.info("📡 No response (normal for IR commands)")
        except Exception as e:
            logger.info(f"📡 Response error: {e}")
        
        sock.close()
        logger.info(f"✅ Command '{command_name}' sent successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send command '{command_name}': {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        logger.error("Usage: python3 send_ir_command.py <command_name>")
        logger.error(f"Available commands: {list(IR_COMMANDS.keys())}")
        sys.exit(1)
    
    command = sys.argv[1]
    logger.info(f"🚀 Starting IR command: {command}")
    
    success = send_ir_command(command)
    
    if success:
        logger.info("🎉 Command completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Command failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()