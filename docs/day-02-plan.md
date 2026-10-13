# Day 2 — From Sensor Readings to Robot Decisions

Metropolia ICT Summer School · Introduction to Mobile Robotics with a Remote Laboratory (3 ECTS) · TX00GZ66-3001.

Tuesday 13 October 2026, 13:00–17:00 · MMC245.

This revision moves the original Day 3 sensor introduction to Day 2 because basic movement, GPIO/PWM and wheel correction have already been covered. The working track is a narrow black line on a white surface, between the two sensors when centred.

Status: teaching draft with runnable examples, not yet physically validated with the line sensors. Sensor labels supplied by the instructor: VCC, GND, D0. Exact module model and supply/output voltage still need checking. All sample-code comments and teaching materials are in English.

## Outcomes

Students can connect a digital line sensor, print its readings, record black/white polarity, drive an LED, use a sensor in an `if` statement, and explain a simple feedback controller. The relay follower is a stretch outcome if wiring or sensor checks take longer.

## Schedule

| Time | Activity | Example / evidence |
|---|---|---|
| 13:00–13:10 | Recap: a command versus a decision based on measurement | Explain today's read–decide–act loop |
| 13:10–13:35 | Sensor connections, voltage check, A2/A3 and GPIO mapping | Identify VCC, GND, D0 and both sensor sides |
| 13:35–14:00 | Read, display and adjust both sensor trimmers | `01_read_sensors.py`, Shell, optional Plotter, sensor check table |
| 14:00–14:15 | Built-in LED, then sensor-driven indication | `02_builtin_led.py`, `03_sensor_builtin_led.py` |
| 14:15–14:30 | Break | |
| 14:30–14:55 | Breadboard LED, resistor and sensor-driven indication | `04_external_led.py`, `05_sensor_external_led.py` |
| 14:55–15:20 | Black/white movement, then stop at a broad bar | `06_black_forward_white_backward.py`, `09_stop_at_bar.py`, wheels lifted first |
| 15:20–15:35 | Break | |
| 15:35–16:15 | Two-sensor state table and optional relay follower | `07_two_sensor_states.py`, `08_relay_line_follower.py` |
| 16:15–16:50 | Simulator/remote-lab rotation | Tasks 10 and 11, task 12 or 14 if ready |
| 16:50–17:00 | Checkpoint and save work | Code, sensor checks, one limitation |

Explain each new Python construct immediately before using it: `Pin.IN`, `value()`, `print`, comparisons, `if/elif/else`, `for`/`while`, `break`, and `try/finally`. Introduce only the constructs needed for the current experiment.

## Printable material

Use the [A4 sensor and line template](../printables/README.md): one selected page per student, printed at 100%. Choose a stripe narrower than the clear gap between sensing spots. The sheet supports sensor checks, bench steering and a stop-marker experiment; a full five-second floor trial needs more room. Optional activities: [additional sensor exercises](day-02-extra-exercises.md).

## Hardware preparation

- Existing robot, charged motor battery, USB data cable and wheel stand.
- Two sensor modules with VCC/GND/D0, plus contrasting paper/tape.
- Breadboard, jumper wires, a standard indicator LED and a 470-ohm series resistor.
- Multimeter for checking supply and D0 high voltage.
- A short track with wide curves and a black stripe narrow enough to fit between the sensor spots. Check actual spacing and stripe width before class.

### Sensor connections

| Sensor terminal | Connection |
|---|---|
| VCC | A supply approved for the actual module; confirm before wiring |
| GND | Robot/ESP32 GND |
| Left D0 | A3, GPIO34, based on the drawing; verify the side physically |
| Right D0 | A2, GPIO35, based on the drawing; verify the side physically |

`D0` on a sensor means its digital output. It does not mean Wemos D0 or GPIO0. A2/A3 identify the board header positions. Reading this D0 connection with `Pin(..., Pin.IN).value()` gives 0 or 1, even though the ESP32 pins also support ADC.

The earlier drawing labels VCC as 5 V. This is not proof that D0 is safe for ESP32. With USB and battery off, check the wiring; identify the module, then establish that its output high voltage is compatible with 3.3 V GPIO. Use a compatible supply or suitable level conversion as required by its actual circuit. Do not prescribe 3.3 V module power without checking module support. GPIO34/35 are input-only and have no internal pull resistors. A module that needs an output pull-up must provide one externally to an appropriate voltage; do not assume `Pin.PULL_UP` works here.

