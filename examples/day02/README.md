# Day 2 — Sensor and LED Exercises

Complete programs for the instructor and students. Run one at a time in Thonny with MicroPython (ESP32). These are digital D0 examples, not analog ADC examples. See the [teaching plan](../../docs/day-02-plan.md) and [slide outline](../../docs/day-02-slides.md).

## Before running

1. Keep `/robot.py` on the ESP32. Upload `day02_settings.py` to the device root as `/day02_settings.py`.
2. Keep motor power off for exercises 01–05 and 07. Check sensor supply and D0 voltage before connecting to ESP32.
3. Open an exercise on your computer and press F5. The exercise itself need not be saved on the board.
4. Calibrate with 01, fill the four WHITE/BLACK levels in settings, upload settings again, and stop/restart the backend before exercises using calibration.
5. Run 06 and 08 with wheels lifted first and the motor battery connected. Preserve per-robot wheel scales. The default movement limit is five seconds; Ctrl+C requests software cleanup.

The `None` calibration defaults are deliberate: sensor-driven examples reject them instead of silently guessing polarity. GPIO assignments initially follow the supplied drawing, left A3/GPIO34 and right A2/GPIO35. Verify the sides physically.

| File | Exercise | Expected result |
|---|---|---|
| `01_read_sensors.py` | Connect and measure D0 | Two numeric columns in Shell for 15 s; optional View > Plotter |
| `02_builtin_led.py` | Digital output | GPIO2 LED blinks five times |
| `03_sensor_builtin_led.py` | Compare a reading with the measured black level | Right sensor on black turns the built-in LED on, for 15 s |
| `04_external_led.py` | Breadboard LED and series resistor | GPIO26/D2 LED blinks five times |
| `05_sensor_external_led.py` | Sensor-driven external output | Right sensor on black turns the external LED on, for 15 s |
| `06_black_forward_white_backward.py` | `if` and continuous motor commands | Right sensor black: forward; white: backward, for at most 5 s |
| `07_two_sensor_states.py` | Four combinations and `if/elif/else` | Prints colour names and intended actions, without movement |
| `08_relay_line_follower.py` | Repeated read–decide–act | Follows a narrow black stripe between the sensors; bounded 5 s trial |

## Wiring

Sensors: approved supply to VCC, common GND, left D0 to A3, right D0 to A2. A sensor's D0 terminal is not Wemos D0/GPIO3. Output high must be compatible with ESP32 3.3 V GPIO. Module supply is not inferred from terminal labels.

External standard LED: GPIO26/D2 → 470-ohm resistor → anode (+), cathode (-) → GND. Confirm this contact is free on the actual motor shield. Switch all power off to rewire.

## Relay track assumptions

The track is black on white. When centred, both sensor spots see white and the stripe lies between them. Left black causes left steering, right black causes right steering, and both black stops and ends the run. Both white also occurs after losing the stripe completely, so this example cannot guarantee line-loss detection. Test on a short, clear course with wide curves.

Remote-lab exercises use the remote course's supplied code, not these GPIO assignments or `RBussi`.

Status: host logic and cleanup checks only; actual sensor electrical compatibility, calibration and robot tracking require physical rehearsal.
