# Day 3 — Sound, Wi-Fi and MQTT

English slide outline. Metropolia ICT Summer School, 14 October 2026.

## 1. Sound, Wi-Fi and MQTT

Day 3 · Wednesday 14 October 2026
13:00–17:00 · MMC245

Introduction to Mobile Robotics
with a Remote Laboratory

Dmitrii Spivak



Instructor note: Metropolia ICT Summer School, course TX00GZ66-3001, 3 ECTS. First demonstrate the verified MQTT beep.

## 2. Today’s route

13:00   Sound: frequency, PWM and functions
14:00   Connect the ESP32 to Wi-Fi
14:20   Break
14:35   MQTT Explorer and first messages
15:00   Sensor telemetry
15:35   Break
15:50   Commands: LED, sound, movement
16:50   Demonstrate and save



Instructor note: Sound 01–03; melodies 11–13 optional. MQTT Explorer setup 14:35–14:45; hello 14:45–15:00. Examples 10 and 14 are alternative extensions, not both mandatory.

## 3. Make one short sound



```python
from machine import Pin, PWM
from time import sleep_ms

sound = PWM(Pin(26), freq=2000, duty_u16=0)
sound.duty_u16(32768)
sleep_ms(200)
sound.duty_u16(0)
sound.deinit()
```

GPIO26 / D2 · Passive piezo · 200 ms

Example: `01_one_sound.py`

Instructor note: Verified instructor passive piezo: GPIO26 / D2 and GND. Disconnect the earlier external LED from GPIO26. Use the verified component/circuit; do not substitute a speaker directly. Keep motor power off for examples 01–13. Source: examples/day03/01_one_sound.py.

## 4. Frequency and duty cycle



```python
sound.freq(2000)
sound.duty_u16(32768)
```

Change one parameter at a time. What do you hear?

Example: `02_frequency_and_duty.py`

Instructor note: Frequency changes pitch. Duty cycle changes the waveform; perceived loudness is not linear. 100% duty is a constant HIGH, not a continuous passive-piezo tone. Full example restores output LOW in finally.

## 5. A reusable beep()



```python
def beep(frequency, duration_ms):
    sound.freq(frequency)
    sound.duty_u16(32768)
    sleep_ms(duration_ms)
    sound.duty_u16(0)

for frequency in [1000, 1500, 2000]:
    beep(frequency, 200)
```

Try a melody: optional examples 11–13.

Example: `03_beep_function.py`

Instructor note: Outer try/finally in the full exercise releases PWM on interruption. Optional melodies 11_ode_to_joy.py, 12_twinkle_twinkle.py, 13_robot_sound_signals.py.

## 6. Upload the network files

Copy network_secrets.example.py.
Rename the copy to network_secrets.py.
Fill in your Wi-Fi and assigned MQTT account.

Upload network_secrets.py and the umqtt folder
to the ESP32 root using Thonny’s Files panel.

Keep passwords private. Use your own robot number.

Instructor note: Use existing MicroPython 1.29.0. No new firmware, CA certificate or NTP required. Board layout: /network_secrets.py, /umqtt/__init__.py, /umqtt/simple.py. robot.py additionally required for movement example 14. Never put passwords in slides or public repositories.

## 7. Connect to Wi-Fi



```python
import network
import network_secrets as settings

wlan = network.WLAN()
wlan.active(True)
wlan.connect(settings.WIFI_SSID,
             settings.WIFI_PASSWORD)
```

Run example 04. Check the IP address in Thonny Shell.

Example: `04_connect_wifi.py`

Instructor note: Snippet shows setup only. Supplied full exercise includes a 15-second timeout and prints the assigned IP. Use ordinary SSID/password 2.4 GHz Wi-Fi; enterprise/captive-portal access requires separate preparation.

## 8. MQTT: who sends what?

ESP32 → broker → MQTT Explorer
Sensor readings: the robot publishes.

MQTT Explorer → broker → ESP32
Commands: the robot subscribes.

A topic chooses the channel. A payload carries the message.

Instructor note: The broker is mqtt.ondroid.org. Both clients connect to the broker; the computer does not directly connect to the ESP32 IP. A topic is a named channel. Broker details are instructor/backend supplied.

## 9. Install MQTT Explorer

Windows: choose the installer or portable app.

macOS: choose ARM for Apple Silicon,
or Intel for an Intel Mac.

Linux: choose .deb or AppImage.
For AppImage, enable “Allow executing as program”.



Instructor note: Official download options verified 14 October 2026: https://mqtt-explorer.com/ . Instructor tested Linux 0.4.0-beta.6; Windows/macOS installation not rehearsed. Follow the official site for downloads; AppImage execution permission wording varies by desktop.

## 10. MQTT Explorer connection

Host: mqtt.ondroid.org
Port: 1883     Protocol: mqtt:// (TCP)
Encryption / TLS: off
Username and password: your account card

Advanced → Client ID: your PC client ID

PC: …-robot01-pc     ESP32: …-robot01-esp32

