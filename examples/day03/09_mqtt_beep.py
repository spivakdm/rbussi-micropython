"""Receive a short sound command. This first callback uses a blocking beep."""
from machine import Pin, PWM
import json

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

PIEZO_GPIO = 26  # D2; confirm free pin and suitable passive piezo circuit.
beep_topic = (settings.TOPIC_PREFIX + "/cmd/beep").encode()

def beep(frequency, duration_ms):
    sound.freq(frequency)
    sound.duty_u16(32768)
    sleep_ms(duration_ms)
    sound.duty_u16(0)


# MQTT supplies topic and message as bytes.
def on_message(topic, message):
    if topic == beep_topic:
        try:
            data = json.loads(message)
            frequency = data["frequency"]
            duration_ms = data["duration_ms"]
            if type(frequency) is not int or type(duration_ms) is not int:
                print("Use integer frequency and duration_ms")
                return
            if not (100 <= frequency <= 5000 and 20 <= duration_ms <= 1000):
                print("Use 100..5000 Hz and 20..1000 ms")
                return
            beep(frequency, duration_ms)
        except (ValueError, KeyError, TypeError):
            print("Invalid beep command: use frequency and duration_ms")


pin = Pin(PIEZO_GPIO, Pin.OUT, value=0)
sound = PWM(pin, freq=2000, duty_u16=0)
try:
    client.set_callback(on_message)
    client.connect(timeout=10)
    client.subscribe(beep_topic)
    print("Waiting for beep commands")

    last_ping = ticks_ms()
    while True:
        client.check_msg()
        # Keep the connection alive while waiting for commands.
        if ticks_diff(ticks_ms(), last_ping) >= 20000:
            client.ping()
            last_ping = ticks_ms()
        sleep_ms(10)

finally:
    sound.duty_u16(0)  # Stop the PWM waveform before releasing it.
    sound.deinit()
    pin.value(0)

    if client.sock is not None:
        try:
            client.disconnect()
        except OSError:
            client.sock.close()
