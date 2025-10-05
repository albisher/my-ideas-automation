# Common Issues and Troubleshooting

This guide covers common issues you might encounter with your Home Assistant setup and how to resolve them.

## System Issues

### Home Assistant Won't Start

#### Symptoms
- Container fails to start
- Web interface not accessible
- Configuration errors

#### Solutions
1. **Check Docker Logs**
   ```bash
   docker logs homeassistant
   ```

2. **Verify Configuration**
   ```bash
   docker exec homeassistant python -m homeassistant --script check_config
   ```

3. **Check Port Conflicts**
   - Ensure port 8123 is available
   - Check for other services using the port

4. **Verify File Permissions**
   - Check config directory permissions
   - Ensure proper ownership

### Configuration Errors

#### Symptoms
- YAML syntax errors
- Integration failures
- Entity not found errors

#### Solutions
1. **Validate YAML Syntax**
   - Use YAML validator
   - Check indentation
   - Verify quotes and brackets

2. **Check Integration Status**
   - Go to Configuration → Integrations
   - Look for failed integrations
   - Check integration logs

3. **Restart Home Assistant**
   - Restart the container
   - Clear browser cache
   - Check logs after restart

## Integration Issues

### D-Link Smart Plug Connection Issues

#### Current Issue
Your D-Link smart plug is experiencing connection issues:

```
ERROR: AttributeError: 'NoneType' object has no attribute 'text'
```

#### Symptoms
- Smart plug not responding
- Authentication failures
- Connection timeouts

#### Solutions
1. **Check Network Connectivity**
   ```bash
   ping 192.168.68.51
   ```

2. **Verify Credentials**
   - Check username/password
   - Test with D-Link app
   - Reset device if needed

3. **Check Firewall Settings**
   - Ensure port 80/443 are open
   - Check for network restrictions

4. **Update Integration**
   - Check for integration updates
   - Restart the integration
   - Check integration logs

### MQTT Connection Issues

#### Symptoms
- MQTT sensors not updating
- Connection timeouts
- Message delivery failures

#### Solutions
1. **Check MQTT Broker**
   ```bash
   docker logs mqtt_broker
   ```

2. **Verify MQTT Configuration**
   - Check broker settings
   - Verify username/password
   - Test connection manually

3. **Check Network**
   - Ensure broker is accessible
   - Check firewall settings
   - Verify port 1883 is open

4. **Test MQTT Connection**
   - Use MQTT client to test
   - Check topic subscriptions
   - Verify message publishing

### Frigate NVR Issues

#### Symptoms
- Camera feed not working
- Object detection not functioning
- Recording failures

#### Solutions
1. **Check Frigate Status**
   ```bash
   docker logs frigate
   ```

2. **Verify Camera Stream**
   - Test RTSP stream directly
   - Check camera credentials
   - Verify network connectivity

3. **Check Frigate Configuration**
   - Validate configuration file
   - Check model loading
   - Verify detection settings

4. **Monitor Performance**
   - Check CPU usage
   - Monitor memory usage
   - Check disk space

## Entity Issues

### Entities Not Updating

#### Symptoms
- Entity states stuck
- No state changes
- Unknown/unavailable states

#### Solutions
1. **Check Entity Status**
   - Go to Developer Tools → States
   - Look for unknown entities
   - Check last updated times

2. **Restart Integration**
   - Go to Configuration → Integrations
   - Restart the integration
   - Check integration logs

3. **Check Network**
   - Verify device connectivity
   - Check for network issues
   - Test device communication

### Motion Detection Not Working

#### Symptoms
- Motion sensors not triggering
- No motion events
- False positives/negatives

#### Solutions
1. **Check Sensor Status**
   - Verify sensor is online
   - Check sensor configuration
   - Test sensor manually

2. **Check Frigate Configuration**
   - Verify motion zones
   - Check detection sensitivity
   - Review motion settings

3. **Check MQTT Topics**
   - Verify topic publishing
   - Check message format
   - Test MQTT connection

### Object Detection Issues

#### Symptoms
- No object detection
- Incorrect counts
- Detection not working

#### Solutions
1. **Check Frigate Model**
   - Verify model is loaded
   - Check model performance
   - Update model if needed

