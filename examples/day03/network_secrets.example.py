"""Copy to network_secrets.py locally; never share your filled-in copy."""
# Ordinary 2.4 GHz SSID/password Wi-Fi; keep these values private.
WIFI_SSID = "YOUR_2_4_GHZ_WIFI"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# Copy your assigned account values exactly; MQTT/TCP uses port 1883, with TLS disabled.
MQTT_HOST = "mqtt.ondroid.org"
MQTT_PORT = 1883
MQTT_USER = "YOUR_ASSIGNED_USERNAME"
MQTT_PASSWORD = "YOUR_ASSIGNED_PASSWORD"

# Each student has a separate namespace and two different connection IDs.
TOPIC_PREFIX = "edu-2026-10/robot01"  # Replace with YOUR assigned prefix.
ESP32_CLIENT_ID = "edu-2026-10-robot01-esp32"  # Use your account card.
PC_CLIENT_ID = "edu-2026-10-robot01-pc"        # Different from ESP32.
