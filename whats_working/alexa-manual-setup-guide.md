# Alexa Home Assistant Manual Setup Guide

## Prerequisites
- Home Assistant running in Docker
- Amazon Echo Dot 5th generation
- Amazon Developer account
- AWS account
- Domain name or DuckDNS subdomain
- Basic understanding of SSL certificates

## Step 1: SSL Certificate Setup

### Option A: DuckDNS with Let's Encrypt (Recommended)

1. **Create DuckDNS account**
   - Go to [DuckDNS.org](https://www.duckdns.org/)
   - Create account and get subdomain (e.g., `myhome.duckdns.org`)

2. **Configure Home Assistant for SSL**
   ```yaml
   # Add to configuration.yaml
   http:
     use_x_forwarded_for: true
     trusted_proxies:
       - 127.0.0.1
       - ::1
     ssl_certificate: /config/ssl/fullchain.pem
     ssl_key: /config/ssl/privkey.pem
   ```

3. **Set up Let's Encrypt certificates**
   ```bash
   # Install certbot
   sudo apt-get update
   sudo apt-get install certbot
   
   # Generate certificates
   sudo certbot certonly --standalone -d myhome.duckdns.org
   
   # Copy certificates to Home Assistant config
   sudo cp /etc/letsencrypt/live/myhome.duckdns.org/fullchain.pem /path/to/homeassistant/config/ssl/
   sudo cp /etc/letsencrypt/live/myhome.duckdns.org/privkey.pem /path/to/homeassistant/config/ssl/
   ```

4. **Set up automatic renewal**
   ```bash
   # Add to crontab
   sudo crontab -e
   # Add this line:
   0 12 * * * /usr/bin/certbot renew --quiet && docker restart homeassistant
   ```

### Option B: Cloudflare Tunnel (Alternative)

1. **Install Cloudflare Tunnel**
   ```bash
   # Download cloudflared
   wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
   sudo dpkg -i cloudflared-linux-amd64.deb
   ```

2. **Authenticate with Cloudflare**
   ```bash
   cloudflared tunnel login
   ```

3. **Create tunnel**
   ```bash
   cloudflared tunnel create homeassistant
   ```

4. **Configure tunnel**
   ```yaml
   # config.yml
   tunnel: homeassistant
   credentials-file: /root/.cloudflared/homeassistant.json
   
   ingress:
     - hostname: myhome.duckdns.org
       service: http://localhost:8123
     - service: http_status:404
   ```

## Step 2: Amazon Developer Setup

1. **Create Amazon Developer Account**
   - Go to [developer.amazon.com](https://developer.amazon.com/)
   - Sign up for developer account
   - Complete verification process

2. **Create Alexa Skill**
   - Go to Alexa Skills Kit
   - Click "Create Skill"
   - Choose "Smart Home" as skill type
   - Name your skill (e.g., "Home Assistant Control")

3. **Configure Skill Information**
   ```json
   {
     "skillName": "Home Assistant Control",
     "skillDescription": "Control Home Assistant devices via Alexa",
     "category": "SMART_HOME"
   }
   ```

## Step 3: AWS Lambda Function

1. **Create Lambda Function**
   - Go to AWS Lambda console
   - Create new function
   - Choose "Author from scratch"
   - Name: "HomeAssistantAlexa"
   - Runtime: Python 3.9

2. **Lambda Function Code**
   ```python
   import json
   import requests
   import os
   
   def lambda_handler(event, context):
       # Home Assistant configuration
       HA_URL = os.environ['HA_URL']
       HA_TOKEN = os.environ['HA_TOKEN']
       
       # Handle different request types
       if event['directive']['header']['name'] == 'DiscoverAppliancesRequest':
           return discover_appliances(HA_URL, HA_TOKEN)
       elif event['directive']['header']['name'] == 'TurnOnRequest':
           return control_appliance(event, HA_URL, HA_TOKEN, 'turn_on')
       elif event['directive']['header']['name'] == 'TurnOffRequest':
           return control_appliance(event, HA_URL, HA_TOKEN, 'turn_off')
       # Add more handlers as needed
   
   def discover_appliances(ha_url, ha_token):
       # Get Home Assistant entities
       headers = {
           'Authorization': f'Bearer {ha_token}',
           'Content-Type': 'application/json'
       }
       
       response = requests.get(f'{ha_url}/api/states', headers=headers)
       entities = response.json()
       
       appliances = []
       for entity in entities:
           if entity['entity_id'].startswith(('light.', 'switch.', 'fan.', 'climate.')):
               appliances.append({
                   'applianceId': entity['entity_id'],
                   'manufacturerName': 'Home Assistant',
                   'modelName': entity['attributes'].get('friendly_name', entity['entity_id']),
                   'version': '1.0',
                   'friendlyName': entity['attributes'].get('friendly_name', entity['entity_id']),
                   'friendlyDescription': f"Home Assistant {entity['entity_id']}",
                   'isReachable': True,
                   'actions': get_actions_for_entity(entity['entity_id'])
               })
       
       return {
           'event': {
               'header': {
                   'namespace': 'Alexa.Discovery',
                   'name': 'DiscoverAppliancesResponse',
                   'payloadVersion': '3',
                   'messageId': str(uuid.uuid4())
               },
               'payload': {
                   'discoveredAppliances': appliances
               }
           }
       }
   
   def control_appliance(event, ha_url, ha_token, action):
       appliance_id = event['directive']['endpoint']['endpointId']
       
       headers = {
           'Authorization': f'Bearer {ha_token}',
           'Content-Type': 'application/json'
       }
       
       data = {
           'entity_id': appliance_id
       }
       
       response = requests.post(f'{ha_url}/api/services/{appliance_id.split(".")[0]}/{action}', 
                              headers=headers, json=data)
       
       return {
           'event': {
               'header': {
                   'namespace': 'Alexa',
                   'name': 'Response',
                   'payloadVersion': '3',
                   'messageId': str(uuid.uuid4())
               },
               'payload': {}
           }
       }
   ```

3. **Set Environment Variables**
   ```
   HA_URL=https://myhome.duckdns.org
   HA_TOKEN=your-homeassistant-long-lived-access-token
   ```

4. **Create API Gateway**
   - Go to API Gateway console
   - Create new API
   - Choose "REST API"
   - Create resource and method
   - Link to Lambda function

## Step 4: Home Assistant Configuration

1. **Create Long-lived Access Token**
   - Go to Home Assistant profile
   - Scroll to "Long-lived access tokens"
   - Create new token
   - Copy token for Lambda function

2. **Configure Alexa Integration**
   ```yaml
   # Add to configuration.yaml
   alexa:
     smart_home:
       endpoint: https://your-api-gateway-url.amazonaws.com/prod
       client_id: your-alexa-skill-client-id
       client_secret: your-alexa-skill-client-secret
   ```

3. **Expose Entities to Alexa**
   ```yaml
   # Add to customize.yaml
   light.living_room:
     alexa: true
     friendly_name: "Living Room Light"
   
   switch.coffee_maker:
     alexa: true
     friendly_name: "Coffee Maker"
   
   climate.bedroom:
     alexa: true
     friendly_name: "Bedroom Temperature"
   ```

## Step 5: Testing and Verification

1. **Test SSL Certificate**
   ```bash
   curl -I https://myhome.duckdns.org
   # Should return 200 OK with SSL
   ```

2. **Test Home Assistant API**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        -H "Content-Type: application/json" \
        https://myhome.duckdns.org/api/
   ```

3. **Test Alexa Skill**
   - Enable skill in Alexa app
   - Test voice commands
   - Check Lambda function logs

## Step 6: Advanced Configuration

### Custom Entity Names
```yaml
# customize.yaml
light.living_room:
  alexa: true
  friendly_name: "Living Room Light"
  alexa_name: "Living Room Light"
  alexa_description: "Main living room light"

switch.coffee_maker:
  alexa: true
  friendly_name: "Coffee Maker"
  alexa_name: "Coffee Maker"
  alexa_description: "Smart coffee maker"
```

### Scene Control
```yaml
# scenes.yaml
- name: "Good Morning"
  entities:
    light.living_room: "on"
    light.bedroom: "on"
    switch.coffee_maker: "on"

- name: "Good Night"
  entities:
    light.living_room: "off"
    light.bedroom: "off"
    switch.coffee_maker: "off"
```

### Automation Integration
```yaml
# automations.yaml
- alias: "Alexa Good Morning"
  trigger:
    platform: alexa
    event: "Good Morning"
  action:
    - service: scene.turn_on
      entity_id: scene.good_morning
```

## Troubleshooting

### Common Issues

1. **SSL Certificate Issues**
   - Check certificate validity: `openssl x509 -in fullchain.pem -text -noout`
   - Verify domain configuration
   - Test with SSL Labs: https://www.ssllabs.com/ssltest/

2. **Lambda Function Errors**
   - Check CloudWatch logs
   - Verify environment variables
   - Test API connectivity

3. **Alexa Skill Issues**
   - Verify skill configuration
   - Check endpoint URL
   - Test with Alexa simulator

4. **Home Assistant API Issues**
   - Check long-lived token
   - Verify entity exposure
   - Test API endpoints

### Debug Commands
```bash
# Test SSL certificate
openssl s_client -connect myhome.duckdns.org:443

# Test Home Assistant API
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://myhome.duckdns.org/api/states

# Check Lambda function logs
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/HomeAssistantAlexa
```

## Security Best Practices

1. **SSL Certificate Security**
   - Use strong encryption (TLS 1.2+)
   - Regular certificate renewal
   - Monitor certificate expiration

2. **API Security**
   - Secure API endpoints
   - Use authentication tokens
   - Implement rate limiting

3. **Network Security**
   - Configure firewall rules
   - Use VPN if needed
   - Regular security updates

## Maintenance

1. **Certificate Renewal**
   - Set up automatic renewal
   - Monitor certificate expiration
   - Test renewal process

2. **Lambda Function Updates**
   - Regular code updates
   - Monitor function logs
   - Update dependencies

3. **Home Assistant Updates**
   - Keep Home Assistant updated
   - Test integration after updates
   - Backup configuration

## Cost Analysis

- **DuckDNS:** Free
- **Let's Encrypt:** Free
- **AWS Lambda:** Free tier (1M requests/month)
- **API Gateway:** Free tier (1M requests/month)
- **Total Monthly Cost:** $0 (within free tiers)

## Conclusion

This manual setup provides a free alternative to Home Assistant Cloud while maintaining full control over the integration. The setup requires technical expertise but offers complete customization and no ongoing subscription costs.