### External LED

Use GPIO26, the Wemos D2 header position, only after confirming it is exposed and unused on the actual shield.

```text
GPIO26 / D2 --- 470 ohm resistor --- LED anode (+)
                                      LED cathode (-) --- GND
```

The longer lead normally identifies the anode of a new LED. The package flat normally identifies the cathode. Check the actual LED if leads have been cut. The resistor may be on either side of the LED, provided it is in series. Do not connect an LED directly between GPIO and GND.

The built-in programmable LED uses GPIO2. The always-on power indicator is a separate LED. Sensor A0 and the built-in LED share GPIO2 on this board, so keep these experiments on the existing A2/A3 sensor connections.

## Files and Thonny workflow

The examples are in [examples/day02](../examples/day02/README.md).

1. Keep the existing `/robot.py` on the board. No additional library or settings file is needed for Day 2.
2. Open an exercise from your computer and run it with F5 using MicroPython (ESP32).
3. Each exercise declares its own GPIO pins and parameters at the top. Edit those constants in that exercise if the wiring or wheel balance differs.
4. Sensor thresholds are adjusted using the module trimmers. The instructor confirmed white = 0 and black = 1. Each sensor-driven exercise declares its BLACK constants as 1. No software threshold calibration is needed.

`print()` reaches Thonny's Shell through the USB serial connection. No separate serial-monitor application is needed. `01_read_sensors.py` prints two numeric columns, also suitable for View > Plotter. Plotter displays digital steps, not a continuous measurement of reflectance. Copy observations from Shell into the worksheet; file logging on the ESP32 is unnecessary for this lesson. An alternative serial terminal would use the same REPL port, normally at 115200 baud, and must not compete with Thonny for it.

## Exercise sequence and instructor notes

### 1. Read and adjust the sensor trimmers

Keep motor power off. Run `01_read_sensors.py`: it prints left and right levels every 250 ms for 15 seconds. Test white/white, black/white, white/black, black/black at the normal sensing height. Cover only one sensor to check the side mapping. Swap the local `LEFT_GPIO`/`RIGHT_GPIO` constants if the actual wiring differs.

Use each sensor's trimmer to obtain a stable change between the white and black areas. There is no software threshold or calibration routine. A previous white/white reading was 0/0; check the black response too. The instructor confirmed white = 0 and black = 1; the examples use `LEFT_BLACK = 1` and `RIGHT_BLACK = 1`. If readings do not change, investigate height, the trimmer setting, contrast, supply and wiring.

### 2. Built-in LED

Run `02_builtin_led.py`: five half-second flashes. Then run `03_sensor_builtin_led.py`: right sensor on black turns the LED on; white turns it off. Both sensor-driven LED examples use explicit `if/else`: `led.value(1)` on black and `led.value(0)` on white. Ask students to predict the effect of changing `==` to `!=`. Motor power stays off.

### 3. External LED

Switch all power off to wire the breadboard. Run `04_external_led.py` before adding sensor logic, then `05_sensor_external_led.py`. Ask students to explain polarity, the resistor, common ground and output versus input pins. Both sensor-driven LED tests last 15 seconds.

### 4. Reactive movement

Run `06_black_forward_white_backward.py` with wheels lifted and motor battery connected. Move paper beneath the right sensor. Black commands both wheels forward; white commands both backward. The test lasts five seconds by default. It demonstrates a conditional response, not line following. Default duty is 50%; increase only if needed to start the actual motors. Use the existing per-robot scale values at the top of the example.

If readings flicker near an edge, first investigate height, threshold, lighting and wiring. As an optional exercise, require three consecutive matching samples before reversing. Do not hide unstable sensing by increasing motor power.

### 5. Stop at a transverse bar

Use `09_stop_at_bar.py`: the robot drives straight until `left_black and right_black`, then stops and exits. Allocate approximately the final 10 minutes of the reactive-movement block. Use the printed broad bar and test with wheels lifted first. One black sensor alone does not stop this program; both-black at launch prevents a forward command. The local `MAX_RUN_MS = 1000` limits the trial to at most one second. No automatic restart or line steering is included. A single A4 sheet requires a short starting distance and an appropriate speed; a timeout is not a distance measurement.

