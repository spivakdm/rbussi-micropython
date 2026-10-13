# Day 3 — Sound, Wi-Fi and MQTT

Use the existing MicroPython 1.29.0 firmware on the Wemos D1 R32. No new firmware and no extra robot wrapper library are required. Pins are declared in each program; MQTT connection functions are supplied inside each network example.

Keep motor power off throughout these exercises. These programs do not call the motor library. Stop a continuous program with Ctrl+C in Thonny; LED and PWM examples release their outputs in `finally`. Run one example at a time with F5; do not save it as `boot.py` or `main.py` during the lesson.

## Exercises

| File | Task | Check |
|---|---|---|
| [01_one_sound.py](01_one_sound.py) | 2000 Hz, 50% fill, 200 ms | One short tone, then silence |
| [02_frequency_and_duty.py](02_frequency_and_duty.py) | Compare frequencies, then 10/25/50% fill | Describe pitch and sound changes |
| [03_beep_function.py](03_beep_function.py) | Local `beep()` function and `for` melody | Three notes |
| [04_connect_wifi.py](04_connect_wifi.py) | Join Wi-Fi, with a 15-second connection timeout | IP address in Thonny Shell |
| [05_mqtt_hello.py](05_mqtt_hello.py) | Publish `hello` over verified TLS | Computer receives `/telemetry/hello` |
| [06_sensor_telemetry.py](06_sensor_telemetry.py) | JSON readings every 500 ms | Computer sees paper changes |
| [07_publish_on_change.py](07_publish_on_change.py) | Remember and compare previous readings | No repeated sensor messages while unchanged |
| [08_mqtt_led.py](08_mqtt_led.py) | Subscribe; explicit `if/elif/else` for ON/OFF | Built-in LED responds |
| [09_mqtt_beep.py](09_mqtt_beep.py) | Parse and validate a JSON command; blocking `beep()` | Short sound; bad commands ignored |
| [10_connected_robot.py](10_connected_robot.py) | Timed telemetry, LED and nonblocking sound together | Telemetry continues during a tone |
| [11_ode_to_joy.py](11_ode_to_joy.py) | Beethoven melody: named notes and durations | Recognizable tune |
| [12_twinkle_twinkle.py](12_twinkle_twinkle.py) | Opening of Twinkle, Twinkle, Little Star | Compare repeated notes and long notes |
| [13_robot_sound_signals.py](13_robot_sound_signals.py) | Startup, success and alert sequences | Reuse one function with different lists and rests |

Core networking target: complete 05, 06 and 08. The combined program and sound commands are extensions. See the [timed teaching sequence](../../docs/day-03-network-plan.md).

## Optional melody exercises

Examples 11–13 need only the verified passive piezo circuit; they do not need Wi-Fi, MQTT, credentials or certificates. They are optional local exercises, not extra required blocks in the Day 3 timetable. Comments inside all course examples explain the steps in English; the upstream dependency files remain unmodified.

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
  ntptime.py              # Supplied upstream time client
  umqtt/
    __init__.py
    simple.py             # Supplied upstream MQTT client
  certs/
    isrg-root-x1.pem       # Public root CA certificate
```

Upload the `umqtt` and `certs` folders with their contents and `ntptime.py` from this directory. If folder upload is unavailable, create those directories in the device pane and upload their files individually. Keep these names and directory structure. `robot.py` may remain on the board; these stationary examples do not need it.

1. Copy [network_secrets.example.py](network_secrets.example.py) to **network_secrets.py** on your computer, in this directory.
2. Fill in the Wi-Fi SSID/password and your assigned MQTT username, password, topic prefix and **both distinct client IDs** from your account card. The robot01 values are examples; replace them if assigned another robot.
3. Upload your filled-in `network_secrets.py` to the board root. Keep the computer copy for the PC client.
4. Run 04, then 05. Start the PC subscriber before 05 because hello is not retained.

Do not share a filled-in configuration or commit it. The public template has placeholders; the kit contains no student passwords. The `umqtt` and `ntptime` modules are pinned upstream dependencies, not a new course robot library; see [sources, hashes and license](SOURCES.md).

## Computer-side receiver and commands

You can use a desktop MQTT client that supports **TLS/TCP**, or the supplied [Python terminal client](../../tools/mqtt_classroom_client.py). Port 8883 is not a browser WebSocket endpoint.

For a desktop client: host `mqtt.ondroid.org`, port `8883`, TLS certificate/hostname verification enabled, your assigned username/password and **PC** client ID. Use the supplied CA if a trust file is required. Subscribe to your `<prefix>/telemetry/#` and optionally `<prefix>/status`. Do not run two PC clients with the same client ID at once.

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

