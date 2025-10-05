"""
Comprehensive test suite for USB Remote TV Control system
"""

import time
import logging
import unittest
from unittest.mock import Mock, patch
import json

# Import system components
from software.agent.tv_controller import TVController, CommandResult, TVStatus, TVState
from software.usb_driver.usb_hid_interface import USBHIDInterface
from software.protocol_handler.ir_protocols import IRProtocolHandler
from software.api.rest_api import TVControlAPI

class TestTVController(unittest.TestCase):
    """Test cases for TV Controller agent"""
    
    def setUp(self):
        """Setup test environment"""
        self.tv_config = {
            'brand': 'Samsung',
            'model': 'UN55MU8000',
            'protocol': 'nec',
            'carrier_frequency': 38000,
            'codes': {
                'power': '0xE0E040BF',
                'volume_up': '0xE0E0E01F',
                'volume_down': '0xE0E0D02F',
                'channel_up': '0xE0E048B7',
                'channel_down': '0xE0E008F7'
            }
        }
        
        # Mock USB interface
        self.mock_usb_interface = Mock()
        self.mock_protocol_handler = Mock()
        
        # Create TV controller with mocked dependencies
        with patch('software.agent.tv_controller.USBHIDInterface') as mock_usb:
            with patch('software.agent.tv_controller.IRProtocolHandler') as mock_protocol:
                mock_usb.return_value = self.mock_usb_interface
                mock_protocol.return_value = self.mock_protocol_handler
                
                self.tv_controller = TVController(
                    usb_device_id='FSP2C01915A',
                    tv_config=self.tv_config,
                    learning_enabled=False,
                    debug=True
                )
    
    def test_initialization(self):
        """Test TV controller initialization"""
        self.assertIsNotNone(self.tv_controller)
        self.assertEqual(self.tv_controller.usb_device_id, 'FSP2C01915A')
        self.assertEqual(self.tv_controller.tv_config, self.tv_config)
    
    def test_send_power_command(self):
        """Test sending power command"""
        # Mock successful USB communication
        self.mock_usb_interface.send_ir_signal.return_value = True
        self.mock_protocol_handler.encode_command.return_value = b'\x01\x02\x03'
        
        result = self.tv_controller.send_command('power')
        
        self.assertTrue(result.success)
        self.assertEqual(result.command, 'power')
        self.mock_usb_interface.send_ir_signal.assert_called_once()
        self.mock_protocol_handler.encode_command.assert_called_once()
    
    def test_send_volume_command(self):
        """Test sending volume command"""
        # Mock successful USB communication
        self.mock_usb_interface.send_ir_signal.return_value = True
        self.mock_protocol_handler.encode_command.return_value = b'\x01\x02\x03'
        
        result = self.tv_controller.send_command('volume_up')
        
        self.assertTrue(result.success)
        self.assertEqual(result.command, 'volume_up')
    
    def test_send_volume_set_command(self):
        """Test sending volume set command with parameters"""
        # Mock successful USB communication
        self.mock_usb_interface.send_ir_signal.return_value = True
        self.mock_protocol_handler.encode_command.return_value = b'\x01\x02\x03'
        
        result = self.tv_controller.send_command('volume_set', {'volume': 75})
        
        self.assertTrue(result.success)
        self.assertEqual(result.command, 'volume_set')
        self.mock_protocol_handler.encode_command.assert_called_with('volume_set', {'volume': 75})
    
    def test_invalid_command(self):
        """Test handling of invalid command"""
        result = self.tv_controller.send_command('invalid_command')
        
        self.assertFalse(result.success)
        self.assertIn('Invalid command', result.error_message)
    
    def test_usb_communication_failure(self):
        """Test handling of USB communication failure"""
        # Mock USB communication failure
        self.mock_usb_interface.send_ir_signal.return_value = False
        self.mock_protocol_handler.encode_command.return_value = b'\x01\x02\x03'
        
        result = self.tv_controller.send_command('power')
        
        self.assertFalse(result.success)
        self.assertIn('Failed to send IR signal', result.error_message)
    
    def test_tv_state_update(self):
        """Test TV state update after command"""
        # Mock successful command
        self.mock_usb_interface.send_ir_signal.return_value = True
        self.mock_protocol_handler.encode_command.return_value = b'\x01\x02\x03'
        
        # Test power command
        result = self.tv_controller.send_command('power')
        self.assertTrue(result.success)
        
        # Check state update
        status = self.tv_controller.get_tv_status()
        self.assertEqual(status.last_command, 'power')
        self.assertIsNotNone(status.last_command_time)
    
    def test_command_history(self):
        """Test command history tracking"""
        # Mock successful commands
        self.mock_usb_interface.send_ir_signal.return_value = True
        self.mock_protocol_handler.encode_command.return_value = b'\x01\x02\x03'
        
        # Send multiple commands
        self.tv_controller.send_command('power')
        self.tv_controller.send_command('volume_up')
        self.tv_controller.send_command('channel_up')
        
        # Check history
        history = self.tv_controller.get_command_history(3)
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0][0], 'power')
        self.assertEqual(history[1][0], 'volume_up')
        self.assertEqual(history[2][0], 'channel_up')

