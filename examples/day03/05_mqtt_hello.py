"""Publish one hello message. Start the computer subscriber first."""

import network
import ssl
import ntptime
import network_secrets as settings
from time import sleep_ms, ticks_ms, ticks_diff
from umqtt.simple import MQTTClient

wlan = network.WLAN()
wlan.active(True)
if not wlan.isconnected():
    wlan.connect(settings.WIFI_SSID, settings.WIFI_PASSWORD)

started = ticks_ms()
while not wlan.isconnected():
    if ticks_diff(ticks_ms(), started) >= 15000:
        wlan.disconnect()
        raise OSError("Wi-Fi timeout: check 2.4 GHz, password and network access")
    sleep_ms(250)
print("Wi-Fi connected; IP:", wlan.ifconfig()[0])

# TLS needs the current UTC time and the uploaded root CA.
if settings.SYNC_NTP:
    ntptime.host = settings.NTP_HOST
    ntptime.timeout = 3
    ntptime.settime()

context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations(cafile=settings.CA_FILE)

client = MQTTClient(
    settings.ESP32_CLIENT_ID.encode(), settings.MQTT_HOST,
    port=settings.MQTT_PORT, user=settings.MQTT_USER.encode(),
    password=settings.MQTT_PASSWORD.encode(), keepalive=60, ssl=context,
)


try:
    client.connect(timeout=10)
    topic = (settings.TOPIC_PREFIX + "/telemetry/hello").encode()
    client.publish(topic, b"hello", retain=False)
    print("Sent hello to", topic)
finally:
    if client.sock is not None:
        try:
            client.disconnect()
        except OSError:
            client.sock.close()
