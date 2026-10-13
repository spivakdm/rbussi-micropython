"""Copy to network_secrets.py locally; never share your filled-in copy."""
# Ordinary 2.4 GHz SSID/password Wi-Fi; keep these values private.
WIFI_SSID = "YOUR_2_4_GHZ_WIFI"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# Copy your assigned account values exactly; TLS/TCP uses port 8883.
MQTT_HOST = "mqtt.ondroid.org"
MQTT_PORT = 8883
MQTT_USER = "YOUR_ASSIGNED_USERNAME"
MQTT_PASSWORD = "YOUR_ASSIGNED_PASSWORD"

# Each student has a separate namespace and two different connection IDs.
TOPIC_PREFIX = "edu-2026-10/robot01"  # Replace with YOUR assigned prefix.
ESP32_CLIENT_ID = "edu-2026-10-robot01-esp32"  # Use your account card.
PC_CLIENT_ID = "edu-2026-10-robot01-pc"        # Different from ESP32.

# Public trust material on the ESP32: shared by all students, not a private key.
CA_FILE = "certs/isrg-root-x1.pem"

# TLS needs the real current UTC clock, normally set over NTP.
NTP_HOST = "pool.ntp.org"
SYNC_NTP = True  # False only after setting the board RTC to current UTC.