2. **Check Detection Settings**
   - Verify detection zones
   - Check sensitivity settings
   - Review object filters

3. **Check MQTT Integration**
   - Verify topic subscriptions
   - Check message format
   - Test MQTT connection

## Dashboard Issues

### Cards Not Displaying

#### Symptoms
- Cards not showing
- Empty dashboard
- Card errors

#### Solutions
1. **Check Card Configuration**
   - Verify YAML syntax
   - Check entity IDs
   - Validate card types

2. **Check Entity States**
   - Verify entities exist
   - Check entity states
   - Test entity functionality

3. **Clear Browser Cache**
   - Clear browser cache
   - Hard refresh page
   - Check browser console

### Camera Feed Issues

#### Symptoms
- Camera not loading
- Stream not working
- Video quality issues

#### Solutions
1. **Check Camera Entity**
   - Verify camera entity exists
   - Check camera state
   - Test camera functionality

2. **Check Stream Source**
   - Verify RTSP stream
   - Test stream directly
   - Check camera credentials

3. **Check Network**
   - Verify network connectivity
   - Check bandwidth
   - Test from different devices

## Performance Issues

### Slow Dashboard Loading

#### Symptoms
- Dashboard loads slowly
- Cards not responsive
- Timeout errors

#### Solutions
1. **Check System Resources**
   - Monitor CPU usage
   - Check memory usage
   - Verify disk space

2. **Optimize Dashboard**
   - Reduce card count
   - Use conditional cards
   - Optimize images

3. **Check Network**
   - Verify network speed
   - Check for network issues
   - Test from different locations

### High CPU Usage

#### Symptoms
- System running slowly
- High CPU usage
- Performance degradation

#### Solutions
1. **Check Running Processes**
   - Monitor system processes
   - Check for resource hogs
   - Identify problematic services

2. **Optimize Configuration**
   - Reduce automation complexity
   - Check for infinite loops
   - Optimize integrations

3. **Check Logs**
   - Review error logs
   - Look for repeated errors
   - Check for memory leaks

## Backup and Recovery

### Backup Issues

#### Symptoms
- Backups failing
- Backup corruption
- Storage issues

#### Solutions
1. **Check Storage Space**
   - Verify disk space
   - Clean up old backups
   - Check storage permissions

2. **Check Backup Configuration**
   - Verify backup settings
   - Check backup schedule
   - Test backup manually

3. **Check Logs**
   - Review backup logs
   - Look for error messages
   - Check backup status

### Recovery Issues

#### Symptoms
- Restore failing
- Backup not found
- Configuration errors

#### Solutions
1. **Check Backup Files**
   - Verify backup exists
   - Check backup integrity
   - Test backup file

2. **Check Permissions**
   - Verify file permissions
   - Check directory access
   - Ensure proper ownership

3. **Check Configuration**
   - Validate configuration
   - Check for conflicts
   - Test configuration

## Getting Help

### Log Analysis

#### Check Logs
1. **Home Assistant Logs**
   - Go to Configuration → Logs
   - Look for error messages
   - Check warning messages

2. **Integration Logs**
   - Check specific integration logs
   - Look for connection errors
   - Check authentication issues

3. **System Logs**
   - Check Docker logs
   - Review system logs
   - Check network logs

### Debug Tools

#### Developer Tools
1. **States**
   - Check entity states
   - Verify state changes
   - Test entity functionality

2. **Services**
   - Test service calls
   - Check service parameters
   - Verify service responses

3. **Events**
   - Monitor system events
   - Check automation triggers
   - Verify event data

### Community Support

#### Resources
- [Home Assistant Community Forum](https://community.home-assistant.io/)
- [GitHub Issues](https://github.com/home-assistant/core/issues)
- [Discord Chat](https://discord.gg/c5DvZ4e)

#### Getting Help
1. **Search Existing Issues**
   - Check forum posts
   - Look for similar issues
   - Review solutions

2. **Provide Information**
   - Include error messages
   - Provide configuration
   - Share logs

3. **Be Specific**
   - Describe the problem
   - Include steps to reproduce
   - Provide system information

---

*This troubleshooting guide is specific to your Home Assistant setup and common issues you might encounter.*
