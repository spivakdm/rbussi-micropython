"""Receive forward and drive for one second. First test with wheels lifted."""
from robot import RBussi

import network
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

client = MQTTClient(
    settings.ESP32_CLIENT_ID.encode(), settings.MQTT_HOST,
    port=settings.MQTT_PORT, user=settings.MQTT_USER.encode(),
    password=settings.MQTT_PASSWORD.encode(), keepalive=60,
)

move_topic = (settings.TOPIC_PREFIX + "/cmd/move").encode()


def on_message(topic, message):
    if topic == move_topic:
        if message == b"forward":
            print("Forward for one second")
            robot.forward(speed=40, seconds=1)
        else:
            print("Ignored command: expected forward")


robot = RBussi()
try:
    client.set_callback(on_message)
    client.connect(timeout=10)
    client.subscribe(move_topic)
    print("Waiting for forward on /cmd/move")

    last_ping = ticks_ms()
    while True:
        client.check_msg()
        # Keep the connection alive while waiting for commands.
        if ticks_diff(ticks_ms(), last_ping) >= 20000:
            client.ping()
            last_ping = ticks_ms()
        sleep_ms(10)

finally:
    robot.close()

    if client.sock is not None:
        try:
            client.disconnect()
        except OSError:
            client.sock.close()
