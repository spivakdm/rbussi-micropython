"""Receive a short sound command. This first callback uses a blocking beep."""
from machine import Pin, PWM
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
    connect_wifi()
    # TLS certificate verification needs the current UTC time.
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
    # Verify the server using the uploaded root CA.
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations(cafile=settings.CA_FILE)
    # MQTT uses bytes; keepalive is in seconds.
    return MQTTClient(
        settings.ESP32_CLIENT_ID.encode(), settings.MQTT_HOST,
        port=settings.MQTT_PORT, user=settings.MQTT_USER.encode(),
        password=settings.MQTT_PASSWORD.encode(), keepalive=60, ssl=context,
    )

PIEZO_GPIO = 26  # D2; confirm free pin and suitable passive piezo circuit.
beep_topic = (settings.TOPIC_PREFIX + "/cmd/beep").encode()

def read_beep(message):
    # Validate the command before starting a tone.
    try:
        data = json.loads(message)
        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object")
        frequency = data.get("frequency")
        duration_ms = data.get("duration_ms")
        # Reject non-integer values, including booleans.
        if type(frequency) is not int or type(duration_ms) is not int:
            raise ValueError("Use integer frequency and duration_ms")
        if not 100 <= frequency <= 5000 or not 20 <= duration_ms <= 1000:
            raise ValueError("Use 100..5000 Hz and 20..1000 ms")
        return frequency, duration_ms
    except (ValueError, TypeError):
        print("Ignored beep: expected integer frequency 100..5000, duration_ms 20..1000")
        return None


def beep(frequency, duration_ms):
    sound.freq(frequency)
    sound.duty_u16(32768)
    try:
        sleep_ms(duration_ms)
    finally:
        sound.duty_u16(0)


# MQTT supplies topic and message as bytes.
def on_message(topic, message):
    if topic == beep_topic:
        command = read_beep(message)
        if command is not None:
            frequency, duration_ms = command
            beep(frequency, duration_ms)


client = make_client()
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
        # Keep the connection alive when readings do not change.
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
            pass
        finally:
            client.sock.close()
