"""Sensor telemetry + LED + nonblocking sound. No motor commands."""
from machine import Pin, PWM
from time import ticks_add
import json

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

def read_beep(message):
    # Reject malformed JSON, missing fields, booleans and out-of-range values.
    try:
        data = json.loads(message)
        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object")
        frequency = data.get("frequency")
        duration_ms = data.get("duration_ms")
        if type(frequency) is not int or type(duration_ms) is not int:
            raise ValueError("Use integer frequency and duration_ms")
        if not 100 <= frequency <= 5000 or not 20 <= duration_ms <= 1000:
            raise ValueError("Use 100..5000 Hz and 20..1000 ms")
        return frequency, duration_ms
    except (ValueError, TypeError):
        print("Ignored beep: expected integer frequency 100..5000, duration_ms 20..1000")
        return None


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
        command = read_beep(message)
        if command is not None:
            frequency, duration_ms = command
            sound.freq(frequency)
            sound.duty_u16(32768)
            beep_until = ticks_add(ticks_ms(), duration_ms)
            # A new valid command replaces the current tone; no sleep here.


client = make_client()
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
        if ticks_diff(now, last_publish) >= 500:
            readings = {"left": left.value(), "right": right.value()}
            payload = json.dumps(readings)
            client.publish(line_topic, payload.encode(), retain=False)
            print(payload)
            last_publish = now
        sleep_ms(10)
finally:
    led.value(0)
    sound.duty_u16(0)
    sound.deinit()
    pin.value(0)

    if client.sock is not None:
        try:
            client.disconnect()
        except OSError:
            pass
        finally:
            client.sock.close()
