# Your Current Home Assistant Configuration

This document details your specific Home Assistant setup, including all configured integrations, entities, and customizations.

## System Overview

### Basic Information
- **Home Assistant Version:** 2025.9.4
- **Installation:** Docker Container
- **Location:** Kuwait (29.2733964, 47.4979476)
- **Timezone:** Asia/Kuwait
- **Currency:** KWD
- **Language:** English
- **Unit System:** Metric

### Network Configuration
- **Internal URL:** Not configured (default)
- **External URL:** Not configured
- **Port:** 8123
- **SSL Profile:** Modern
- **CORS Origins:** https://cast.home-assistant.io

## Active Integrations

### Core Integrations
1. **Sun Integration**
   - **Purpose:** Solar position tracking
   - **Entities:** Sun position, dawn/dusk times, solar elevation/azimuth
   - **Status:** Active

2. **Backup Integration**
   - **Purpose:** Automatic system backups
   - **Entities:** Backup manager state, schedule info
   - **Status:** Active with automatic backups enabled

3. **Google Translate TTS**
   - **Purpose:** Text-to-speech functionality
   - **Language:** English (en-us)
   - **Status:** Active

4. **Weather (Met.no)**
   - **Purpose:** Local weather data
   - **Location:** Home (Kuwait)
   - **Track Home:** Enabled
   - **Status:** Active

5. **Radio Browser**
   - **Purpose:** Internet radio streaming
   - **Status:** Active

6. **D-Link Smart Plug**
   - **Host:** 192.168.68.51
   - **Username:** admin
   - **Status:** Active (with connection issues)

### Voice Assistant Configuration
- **TTS Engine:** Google Translate
- **Language:** English (en-us)
- **Wake Word:** Not configured
- **Exposed Entities:** Motion sensors

## Entity Registry

### Motion Detection Entities
```
binary_sensor.dcs_8000lh_motion
binary_sensor.dcs_8000lh_motion_1
binary_sensor.dcs_8000lh_motion_2
```

### Object Detection Sensors
```
sensor.dcs_8000lh_person_count
sensor.dcs_8000lh_car_count
sensor.dcs_8000lh_person_count_1
sensor.dcs_8000lh_car_count_1
sensor.dcs_8000lh_person_count_2
sensor.dcs_8000lh_car_count_2
sensor.dcs_8000lh_motion_raw
```

### Scripts
```
script.take_camera_snapshot
script.restart_frigate
script.motion_alert
script.test_mqtt
```

### Automations
```
automation.motion_detection_alert
automation.person_detection_alert
automation.car_detection_alert
automation.night_mode_activation
automation.day_mode_activation
automation.tapo_motion_response
automation.security_mode_activation
automation.security_mode_deactivation
automation.dcs_8000lh_motion_detected
automation.dcs_8000lh_person_detected
automation.dcs_8000lh_car_detected
```

### System Entities
```
person.admin
tts.google_translate_en_com
todo.shopping_list
weather.forecast_home
event.backup_automatic_backup
sensor.backup_backup_manager_state
sensor.backup_next_scheduled_automatic_backup
sensor.backup_last_successful_automatic_backup
sensor.backup_last_attempted_automatic_backup
```

## Areas Configuration

### Defined Areas
1. **Living Room**
   - **ID:** living_room
   - **Created:** 2025-09-25T17:02:06.919016+00:00

2. **Kitchen**
   - **ID:** kitchen
   - **Created:** 2025-09-25T17:02:06.919061+00:00

3. **Bedroom**
   - **ID:** bedroom
   - **Created:** 2025-09-25T17:02:06.919072+00:00

## Dashboard Configuration

### Main Dashboard (ui-lovelace.yaml)
- **Title:** DCS-8000LH Camera System
- **View:** Overview (default)

#### Cards Configuration
1. **Camera System (Vertical Stack)**
   - Camera card: `camera.dcs_8000lh_camera`
   - Name: "DCS-8000LH Live Feed"