Instructor note: Backend confirmed TCP/1883 on 14 October. No certificate is needed. Credentials and messages are unencrypted. ESP32 and PC IDs must be distinct; for robot01: edu-2026-10-robot01-esp32 and edu-2026-10-robot01-pc. Close other PC clients using the same ID. Settings verified on installed MQTT Explorer.

## 11. See your robot’s messages

Disconnect → Advanced → Subscriptions

Subscribe to:
edu-2026-10/robot01/#

Save and connect again.

Commands + telemetry. Select a topic to inspect its history.

Instructor note: Use your own assigned prefix. Replace default # and $SYS/# with own prefix/#; broker permissions can restrict other robots. Official custom subscription documentation: https://mqtt-explorer.com/ . # is a subscription wildcard, never a publish target. No broker history is implied by MQTT; previously retained values may arrive on subscribe.

## 12. Publish your first hello



```python
topic = settings.TOPIC_PREFIX + "/telemetry/hello"
client.publish(topic.encode(), b"hello",
               retain=False)
```

Subscribe first: this message is not retained.

Example: `05_mqtt_hello.py`

Instructor note: Run the full example after starting MQTT Explorer. The code snippet assumes client and settings are initialized. Instructor physically verified ESP32 publication and separate PC reception over port 1883. No TLS, CA or NTP.

## 13. Send sensor readings



```python
readings = {"left": left.value(),
            "right": right.value()}
payload = json.dumps(readings)
client.publish(topic, payload.encode(), retain=False)
```

Example 06 sends readings every 500 ms.

Example: `06_sensor_telemetry.py`

Instructor note: Full program creates inputs GPIO34 left/A3, GPIO35 right/A2. White 0, black 1, confirmed by instructor. JSON gives names to the values. Run 06 then move paper under each sensor.

## 14. Publish only when it changes



```python
if readings != previous:
    payload = json.dumps(readings)
    client.publish(topic, payload.encode(), retain=False)
    previous = readings
```

Keep the paper still. Move it. Compare the message history.

Example: `07_publish_on_change.py`

Instructor note: Full example sets previous = None before while True. The first reading is sent even if both sensors are zero; compare dictionary values on subsequent loops. Keepalive and MQTT processing remain in the supplied program.

## 15. Control the built-in LED



```python
if message == b"ON":
    led.value(1)
elif message == b"OFF":
    led.value(0)
```

Publish → raw text · QoS 0 · Retain off

Example: `08_mqtt_led.py`

Instructor note: Full example callback checks topic, then bytes ON/OFF. MQTT Explorer: raw text, ON without quotes, QoS 0, Retain off. Publish again with OFF. GPIO2 is the user LED, not the power indicator.

## 16. Request a beep



```python
{"frequency": 2000, "duration_ms": 500}
```

Use the full topic prefix. QoS 0 · Retain off

Example: `09_mqtt_beep.py`

Instructor note: Verified on instructor ESP32: MQTT Explorer sent JSON, ESP32 received it and enabled GPIO26 PWM for the requested duration; instructor heard it. Full callback accepts integer frequency 100..5000 and duration_ms 20..1000. Blocking sound delays other commands until complete.

## 17. Drive forward for one second



```python
if message == b"forward":
    robot.forward(speed=40, seconds=1)
```

Wheels lifted first. Retain off. Publish once, then wait.

Example: `14_mqtt_forward.py`

Instructor note: Optional exercise 14. Upload robot.py. Lift wheels for the first test, then enable motor power. Run full example in Thonny. Only forward is recognized. Host tests passed; MQTT movement has not yet been physically rehearsed.

## 18. What happens while moving?

forward() waits one second, then stops.
The program stays ready for another message.

During that second, the callback is busy.
Repeated clicks can queue more movements.

Immediate physical stop: switch off motor power.

Instructor note: The method robot.forward uses timed local sleep and finally stop. Ctrl+C closes controller. A network stop cannot interrupt this blocking callback; use motor-power switch for immediate physical stop. Network failure alone is not an emergency stop. Never retain movement commands; clear old retained commands before running. Extension: backward elif.

## 19. Optional: combine the system

Read sensors and publish telemetry.
Receive LED commands.
Start a tone and stop it at its deadline.

Use ticks_ms() instead of a long sleep.

Can an LED command work while the tone is playing?

Example: `10_connected_robot.py`

Instructor note: Example 10 combines sensors, LED and nonblocking sound, not motors. Choose it OR movement 14 for the 16:30–16:50 extension. Synchronous check_msg may still block reading partial packets; this is not a hard real-time controller.

## 20. Day 3 checkpoint

Show a sensor message in MQTT Explorer.
Send an LED command back to your ESP32.
If ready: request a beep or a short movement.

Explain topic, payload and client ID.
Save your code; keep credentials private.



Instructor note: Minimum outcome: telemetry plus LED command. Extensions are optional. Stop the program with Ctrl+C and switch motor power off before packing. Save local files; avoid boot.py/main.py auto-run during exercises.
