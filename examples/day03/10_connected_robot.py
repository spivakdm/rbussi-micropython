"""Sensor telemetry + LED + nonblocking sound. No motor commands."""
from machine import Pin, PWM
from time import ticks_add
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

LEFT_GPIO = 34   # A3; white=0, black=1.
RIGHT_GPIO = 35  # A2; confirm sides by covering one sensor at a time.
left = Pin(LEFT_GPIO, Pin.IN)
right = Pin(RIGHT_GPIO, Pin.IN)

BUILTIN_LED_GPIO = 2
PIEZO_GPIO = 26  # D2; confirm free pin and suitable passive piezo circuit.
line_topic = (settings.TOPIC_PREFIX + "/telemetry/line").encode()
led_topic = (settings.TOPIC_PREFIX + "/cmd/led").encode()
beep_topic = (settings.TOPIC_PREFIX + "/cmd/beep").encode()
beep_until = None


# MQTT supplies topic and message as bytes.
def on_message(topic, message):
    global beep_until
    if topic == led_topic:
        if message == b"ON":
            led.value(1)
        elif message == b"OFF":
            led.value(0)
        else:
            print("Ignored LED command: expected ON or OFF")
    elif topic == beep_topic:
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
            sound.freq(frequency)
            sound.duty_u16(32768)
            # Schedule the stop time without a blocking sleep.
            beep_until = ticks_add(ticks_ms(), duration_ms)
        except (ValueError, KeyError, TypeError):
            print("Invalid beep command: use frequency and duration_ms")


led = Pin(BUILTIN_LED_GPIO, Pin.OUT, value=0)
pin = Pin(PIEZO_GPIO, Pin.OUT, value=0)
sound = PWM(pin, freq=2000, duty_u16=0)
try:
    client.set_callback(on_message)
    client.connect(timeout=10)
    client.subscribe(led_topic)
    client.subscribe(beep_topic)
    last_publish = ticks_add(ticks_ms(), -500)
    while True:
        client.check_msg()
        now = ticks_ms()
        if beep_until is not None and ticks_diff(now, beep_until) >= 0:
            sound.duty_u16(0)
            beep_until = None
        # Publish every 500 ms; process commands between publications.
        if ticks_diff(now, last_publish) >= 500:
            readings = {"left": left.value(), "right": right.value()}
            payload = json.dumps(readings)
            client.publish(line_topic, payload.encode(), retain=False)
            print(payload)
            last_publish = now
        sleep_ms(10)
finally:
    led.value(0)
    sound.duty_u16(0)  # Stop the PWM waveform before releasing it.
    sound.deinit()
    pin.value(0)

    if client.sock is not None:
        try:
            client.disconnect()
        except OSError:
            client.sock.close()
