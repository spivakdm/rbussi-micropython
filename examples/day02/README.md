# Day 2 — Sensor and LED Exercises

Complete programs for the instructor and students. Run one at a time in Thonny with MicroPython (ESP32). These are digital D0 examples, not analog ADC examples. See the [teaching plan](../../docs/day-02-plan.md) and [slide outline](../../docs/day-02-slides.md).

## Before running

1. Keep `/robot.py` on the ESP32. No additional library or settings file is needed.
2. Keep motor power off for exercises 01–05 and 07. Check sensor supply and D0 voltage before connecting to ESP32.
3. Open an exercise on your computer and press F5. It declares its own pins and parameters at the top; the exercise need not be saved on the board.
4. Use the sensor trimmers to set a reliable black/white response. Run 01 to check it. The instructor confirmed white = 0 and black = 1; the BLACK constants are defined as 1 directly in the examples. No software calibration is required.
5. Run 06, 08 and 09 with wheels lifted first and the motor battery connected. Copy any wheel-scale correction into the local `LEFT_SCALE`/`RIGHT_SCALE` constants. These movement programs use `while True` with no time limit. Example 06 runs until Ctrl+C; 08/09 also exit when both sensors see black. Ctrl+C requests cleanup through `finally`. Without USB, use the motor-power switch if you need to stop a run.

GPIO assignments initially follow the drawing, left A3/GPIO34 and right A2/GPIO35. Verify the sides physically. An old settings file left on the board is ignored by these examples.

| File | Exercise | Expected result |
|---|---|---|
| `01_read_sensors.py` | Connect and measure D0 | Two numeric columns in Shell for 15 s; optional View > Plotter |
| `02_builtin_led.py` | Digital output | GPIO2 LED blinks five times |
| `03_sensor_builtin_led.py` | Compare a reading with the measured black level | Right sensor on black turns the built-in LED on, for 15 s |
| `04_external_led.py` | Breadboard LED and series resistor | GPIO26/D2 LED blinks five times |
| `05_sensor_external_led.py` | Sensor-driven external output | Right sensor on black turns the external LED on, for 15 s |
| `06_black_forward_white_backward.py` | `if` and continuous motor commands | Right sensor black: forward; white: backward; stop with Ctrl+C |
| `07_two_sensor_states.py` | Four combinations and `if/elif/else` | Prints colour names and intended actions, without movement |
| `08_relay_line_follower.py` | Repeated read–decide–act | Follows a narrow black stripe until both-black or Ctrl+C |
| `09_stop_at_bar.py` | Logical `and` and `break` | Drives straight until both sensors see black or Ctrl+C |

## Stop at the bar

Adjust both sensor trimmers and check black/white readings first. Run `09_stop_at_bar.py` with wheels lifted; move the [printed stop bar](../../printables/README.md) beneath both sensors. Both-black stops and ends the run; a single black sensor does not stop it. If both are already black at launch, no forward command is issued. There is no timer: if the bar is not detected, it keeps driving until interrupted or motor power is switched off. The script does not restart automatically and does not steer. For a floor trial, point it towards the bar from a short distance and check the actual available space.

## Wiring

Sensors: approved supply to VCC, common GND, left D0 to A3, right D0 to A2. A sensor's D0 terminal is not Wemos D0/GPIO3. Output high must be compatible with ESP32 3.3 V GPIO. Module supply is not inferred from terminal labels.

External standard LED: GPIO26/D2 → 470-ohm resistor → anode (+), cathode (-) → GND. Confirm this contact is free on the actual motor shield. Switch all power off to rewire.

## Relay track assumptions

The track is black on white. When centred, both sensor spots see white and the stripe lies between them. Left black causes left steering, right black causes right steering, and both black stops and ends the run. Both white also occurs after losing the stripe completely, so this example cannot guarantee line-loss detection. Test on a short, clear course with wide curves.

Remote-lab exercises use the remote course's supplied code, not these GPIO assignments or `RBussi`.

Status: host logic and cleanup checks only; actual sensor electrical compatibility, trimmer adjustment and robot tracking require physical rehearsal.

## Run without the USB cable

In Thonny, save the selected complete exercise to **MicroPython device** as `/main.py`. Keep `/robot.py` on the board too; Day 2 needs no extra settings module. Reset or power-cycle the ESP32 to start the program automatically. Use `main.py` for the application, not `boot.py`, which is for early startup configuration.

The external supply must power the ESP32 as well as the motor driver. Disconnecting USB does not necessarily reset the board or start a new run. The movement examples have no automatic time limit. Examples 08/09 end on both-black; 06 continues until interrupted. Saving a movement example as main.py makes it run again after each reset. Keep the wheels lifted for the first startup test.

## Optional extra controllers

[Assignment, wiring proposal and prediction tables](../../docs/extra-line-control-tasks.md).

- `10_proportional_five_sensors.py`: five digital sensors; position arithmetic through `for`, then proportional steering with Kp.
- `11_relay_three_sensors.py`: three digital sensors; explicit `if/elif/else` with gentle and strong corrections.

These require additional connected sensors; they cannot be run as physical controllers on the original two-sensor robot. Added GPIOs are a proposed arrangement to verify. The line must be beneath the centre sensor when centred, unlike the earlier two-sensor setup. Both examples have no timer and stop on their specified patterns or Ctrl+C. For students with only two sensors, use the assignment's calculation-only snippet and prediction tables.
