# Day 3 — Sound, Wi-Fi and MQTT

Use the existing MicroPython 1.29.0 firmware on the Wemos D1 R32. No new firmware and no extra robot wrapper library are required. Pins are declared in each program. Each network example starts with the same supplied Wi-Fi setup, followed by the exercise itself.

Keep motor power off throughout these exercises. These programs do not call the motor library. Stop a continuous program with Ctrl+C in Thonny; LED and PWM examples release their outputs in `finally`. Run one example at a time with F5; do not save it as `boot.py` or `main.py` during the lesson.

## Exercises

| File | Task | Check |
|---|---|---|
| [01_one_sound.py](01_one_sound.py) | 2000 Hz, 50% fill, 200 ms | One short tone, then silence |
| [02_frequency_and_duty.py](02_frequency_and_duty.py) | Compare frequencies, then 10/25/50% fill | Describe pitch and sound changes |
| [03_beep_function.py](03_beep_function.py) | Local `beep()` function and `for` melody | Three notes |
| [04_connect_wifi.py](04_connect_wifi.py) | Join Wi-Fi, with a 15-second connection timeout | IP address in Thonny Shell |
| [05_mqtt_hello.py](05_mqtt_hello.py) | Publish `hello` over TCP port 1883 | Computer receives `/telemetry/hello` |
| [06_sensor_telemetry.py](06_sensor_telemetry.py) | JSON readings every 500 ms | Computer sees paper changes |
| [07_publish_on_change.py](07_publish_on_change.py) | Remember and compare previous readings | No repeated sensor messages while unchanged |
| [08_mqtt_led.py](08_mqtt_led.py) | Subscribe; explicit `if/elif/else` for ON/OFF | Built-in LED responds |
| [09_mqtt_beep.py](09_mqtt_beep.py) | Parse and validate a JSON command; blocking `beep()` | Short sound; bad commands ignored |
| [10_connected_robot.py](10_connected_robot.py) | Timed telemetry, LED and nonblocking sound together | Telemetry continues during a tone |
| [11_ode_to_joy.py](11_ode_to_joy.py) | Beethoven melody: named notes and durations | Recognizable tune |
| [12_twinkle_twinkle.py](12_twinkle_twinkle.py) | Opening of Twinkle, Twinkle, Little Star | Compare repeated notes and long notes |
| [13_robot_sound_signals.py](13_robot_sound_signals.py) | Startup, success and alert sequences | Reuse one function with different lists and rests |

Core networking target: complete 05, 06 and 08. Read programs from top to bottom: imports, connection setup, then the task. Functions are used for reusable sounds and MQTT callbacks; callbacks are introduced in 08. The Wi-Fi setup is supplied by the instructor. Students focus first on `publish()`, sensor readings and the LED `if/elif/else`. Exercise 10 adds elapsed-time scheduling and is an advanced extension. The combined program and sound commands are extensions. See the [timed teaching sequence](../../docs/day-03-network-plan.md).

## Optional melody exercises

Examples 11–13 need only the verified passive piezo circuit; they do not need Wi-Fi, MQTT, credentials or certificates. They are optional local exercises, not extra required blocks in the Day 3 timetable. Examples use brief English comments for wiring and less obvious steps; the upstream dependency files remain unmodified.

Each melody is a list of `(frequency, duration_ms)` pairs. Named notes such as `C4 = 262` make the tune easier to edit. The player uses `for` to unpack each pair. A zero frequency represents a rest: the program disables PWM and waits; it does not pass 0 to `PWM.freq()`.

Try changing one note, halving all durations to increase the tempo, or multiplying each nonzero frequency by 2 to raise the melody by an octave. The small silent gap separates repeated notes. These players use blocking delays for clarity; they are not intended to run inside the combined MQTT callback. To add a melody there, advance one note at a time using deadlines, as exercise 10 does for a single tone.

## Wiring

- Left digital D0: A3 / GPIO34; right D0: A2 / GPIO35. White = 0, black = 1. Confirm left/right by covering one sensor at a time. Keep the existing verified sensor wiring.
- Built-in LED: GPIO2, HIGH = on.
- Passive piezo: proposed D2 / GPIO26, common GND, **after the instructor verifies the component and circuit**. GPIO26 was also proposed for the external LED; disconnect that circuit before reusing the pin. An active buzzer does not provide the same pitch experiment. Do not drive a speaker or a higher-current buzzer directly from the GPIO; use a suitable driver circuit if the component requires one.

For PWM, frequency sets repetition rate. `duty_u16(32768)` is approximately 50% fill; `duty_u16(0)` stops the alternating drive. Fill ratio changes the waveform and is not a linear volume setting. Compare one parameter at a time.

## Files to upload with Thonny

