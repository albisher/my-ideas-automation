#!/usr/bin/env python3
"""
Flask API for IR Controller
Provides REST API endpoints for controlling IR devices
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from ir_controller import IRController, IRCommand, IRProtocol

app = Flask(__name__)
CORS(app)

# Initialize IR controller
ir_controller = IRController()

@app.route('/api/commands', methods=['GET'])
def get_commands():
    """Get list of available commands"""
    commands = ir_controller.list_commands()
    return jsonify({"commands": commands})

@app.route('/api/commands/<command_name>', methods=['POST'])
def send_command(command_name):
    """Send IR command"""
    try:
        success = ir_controller.send_command(command_name)
        if success:
            return jsonify({"status": "success", "message": f"Command '{command_name}' sent"})
        else:
            return jsonify({"status": "error", "message": f"Failed to send command '{command_name}'"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/learn', methods=['POST'])
def learn_command():
    """Learn new IR command"""
    data = request.get_json()
    command_name = data.get('command_name')
    device_name = data.get('device_name')
    
    if not command_name or not device_name:
        return jsonify({"status": "error", "message": "command_name and device_name required"}), 400
    
    try:
        success = ir_controller.learn_command(command_name, device_name)
        if success:
            return jsonify({"status": "success", "message": f"Command '{command_name}' learned"})
        else:
            return jsonify({"status": "error", "message": f"Failed to learn command '{command_name}'"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/devices/<device_name>/commands', methods=['GET'])
def get_device_commands(device_name):
    """Get commands for specific device"""
    commands = ir_controller.get_device_commands(device_name)
    return jsonify({"device": device_name, "commands": commands})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get controller status"""
    status = {
        "broadlink_available": ir_controller.broadlink_device is not None,
        "lirc_available": ir_controller.lirc_client is not None,
        "total_commands": len(ir_controller.commands)
    }
    return jsonify(status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