2. **Motion Detection (Entities)**
   - `binary_sensor.dcs_8000lh_motion`
   - `sensor.dcs_8000lh_person_count`
   - `sensor.dcs_8000lh_car_count`

3. **MQTT Status (Entities)**
   - `binary_sensor.dcs_8000lh_motion_mqtt`
   - `sensor.dcs_8000lh_person_count_mqtt`
   - `sensor.dcs_8000lh_car_count_mqtt`

### Additional Dashboards
- **Map Dashboard** - Geographic view with map integration

## Blueprints Available

### Automation Blueprints
1. **Motion-activated Light**
   - **File:** `blueprints/automation/homeassistant/motion_light.yaml`
   - **Purpose:** Turn on lights when motion is detected
   - **Author:** Home Assistant

2. **Zone Notification**
   - **File:** `blueprints/automation/homeassistant/notify_leaving_zone.yaml`
   - **Purpose:** Notify when person leaves a zone
   - **Author:** Home Assistant

### Script Blueprints
1. **Confirmable Notification**
   - **File:** `blueprints/script/homeassistant/confirmable_notification.yaml`
   - **Purpose:** Send actionable notifications with confirmation
   - **Author:** Home Assistant

### Template Blueprints
1. **Inverted Binary Sensor**
   - **File:** `blueprints/template/homeassistant/inverted_binary_sensor.yaml`
   - **Purpose:** Create inverted binary sensor
   - **Author:** Home Assistant

## Configuration Files

### Main Configuration (configuration.yaml)
```yaml
# Home Assistant Configuration with Tapo Integration
default_config:

# Enable discovery for Tapo devices
discovery:
  enable:
    - tapo

# Enable mDNS discovery for Tapo devices
zeroconf:
```

### Include Files
- `automations.yaml` - Empty (automations in storage)
- `scripts.yaml` - Empty (scripts in storage)
- `scenes.yaml` - Empty (scenes in storage)
- `groups.yaml` - Empty (groups in storage)
- `entities.yaml` - Empty (entities in storage)

## Security Configuration

### Authentication
- **Provider:** Home Assistant local authentication
- **Users:** admin (owner)
- **Multi-factor Authentication:** Not configured
- **Login Attempts Threshold:** -1 (unlimited)
- **IP Ban:** Enabled

### Network Security
- **X-Frame-Options:** Enabled
- **CORS:** Limited to cast.home-assistant.io
- **Trusted Proxies:** Not configured

## Backup Configuration

### Automatic Backups
- **Status:** Enabled
- **Manager State:** Available
- **Next Scheduled:** Check backup manager
- **Last Successful:** Check backup manager
- **Last Attempted:** Check backup manager

## Voice Assistant Settings

### Assist Pipeline
- **Conversation Engine:** conversation.home_assistant
- **Language:** English
- **TTS Engine:** google_translate
- **TTS Language:** en-us
- **Wake Word:** Not configured
- **Local Intents:** Disabled

### Exposed Entities
Motion sensors are exposed to voice assistant:
- `binary_sensor.dcs_8000lh_motion`
- `binary_sensor.dcs_8000lh_motion_1`
- `binary_sensor.dcs_8000lh_motion_2`

## Known Issues

### D-Link Smart Plug
- **Issue:** Authentication failures
- **Error:** `AttributeError: 'NoneType' object has no attribute 'text'`
- **Status:** Connection issues with smart plug at 192.168.68.51

### Configuration Warnings
- **Platform Integration:** No support for camera generic platform
- **Config Entry:** Only UPNP configuration detected

## Performance Metrics

### System Health
- **Analytics:** Enabled (base and diagnostics)
- **UUID:** 6d77aa9aae6345879ce6c14bcb1aac17
- **Onboarding:** Completed

### Storage Usage
- **Configuration:** Stored in `/config/`
- **Backups:** Local storage
- **Logs:** Rotated automatically

---

*This configuration overview is specific to your Home Assistant setup as of the last update.*