Extract the student kit first. In **View → Files**, use the computer pane and **Upload to /** for board files. The final board layout for networking is:

```text
/
  network_secrets.py       # Your own private settings
  umqtt/
    __init__.py
    simple.py             # Supplied upstream MQTT client
```

Upload the `umqtt` folder with its contents from this directory. If folder upload is unavailable, create those directories in the device pane and upload their files individually. Keep these names and directory structure. `robot.py` may remain on the board; these stationary examples do not need it.

1. Copy [network_secrets.example.py](network_secrets.example.py) to **network_secrets.py** on your computer, in this directory.
2. Fill in the Wi-Fi SSID/password and your assigned MQTT username, password, topic prefix and **both distinct client IDs** from your account card. The robot01 values are examples; replace them if assigned another robot.
3. Upload your filled-in `network_secrets.py` to the board root. Keep the computer copy for the PC client.
4. Run 04, then 05. Start the PC subscriber before 05 because hello is not retained.

Do not share a filled-in configuration or commit it. The public template has placeholders; the kit contains no student passwords. The `umqtt` module is a pinned upstream dependency; see [sources, hashes and license](SOURCES.md).

## Computer-side receiver and commands

You can use a desktop MQTT client that supports **MQTT/TCP**, or the supplied [Python terminal client](../../tools/mqtt_classroom_client.py). Port 1883 is not a browser WebSocket endpoint.

For a desktop client: host `mqtt.ondroid.org`, port `1883`, TLS/SSL disabled, your assigned username/password and **PC** client ID. Subscribe to your `<prefix>/telemetry/#` and optionally `<prefix>/status`. Do not run two PC clients with the same client ID at once.

For the Python terminal, use a regular computer terminal with Python 3.9+ (CPython), not the MicroPython Shell. Run from the extracted student-kit root. The commands below use a separate local environment and do not change Thonny's ESP32 interpreter.

Windows PowerShell:

```powershell
py -3 -m venv .mqtt-venv
.mqtt-venv\Scripts\python.exe -m pip install paho-mqtt==2.1.0
.mqtt-venv\Scripts\python.exe tools/mqtt_classroom_client.py --config examples/day03/network_secrets.py
```

Linux/macOS:

```bash
python3 -m venv .mqtt-venv
.mqtt-venv/bin/python -m pip install paho-mqtt==2.1.0
.mqtt-venv/bin/python tools/mqtt_classroom_client.py --config examples/day03/network_secrets.py
```

On Debian/Ubuntu, if venv creation reports that ensurepip is unavailable, install `python3-venv` using the system package manager, then repeat. A separate CPython installation may be needed on Windows/macOS; Thonny's bundled interpreter is not necessarily available as `py` or `python3`. A preinstalled desktop MQTT client is the alternative. Prepare this before class where possible.

The terminal receives messages in the background while accepting commands:

```text
on
off
beep 2000 200
quit
```

All command publishes use QoS 0 and `retain=False`.

Equivalent manual messages for robot01:

| Topic | Payload |
|---|---|
| `edu-2026-10/robot01/cmd/led` | `ON` |
| `edu-2026-10/robot01/cmd/led` | `OFF` |
| `edu-2026-10/robot01/cmd/beep` | `{"frequency":2000,"duration_ms":200}` |

Use your own prefix. Publish to concrete topics; `#` is only for subscriptions. Do not retain commands. Clear any previously retained command on the broker before rehearsal; these simple programs do not inspect the MQTT retained-message flag. The examples do not publish device status yet.

## Connection mode

The backend confirmed **MQTT TCP, port 1883, TLS/SSL disabled** on 14 October 2026. The current examples use this mode. No CA certificate, `ssl`, `ntptime` or clock synchronization is needed. Credentials and messages travel without encryption on this connection.

Username, password, topic prefix and client IDs stay the same. If your older account card or configuration says 8883, change the port to **1883** and disable TLS in the computer client. Existing TLS clients on 8883 can continue working simultaneously; the two ports use the same broker and topics.

`ntptime.py` and `certs/isrg-root-x1.pem` remain in the repository as optional material for the earlier verified-TLS setup. They are not required uploads for this lesson. The earlier version is preserved in Git history.

## Troubleshooting

- **Wi-Fi timeout:** verify 2.4 GHz, SSID/password and access policy. This simple template supports ordinary SSID/password networks, not an enterprise login or captive portal. IP assignment does not prove broker access.
- **Import error:** check the board root and `umqtt/simple.py` folder layout. Use the supplied MQTT copy.
- **Login refused:** check activation and your exact credentials. Do not print the password to diagnose it.
- **Repeated disconnects:** check duplicate client IDs and Wi-Fi. Stop the old example before starting another.
- **No message:** start the subscriber first; check prefix, topic direction and broker permissions. QoS 0 is a simple demonstration and does not guarantee delivery.

The examples stop on network errors rather than retrying or reconnecting automatically. Fix the cause and press F5 again. Sound helpers rely on the program's outer `try/finally` for interruption cleanup; keep their calls inside that block. `check_msg()` polls for messages, but the small synchronous MQTT client may block while reading a partial packet; this is not a hard real-time controller. Exercise 09 also blocks intentionally for each short tone. Exercise 10 removes that application delay with `ticks_ms()`/`ticks_diff()`; it does not make the transport asynchronous.

## Verification status

Host tests cover decisions, malformed commands, timing and interruption cleanup using simulated hardware/network modules. On 14 October, the first account passed authenticated two-client telemetry exchange on TCP/1883 from the instructor computer, without TLS. No command/status messages were published in that check. The physical ESP32 then ran the unmodified `05_mqtt_hello.py` with MicroPython 1.29.0 on the instructor computer's current Wi-Fi. It authenticated and published `hello`; the separate PC client received it. No TLS, CA upload or NTP was used. Other accounts, sensor/sound exercises and command permissions still need rehearsal. See the [recorded test](../../docs/day-03-network-plan.md).