class TestIRProtocolHandler(unittest.TestCase):
    """Test cases for IR Protocol Handler"""
    
    def setUp(self):
        """Setup test environment"""
        self.tv_config = {
            'protocol': 'nec',
            'carrier_frequency': 38000,
            'codes': {
                'power': '0xE0E040BF',
                'volume_up': '0xE0E0E01F',
                'volume_down': '0xE0E0D02F'
            }
        }
        
        self.protocol_handler = IRProtocolHandler(self.tv_config)
    
    def test_initialization(self):
        """Test protocol handler initialization"""
        self.assertEqual(self.protocol_handler.protocol, 'nec')
        self.assertEqual(self.protocol_handler.carrier_freq, 38000)
        self.assertIn('power', self.protocol_handler.codes)
    
    def test_encode_nec_command(self):
        """Test NEC protocol encoding"""
        ir_data = self.protocol_handler.encode_command('power')
        
        self.assertIsNotNone(ir_data)
        self.assertIsInstance(ir_data, bytes)
        self.assertGreater(len(ir_data), 0)
    
    def test_encode_volume_command(self):
        """Test encoding volume command"""
        ir_data = self.protocol_handler.encode_command('volume_up')
        
        self.assertIsNotNone(ir_data)
        self.assertIsInstance(ir_data, bytes)
    
    def test_invalid_command(self):
        """Test handling of invalid command"""
        ir_data = self.protocol_handler.encode_command('invalid_command')
        
        self.assertIsNone(ir_data)
    
    def test_volume_set_command(self):
        """Test volume set command with parameters"""
        ir_data = self.protocol_handler.encode_command('volume_set', {'volume': 50})
        
        # Should return a valid IR signal (either specific code or volume up/down)
        self.assertIsNotNone(ir_data)
    
    def test_get_available_commands(self):
        """Test getting available commands"""
        commands = self.protocol_handler.get_available_commands()
        
        self.assertIn('power', commands)
        self.assertIn('volume_up', commands)
        self.assertIn('volume_down', commands)
    
    def test_set_protocol(self):
        """Test setting IR protocol"""
        self.protocol_handler.set_protocol('rc5')
        self.assertEqual(self.protocol_handler.protocol, 'rc5')
    
    def test_add_custom_code(self):
        """Test adding custom IR code"""
        self.protocol_handler.add_custom_code('custom_command', '0x12345678')
        
        self.assertIn('custom_command', self.protocol_handler.codes)
        self.assertEqual(self.protocol_handler.codes['custom_command'], '0x12345678')

