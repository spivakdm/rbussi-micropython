"""Receive ON/OFF for the built-in LED. Motor power off; Ctrl+C stops."""
from machine import Pin

import network
import ssl
import ntptime
import network_secrets as settings
from time import sleep_ms, ticks_ms, ticks_diff, gmtime
from umqtt.simple import MQTTClient

def connect_wifi():
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
    return wlan


def make_client():
    # Supplied connection template: Wi-Fi, clock, CA verification, credentials.
    connect_wifi()
    if settings.SYNC_NTP:
        ntptime.host = settings.NTP_HOST
        ntptime.timeout = 3
        for attempt in range(3):
            try:
                ntptime.settime()
                break
            except OSError:
                if attempt == 2:
                    raise OSError("NTP failed: set current UTC RTC; see README")
                sleep_ms(500)
    if gmtime()[0] < 2026:
        raise OSError("Set the board RTC to current UTC before TLS")
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations(cafile=settings.CA_FILE)
    return MQTTClient(
        settings.ESP32_CLIENT_ID.encode(), settings.MQTT_HOST,
        port=settings.MQTT_PORT, user=settings.MQTT_USER.encode(),
        password=settings.MQTT_PASSWORD.encode(), keepalive=60, ssl=context,
    )

BUILTIN_LED_GPIO = 2
led_topic = (settings.TOPIC_PREFIX + "/cmd/led").encode()

def on_message(topic, message):
    if topic == led_topic:
        if message == b"ON":
            led.value(1)
        elif message == b"OFF":
            led.value(0)
        else:
            print("Ignored LED command: expected ON or OFF")

client = make_client()
led = Pin(BUILTIN_LED_GPIO, Pin.OUT, value=0)
try:
    client.set_callback(on_message)
    client.connect(timeout=10)
    client.subscribe(led_topic)
    print("Waiting for LED commands")

    last_ping = ticks_ms()
    while True:
        client.check_msg()
        if ticks_diff(ticks_ms(), last_ping) >= 20000:
            client.ping()
            last_ping = ticks_ms()
        sleep_ms(10)

finally:
    led.value(0)

    if client.sock is not None:
        try:
            client.disconnect()
        except OSError:
            pass
        finally:
            client.sock.close()
