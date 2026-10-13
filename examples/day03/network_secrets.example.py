"""Copy to network_secrets.py locally; never share your filled-in copy."""
WIFI_SSID = "YOUR_2_4_GHZ_WIFI"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
MQTT_HOST = "mqtt.ondroid.org"
MQTT_PORT = 8883
MQTT_USER = "YOUR_ASSIGNED_USERNAME"
MQTT_PASSWORD = "YOUR_ASSIGNED_PASSWORD"
TOPIC_PREFIX = "edu-2026-10/robot01"  # Replace with YOUR assigned prefix.
ESP32_CLIENT_ID = "edu-2026-10-robot01-esp32"  # Use your account card.
PC_CLIENT_ID = "edu-2026-10-robot01-pc"        # Different from ESP32.
CA_FILE = "certs/isrg-root-x1.pem"
NTP_HOST = "pool.ntp.org"
SYNC_NTP = True  # False only after setting the board RTC to current UTC.