class TestTVControlAPI(unittest.TestCase):
    """Test cases for TV Control API"""
    
    def setUp(self):
        """Setup test environment"""
        # Mock TV controller
        self.mock_tv_controller = Mock()
        self.mock_tv_controller.send_command.return_value = CommandResult(
            success=True,
            command='power',
            timestamp=time.time()
        )
        self.mock_tv_controller.get_tv_status.return_value = TVStatus(
            power_state=TVState.ON,
            volume=50,
            channel=1,
            input_source='hdmi1',
            last_command='power',
            last_command_time=time.time()
        )
        self.mock_tv_controller.get_command_history.return_value = [
            ('power', time.time(), True),
            ('volume_up', time.time(), True)
        ]
        
        # Create API
        self.api = TVControlAPI(self.mock_tv_controller)
        self.client = self.api.app.test_client()
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/api/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_get_tv_status(self):
        """Test getting TV status"""
        response = self.client.get('/api/tv/status')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('power_state', data)
        self.assertIn('volume', data)
        self.assertIn('channel', data)
    
    def test_toggle_power(self):
        """Test toggling TV power"""
        response = self.client.post('/api/tv/power')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['command'], 'power')
    
    def test_control_volume(self):
        """Test volume control"""
        # Test volume up
        response = self.client.post('/api/tv/volume', 
                                  json={'action': 'up'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Test volume set
        response = self.client.post('/api/tv/volume', 
                                  json={'action': 'set', 'volume': 75})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_control_channel(self):
        """Test channel control"""
        # Test channel up
        response = self.client.post('/api/tv/channel', 
                                  json={'action': 'up'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Test channel set
        response = self.client.post('/api/tv/channel', 
                                  json={'action': 'set', 'channel': 5})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_change_input(self):
        """Test changing input source"""
        response = self.client.post('/api/tv/input', 
                                  json={'input': 'hdmi2'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_navigation_control(self):
        """Test navigation controls"""
        response = self.client.post('/api/tv/navigation', 
                                  json={'action': 'menu'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_custom_command(self):
        """Test custom command"""
        response = self.client.post('/api/tv/command', 
                                  json={'command': 'power'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_get_command_history(self):
        """Test getting command history"""
        response = self.client.get('/api/tv/history')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('history', data)
        self.assertIsInstance(data['history'], list)
    
    def test_get_available_commands(self):
        """Test getting available commands"""
        response = self.client.get('/api/tv/available-commands')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('commands', data)
        self.assertIsInstance(data['commands'], list)

class TestIntegration(unittest.TestCase):
    """Integration tests for complete system"""
    
    def setUp(self):
        """Setup integration test environment"""
        self.tv_config = {
            'brand': 'Samsung',
            'model': 'UN55MU8000',
            'protocol': 'nec',
            'carrier_frequency': 38000,
            'codes': {
                'power': '0xE0E040BF',
                'volume_up': '0xE0E0E01F',
                'volume_down': '0xE0E0D02F',
                'channel_up': '0xE0E048B7',
                'channel_down': '0xE0E008F7'
            }
        }
    
    @patch('software.agent.tv_controller.USBHIDInterface')
    @patch('software.agent.tv_controller.IRProtocolHandler')
    def test_complete_workflow(self, mock_protocol, mock_usb):
        """Test complete workflow from command to IR transmission"""
        # Setup mocks
        mock_usb_instance = Mock()
        mock_usb_instance.send_ir_signal.return_value = True
        mock_usb.return_value = mock_usb_instance
        
        mock_protocol_instance = Mock()
        mock_protocol_instance.encode_command.return_value = b'\x01\x02\x03'
        mock_protocol.return_value = mock_protocol_instance
        
        # Create TV controller
        tv_controller = TVController(
            usb_device_id='FSP2C01915A',
            tv_config=self.tv_config,
            learning_enabled=False,
            debug=True
        )
        
        # Test complete workflow
        result = tv_controller.send_command('power')
        
        # Verify results
        self.assertTrue(result.success)
        self.assertEqual(result.command, 'power')
        
        # Verify mock calls
        mock_protocol_instance.encode_command.assert_called_once_with('power', None)
        mock_usb_instance.send_ir_signal.assert_called_once_with(b'\x01\x02\x03')
    
    def test_error_handling(self):
        """Test error handling in complete system"""
        with patch('software.agent.tv_controller.USBHIDInterface') as mock_usb:
            with patch('software.agent.tv_controller.IRProtocolHandler') as mock_protocol:
                # Setup mocks to simulate failure
                mock_usb_instance = Mock()
                mock_usb_instance.send_ir_signal.return_value = False
                mock_usb.return_value = mock_usb_instance
                
                mock_protocol_instance = Mock()
                mock_protocol_instance.encode_command.return_value = b'\x01\x02\x03'
                mock_protocol.return_value = mock_protocol_instance
                
                # Create TV controller
                tv_controller = TVController(
                    usb_device_id='FSP2C01915A',
                    tv_config=self.tv_config,
                    learning_enabled=False,
                    debug=True
                )
                
                # Test error handling
                result = tv_controller.send_command('power')
                
                # Verify error handling
                self.assertFalse(result.success)
                self.assertIn('Failed to send IR signal', result.error_message)

def run_tests():
    """Run all test suites"""
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestTVController))
    test_suite.addTest(unittest.makeSuite(TestIRProtocolHandler))
    test_suite.addTest(unittest.makeSuite(TestTVControlAPI))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)

