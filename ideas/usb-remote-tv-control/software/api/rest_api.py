"""
REST API for USB Remote TV Control Agent
"""

import time
import logging
from typing import Dict, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

class TVControlAPI:
    """
    REST API for TV control operations
    """
    
    def __init__(self, tv_controller):
        """
        Initialize TV control API
        
        Args:
            tv_controller: TVController instance
        """
        self.tv_controller = tv_controller
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for web interface
        
        self.logger = logging.getLogger(__name__)
        
        # Setup API routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': time.time(),
                'tv_controller': 'connected' if self.tv_controller else 'disconnected'
            })
        
        @self.app.route('/api/tv/status', methods=['GET'])
        def get_tv_status():
            """Get current TV status"""
            try:
                status = self.tv_controller.get_tv_status()
                return jsonify({
                    'power_state': status.power_state.value,
                    'volume': status.volume,
                    'channel': status.channel,
                    'input_source': status.input_source,
                    'last_command': status.last_command,
                    'last_command_time': status.last_command_time
                })
            except Exception as e:
                self.logger.error(f"Error getting TV status: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/tv/power', methods=['POST'])
        def toggle_power():
            """Toggle TV power on/off"""
            try:
                result = self.tv_controller.send_command('power')
                return jsonify({
                    'success': result.success,
                    'command': result.command,
                    'timestamp': result.timestamp,
                    'error': result.error_message
                })
            except Exception as e:
                self.logger.error(f"Error toggling power: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/tv/volume', methods=['POST'])
        def control_volume():
            """Control TV volume"""
            try:
                data = request.get_json()
                action = data.get('action', 'up')
                
                if action == 'up':
                    result = self.tv_controller.send_command('volume_up')
                elif action == 'down':
                    result = self.tv_controller.send_command('volume_down')
                elif action == 'set':
                    volume = data.get('volume', 50)
                    result = self.tv_controller.send_command('volume_set', {'volume': volume})
                elif action == 'mute':
                    result = self.tv_controller.send_command('mute')
                else:
                    return jsonify({'error': 'Invalid volume action'}), 400
                
                return jsonify({
                    'success': result.success,
                    'command': result.command,
                    'timestamp': result.timestamp,
                    'error': result.error_message
                })
            except Exception as e:
                self.logger.error(f"Error controlling volume: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/tv/channel', methods=['POST'])
        def control_channel():
            """Control TV channel"""
            try:
                data = request.get_json()
                action = data.get('action', 'up')
                
                if action == 'up':
                    result = self.tv_controller.send_command('channel_up')
                elif action == 'down':
                    result = self.tv_controller.send_command('channel_down')
                elif action == 'set':
                    channel = data.get('channel', 1)
                    result = self.tv_controller.send_command('channel_set', {'channel': channel})
                else:
                    return jsonify({'error': 'Invalid channel action'}), 400
                
                return jsonify({
                    'success': result.success,
                    'command': result.command,
                    'timestamp': result.timestamp,
                    'error': result.error_message
                })
            except Exception as e:
                self.logger.error(f"Error controlling channel: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/tv/input', methods=['POST'])
        def change_input():
            """Change TV input source"""
            try:
                data = request.get_json()
                input_source = data.get('input', 'hdmi1')
                
                # Map input names to commands
                input_commands = {
                    'hdmi1': 'input_hdmi1',
                    'hdmi2': 'input_hdmi2',
                    'hdmi3': 'input_hdmi3',
                    'hdmi4': 'input_hdmi4',
                    'usb': 'input_usb',
                    'av': 'input_av'
                }
                
                command = input_commands.get(input_source)
                if not command:
                    return jsonify({'error': 'Invalid input source'}), 400
                
                result = self.tv_controller.send_command(command)
                
                return jsonify({
                    'success': result.success,
                    'command': result.command,
                    'timestamp': result.timestamp,
                    'error': result.error_message
                })
            except Exception as e:
                self.logger.error(f"Error changing input: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/tv/navigation', methods=['POST'])
        def navigation_control():
            """TV navigation controls (menu, back, home, etc.)"""
            try:
                data = request.get_json()
                action = data.get('action', 'menu')
                
                # Map navigation actions to commands
                nav_commands = {
                    'menu': 'menu',
                    'back': 'back',
                    'home': 'home',
                    'up': 'up',
                    'down': 'down',
                    'left': 'left',
                    'right': 'right',
                    'ok': 'ok',
                    'exit': 'exit'
                }
                
                command = nav_commands.get(action)
                if not command:
                    return jsonify({'error': 'Invalid navigation action'}), 400
                
                result = self.tv_controller.send_command(command)
                
                return jsonify({
                    'success': result.success,
                    'command': result.command,
                    'timestamp': result.timestamp,
                    'error': result.error_message
                })
            except Exception as e:
                self.logger.error(f"Error with navigation control: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/tv/command', methods=['POST'])
        def send_custom_command():
            """Send custom TV command"""
            try:
                data = request.get_json()
                command = data.get('command')
                parameters = data.get('parameters')
                
                if not command:
                    return jsonify({'error': 'Command is required'}), 400
                
                result = self.tv_controller.send_command(command, parameters)
                
                return jsonify({
                    'success': result.success,
                    'command': result.command,
                    'timestamp': result.timestamp,
                    'error': result.error_message
                })
            except Exception as e:
                self.logger.error(f"Error sending custom command: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/tv/history', methods=['GET'])
        def get_command_history():
            """Get recent command history"""
            try:
                limit = request.args.get('limit', 10, type=int)
                history = self.tv_controller.get_command_history(limit)
                
                return jsonify({
                    'history': [
                        {
                            'command': cmd,
                            'timestamp': ts,
                            'success': success
                        }
                        for cmd, ts, success in history
                    ]
                })
            except Exception as e:
                self.logger.error(f"Error getting command history: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/tv/learn', methods=['POST'])
        def learn_from_behavior():
            """Learn from user behavior patterns"""
            try:
                data = request.get_json()
                user_commands = data.get('commands', [])
                
                if user_commands:
                    self.tv_controller.learn_from_user_behavior(user_commands)
                
                return jsonify({
                    'success': True,
                    'message': 'Learning data processed'
                })
            except Exception as e:
                self.logger.error(f"Error learning from behavior: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/tv/available-commands', methods=['GET'])
        def get_available_commands():
            """Get list of available TV commands"""
            try:
                # This would get commands from the protocol handler
                commands = [
                    'power', 'volume_up', 'volume_down', 'volume_set',
                    'channel_up', 'channel_down', 'channel_set',
                    'input_hdmi1', 'input_hdmi2', 'input_hdmi3', 'input_hdmi4',
                    'input_usb', 'input_av', 'mute', 'menu', 'back',
                    'home', 'up', 'down', 'left', 'right', 'ok', 'exit'
                ]
                
                return jsonify({
                    'commands': commands
                })
            except Exception as e:
                self.logger.error(f"Error getting available commands: {e}")
                return jsonify({'error': str(e)}), 500
    
    def run(self, host='0.0.0.0', port=8080, debug=False):
        """
        Run the API server
        
        Args:
            host: Host address
            port: Port number
            debug: Enable debug mode
        """
        self.logger.info(f"Starting TV Control API server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

def create_app(tv_controller):
    """
    Create Flask application with TV control API
    
    Args:
        tv_controller: TVController instance
        
    Returns:
        Flask application
    """
    api = TVControlAPI(tv_controller)
    return api.app

