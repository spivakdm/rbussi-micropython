# RBussi MicroPython Robot

Movement library and student starter kit for a two-wheel robot built around a **Wemos D1 R32**, classic **ESP32**, and **4 MB flash**. Used in *Introduction to Mobile Robotics with a Remote Laboratory*, Metropolia ICT Summer School, 12–16 October 2026.

All code comments and teaching instructions are in English. No Git installation is needed to use the student kit.

## Downloads

- [Student kit v0.19 — download ZIP](https://github.com/spivakdm/rbussi-micropython/raw/refs/heads/main/dist/RBussi-student-kit-v0.19.zip): library, firmware, examples, wiring reference, and instructions.
- [robot.py — download library](https://github.com/spivakdm/rbussi-micropython/raw/refs/heads/main/robot.py)
- [MicroPython 1.29.0 — download firmware](https://github.com/spivakdm/rbussi-micropython/raw/refs/heads/main/firmware/ESP32_GENERIC-20260824-v1.29.0.bin)

The firmware is an unmodified upstream **ESP32_GENERIC** image. It is for the classic ESP32, not ESP8266, ESP32-C3, or ESP32-S3. Firmware installation and the library upload are separate steps: the `.bin` does not contain `robot.py`.

## Start with Thonny

1. Install [Thonny](https://thonny.org/) for your operating system and extract the student ZIP.
2. Connect USB with motor power off. Select **MicroPython (ESP32)** and the robot's USB serial port.
3. Follow the [firmware and library guide](docs/firmware-and-library.md) to install the supplied image, or verify an instructor-prepared board. The classic ESP32 full image uses address **0x1000**. Erasing flash deletes existing board files.
4. Upload `robot.py` to the root of the MicroPython device using **View → Files**.
5. Open `examples/00_check_setup.py` on the computer and press **F5**. It requests no movement.
6. Lift the wheels, connect the motor battery, and run `examples/first_drive.py`. Keep the motor-power switch accessible.

See the [Windows, macOS, and Linux setup guide](docs/student-setup.md). The student installation routes still require a full instructor rehearsal on each OS.

## First movement

```python
from robot import RBussi

robot = RBussi()
try:
    robot.forward(speed=50, seconds=0.5)
finally:
    robot.close()
```

Save personal programs under a new filename on the computer. `robot.py` is reserved for the library. Do not save a Day 1 movement program as `main.py`, which would run at boot.

See the [full library guide and examples](docs/library.md) for constructor options, method parameters, calibration, and stopping behavior.

## Movement API

| Method | Behavior |
|---|---|
| `forward(speed=50, seconds=1)` | Forward, then stop |
| `backward(speed=50, seconds=1)` | Backward, then stop |
| `left(speed=50, seconds=0.3)` | Turn left on the spot, then stop |
| `right(speed=50, seconds=0.3)` | Turn right on the spot, then stop |
| `move(left=40, right=60, seconds=1)` | Independent timed wheel commands |
| `motors(left=40, right=60)` | Continuous commands until changed or stopped |
| `stop()` | Stop both motors |
| `close()` | Stop and release PWM resources; call at the end |

Directional speed accepts 0–100. Independent wheel commands accept −100 to 100, with positive values meaning forward. Duration accepts 0–60 seconds; zero duration never starts the motors. Speed is PWM duty rather than measured velocity: this robot has no wheel encoders. Timed turns do not specify exact angles.

Keep one active `RBussi` object. Use `try/finally` with `robot.close()`, especially for continuous commands. Timed movement also stops in `finally`, including on interruption. Before reversing a moving wheel, the library stops both motors for 20 ms. Software stopping depends on a functioning board and program; keep physical motor power accessible.

## Wheel balance

```python
from robot import RBussi

robot = RBussi(left_scale=0.95, right_scale=1.0)
try:
    robot.move(left=50, right=50, seconds=0.5)
finally:
    robot.close()
```

Both scales default to 1.0 and accept 0–1. Reduce the faster wheel's scale, using repeated trials on the same surface. The value 0.95 above is only an example. Corrections affect all movement methods and do not provide measured-speed feedback. Wiring differences can be handled separately with `left_reversed=True` or `right_reversed=True`.

See the [wheel-calibration guide](docs/wheel-calibration.md) and `examples/03_wheel_balance.py`.

## Hardware mapping

| Function | Board label | ESP32 GPIO |
|---|---|---|
| Right motor A: PWM / direction / brake | D3 / D12 / D9 | 25 / 19 / 13 |
| Left motor B: PWM / direction / brake | D11 / D13 / D8 | 23 / 18 / 12 |
| Line sensor A2 | A2 | 35 |
| Line sensor A3 | A3 | 34 |

See the [wiring reference](docs/wiring-reference.md). The supplied diagram labels sensor power as +5 V; verify the actual sensor DO voltage before connecting it to the ESP32. Do not apply a 5 V signal to an ESP32 GPIO.

Motor A's right-side identity and default forward movement were physically confirmed on the preparation robot. Reverse, turns, and the new wheel-scale correction still require physical verification. Sensor sides are taken from the drawing, not a physical calibration; reliable black/white response remains to be established.

Board mapping reference: [RIOT Wemos D1 R32 definitions](https://api.riot-os.org/esp32-wemos-d1-r32_2include_2arduino__iomap_8h.html). Motor control was adapted from the instructor's earlier mBlock motor library.

## Guides and examples

- [Student setup](docs/student-setup.md)
- [Firmware installation and library upload](docs/firmware-and-library.md)
- [Movement quick reference](docs/quick-reference.md)
- [Full library guide and examples](docs/library.md)
- [Wheel calibration](docs/wheel-calibration.md)
- [Wiring reference](docs/wiring-reference.md)
- [Observation worksheet](worksheets/day01-observations.md)
- [Examples](examples)

Simulator and remote-laboratory activities use their own libraries and APIs. Obtain Moodle and simulator access instructions from the instructor.

## Checks and rebuilding the kit

Host checks use simulated GPIO/PWM and do not move a real robot:

```bash
python3 -m unittest discover -s tests -v
python3 tools/build_student_kit.py
```

The checks cover motor stopping and wheel scaling, line-control decisions, MQTT command validation, telemetry timing, TCP connection settings and interruption cleanup using simulated hardware/network modules. Rebuilding the kit verifies the approved firmware hash and generates checksums for the included files.

## Firmware provenance

See [firmware source and version](firmware/SOURCE.md) and the [upstream MicroPython license notice](firmware/MicroPython-LICENSE.txt). Those notices apply to the upstream firmware and its dependencies; they do not assign a license to the other course materials.

## Day 2: Sensors and LEDs

[Lesson plan](docs/day-02-plan.md), [presentation outline](docs/day-02-slides.md), [core exercises and optional controllers](examples/day02/README.md), and [worksheet](worksheets/day02-observations.md). Only `robot.py` is needed on the board. Each exercise declares its own pins and parameters. Adjust the sensor trimmers and check the digital readings before sensor-driven exercises; no extra settings module or software calibration is required. The relay example assumes a narrow black line between two sensors on white. Physical sensor validation is still pending.

## Printable practice sheet

[A4 sensor and line template](printables/day02-line-templates.pdf): print one selected page per student at 100%. Stripe widths: 10, 6 and 14 mm. Includes calibration patches and a stop bar. See [printing instructions](printables/README.md) and [additional sensor exercises](docs/day-02-extra-exercises.md). The printable and the stop-at-bar example are included in student kit v0.19.

## Optional controllers with more sensors

[Two extra assignments](docs/extra-line-control-tasks.md): five-sensor proportional control with an explicit `for` loop, and three-sensor relay control with an eight-state table. Includes complete examples 10/11 and proposed additional wiring. Physical runs require the extra sensors; students with the original two-sensor kit can use the calculation-only snippet and prediction tables.

## Day 3: Sound, Wi-Fi and MQTT

[Sound, Wi-Fi and MQTT lesson draft](docs/day-03-network-plan.md), based on the supplied class broker and per-robot topic namespaces. The first account passed a two-client telemetry round trip over TCP/1883 from the instructor computer. The backend confirmed this mode with TLS disabled on 14 October; the updated examples need no certificate or NTP. A physical ESP32 with MicroPython 1.29.0 also ran exercise 05 successfully: its hello message reached the computer through port 1883 on the tested Wi-Fi. Other accounts, classroom-network coverage and command-topic permissions remain to be checked. Account passwords are not included in the repository or student bundle.

[Ten progressive examples, three optional sound programs and upload instructions](examples/day03/README.md): passive piezo PWM, Wi-Fi, MQTT hello, sensor JSON, change-only publishing, LED/sound commands and a combined application. Includes a private settings template, a pinned upstream MQTT module and an optional computer terminal client. Examples have passed host checks and exercise 05 passed on the physical ESP32. Remaining sensor, LED, piezo and classroom-network rehearsal is still required.

## ROS 2 introduction

[ROS + MQTT setup and exercises](ros2/README.md): browser-based Turtlesim with RBussi artwork, prepared MicroPython robot application, ROS 2 container, and a bridge to the existing broker. [Download the ROS classroom kit and container images](https://github.com/spivakdm/rbussi-micropython/releases/tag/ros-kit-v0.2.1).