## Do we need a certificate?

**Yes: our examples need the public root CA certificate to verify the MQTT server over TLS on port 8883.** Upload the supplied `certs/isrg-root-x1.pem` to the ESP32, keeping the `certs` directory. This same public file is used by all students. It contains no passwords or private keys and is already included in the student kit; students do not generate or request their own certificate.

The broker sends its server certificate and intermediate chain during the TLS handshake. Our root CA lets the ESP32 check that chain; the client also checks the hostname `mqtt.ondroid.org`. The account then authenticates with its assigned username and password. This setup does not load a client certificate or client private key.

The connection code inside examples 05–10 does this:

```python
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations(cafile=settings.CA_FILE)
```

`CA_FILE` is `"certs/isrg-root-x1.pem"` in the private settings template. `make_client()` supplies this context to the MQTT client, which supplies the hostname to TLS. The board also needs the actual current UTC date/time to check the certificate validity period; that is why the template uses NTP before MQTT. A root CA is different from the broker's short-lived leaf certificate: do not replace the bundled root with a random exported server certificate.

## Clock, TLS and troubleshooting

The template synchronizes the ESP32 clock using NTP before connecting over TLS. It loads the supplied root CA and uses `CERT_REQUIRED`; the supplied MQTT module passes the server hostname for verification. Do not replace these with unchecked TLS. See [MicroPython SSL requirements](https://docs.micropython.org/en/v1.29.0/library/ssl.html).

- **Wi-Fi timeout:** verify 2.4 GHz, SSID/password and access policy. This simple template supports ordinary SSID/password networks, not an enterprise login or captive portal. IP assignment does not prove broker access.
- **NTP failed:** the network may block UDP/123. Use an approved local NTP host, or set the board RTC to current **UTC** from the instructor computer, then set `SYNC_NTP = False` in the private configuration and upload it again. For example, with mpremote installed on the computer: `mpremote connect auto rtc --set` (close Thonny first). Do not hard-code the lesson date: TLS needs the actual current date/time after a power cycle.
- **TLS error:** check the actual UTC clock, CA path, uploaded files, host, firmware and the current broker certificate chain. The included ISRG Root X1 verified the broker from the computer on 13 October 2026; ESP32 support for the actual chain still requires rehearsal. Never use `CERT_NONE` as a workaround.
- **Import error:** check the root directory and `umqtt/simple.py` folder layout. Use the supplied MQTT copy; older copies may not support `ssl=SSLContext`.
- **Login refused:** check activation and your exact credentials. Do not print the password to diagnose it.
- **Repeated disconnects:** check duplicate client IDs and Wi-Fi. Stop the old example before starting another.
- **No message:** start the subscriber first; check prefix, topic direction and broker permissions. QoS 0 is a simple demonstration and does not guarantee delivery.

The examples stop on network errors rather than reconnect automatically. Fix the cause and press F5 again. `check_msg()` polls for messages, but the small synchronous MQTT client may block while reading a partial packet; this is not a hard real-time controller. Exercise 09 also blocks intentionally for each short tone. Exercise 10 removes that application delay with `ticks_ms()`/`ticks_diff()`; it does not make the transport asynchronous.

## Verification status

Host tests cover decisions, malformed commands, timing and interruption cleanup using simulated hardware/network modules. The supplied computer terminal client also received a real telemetry test message on the first account with the included CA; the desktop test publisher used TLS 1.2. No command/status messages were sent during that check. These new examples have **not yet been run on an ESP32**; the board was not visible as a USB serial device during preparation. Rehearse Wi-Fi, NTP, verified ESP32 TLS, command permissions and the piezo circuit on the actual teaching network before class.