Ask students to predict what replacing `and` with `or` would change. Compare the marker rule with the remote stop-at-line task.

### 6. Two sensors and a relay controller

Run `07_two_sensor_states.py` with motor power off. It prints the intended action without moving. Test all four states, then test the same cases with wheels lifted using `08_relay_line_follower.py`.

| Left surface | Right surface | Command | Wheel PWM before scaling |
|---|---|---|---|
| White | White | Forward | `SPEED`, `SPEED` |
| Black | White | Correct left | `INNER_SPEED`, `SPEED` |
| White | Black | Correct right | `SPEED`, `INNER_SPEED` |
| Black | Black | Stop and end this run | 0, 0 |

Defaults: `SPEED = 50`, `INNER_SPEED = 0`, `SAMPLE_MS = 20`, `RUN_MS = 5000`. Braking the inner wheel gives a strong initial correction without reversing it. Once this works, increase `INNER_SPEED` to explore gentler steering and compare runs. Preserve experimentally chosen `LEFT_SCALE` and `RIGHT_SCALE`.

Start with the robot centred over the stripe: both sensor spots see white, with black between them. A short floor test needs clear space and USB cable slack. The example closes the controller after the time limit, both-black, an error, or Ctrl+C. This is software cleanup, not an independent hardware stop.

**Ambiguity:** white/white also occurs when the robot has left the stripe completely. Two binary readings cannot distinguish those cases. Both-black could be a marker, crossing or unsuitable stripe width; this lesson deliberately stops. Do not claim reliable line-loss detection. A track/layout change, additional sensing or a more informative sensor signal is needed to resolve ambiguity. The five-second limit bounds the teaching trial but does not detect loss.

## Simulator and remote laboratory

Use the remote platform's own documented API and Octoliner; local `RBussi`, pin numbers and settings are not portable to it.

- Task 10, Introduction to Octoliner Sensor: read a central channel and compare its numeric range with local D0 values.
- Task 11, Conditional Logic & Reactive Behavior: stop at a detected line. Explain why the behavior differs from the local forward/backward demonstration.
- Task 12, Processing Sensor Data: optional scanning/threshold exercise if tasks 10–11 are complete.
- Task 14, Visual Telemetry: optional LED extension if prerequisites permit access. Otherwise defer to Day 3.
- Task 13, eight-channel spatial logic, and tasks 15–16, remote line following, remain Day 3 work unless students finish early and unlock rules allow it.

Simulate a supported task while waiting for physical access. Start with a 5-minute demonstration, then approximately 25 minutes of individual/rotating work and 5 minutes to compare measurements. Actual URLs, API names and remote examples have not been supplied, so no remote executable code is invented here. Use course-provided templates.

If time runs short, prioritize reliable sensor readings, one sensor-driven LED, and conditional movement. Demonstrate the relay follower and continue it on Day 3. Preserve the remote-lab block; its unused individual tasks can continue on Day 3 according to capacity.

## Checkpoint

Students save their side mapping, LED wiring, local constants and one working program. Ask: what is measured, how is it interpreted, and what command follows? Each student explains why two white readings do not prove that the line is still between the sensors.

## Sources and verification

- [MicroPython ESP32 GPIO and PWM reference](https://docs.micropython.org/en/latest/esp32/quickref.html#pins-and-gpio).
- [Espressif hardware and GPIO voltage guidance](https://docs.espressif.com/projects/esp-faq/en/latest/hardware-related/hardware-design.html).
- [Wemos D1 R32 board mappings](https://github.com/UCLM-ESI/wemos-d1-r32-pio/blob/master/pins_arduino.h).
- Thonny Plotter workflow checked against installed Thonny 5.0.0 help.
- Remote activity scope comes from the instructor-supplied task list.

Host checks exercise sensor decisions and cleanup with simulated hardware. They do not verify the module supply, D0 high voltage, sensor checks, LED polarity on a particular board revision, or physical line-following performance. Rehearse these with the actual kit before delivery.
