# Home Assistant Installation & Setup

This guide covers the installation and initial setup of your Home Assistant instance.

## Current Installation

### System Information
- **Home Assistant Version:** 2025.9.4
- **Installation Method:** Docker Container
- **Location:** Kuwait (Asia/Kuwait)
- **Timezone:** Asia/Kuwait
- **Currency:** KWD
- **Language:** English

### Docker Setup
Your Home Assistant is running in a Docker container with the following configuration:

```yaml
# docker-compose.yml
version: '3.8'
services:
  homeassistant:
    container_name: homeassistant
    image: ghcr.io/home-assistant/home-assistant:stable
    volumes:
      - ./homeassistant/config:/config
      - /etc/localtime:/etc/localtime:ro
    restart: unless-stopped
    privileged: true
    network_mode: host
```

## Initial Configuration

### Core Settings
Your Home Assistant is configured with:
- **Location:** 29.2733964, 47.4979476 (Kuwait)
- **Elevation:** 0 meters
- **Unit System:** Metric
- **Radius:** 100 km

### Network Configuration
- **Internal URL:** Not configured (using default)
- **External URL:** Not configured
- **Port:** 8123 (default)
- **SSL Profile:** Modern

## First Steps After Installation

### 1. User Account Setup
- **Admin User:** admin
- **Authentication:** Home Assistant local authentication
- **Multi-factor Authentication:** Not configured

### 2. Onboarding Completed
The following onboarding steps have been completed:
- ✅ User creation
- ✅ Core configuration
- ✅ Analytics preferences
- ✅ Integration setup

### 3. Initial Integrations
Your system has the following integrations configured:
- **Sun** - Solar position tracking
- **go2rtc** - Real-time communication
- **Backup** - Automatic backups
- **Google Translate** - Text-to-speech
- **Shopping List** - Task management
- **Weather (Met.no)** - Weather data
- **Radio Browser** - Internet radio
- **D-Link** - Smart plug integration

## Access Information

### Web Interface
- **URL:** http://localhost:8123
- **Username:** admin
- **Password:** [Set during initial setup]

### API Access
- **API Endpoint:** http://localhost:8123/api
- **Long-lived Access Token:** Available in profile settings

## Backup Configuration

### Automatic Backups
- **Status:** Enabled
- **Frequency:** Automatic (default schedule)
- **Storage:** Local storage in `/config/backups/`
- **Last Backup:** Check backup manager in settings

### Manual Backup
To create a manual backup:
1. Go to Settings → System → Backups
2. Click "Create Backup"
3. Add a description
4. Click "Create"

## Security Considerations

### Authentication
- **Local Authentication:** Enabled
- **Login Attempts Threshold:** -1 (unlimited)
- **IP Ban:** Enabled

### Network Security
- **CORS Allowed Origins:** https://cast.home-assistant.io
- **X-Frame-Options:** Enabled
- **Trusted Proxies:** Not configured

## Next Steps

1. **Configure Integrations** - Set up your smart devices
2. **Create Automations** - Automate your home
3. **Customize Dashboard** - Organize your interface
4. **Set up Voice Assistant** - Enable voice control
5. **Configure Notifications** - Set up alerts and notifications

## Troubleshooting

### Common Issues
- **Container won't start:** Check Docker logs
- **Configuration errors:** Validate YAML syntax
- **Integration failures:** Check device connectivity

### Logs
- **Location:** `/config/home-assistant.log`
- **Level:** Info (default)
- **Rotation:** Automatic

### Support Resources
- [Home Assistant Documentation](https://www.home-assistant.io/docs/)
- [Community Forum](https://community.home-assistant.io/)
- [GitHub Issues](https://github.com/home-assistant/core/issues)

---

*This installation guide is specific to your Home Assistant setup.*
